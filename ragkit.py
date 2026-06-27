"""RAG over your documents — retrieve relevant passages and answer with citations.

The reusable core behind enterprise AI agents and source-cited chatbots. Runs
fully offline: a stdlib TF-IDF index for retrieval and a deterministic local LLM
stub for generation, so demos are reproducible with no keys and no network.

Plug in a real model later by setting LLM_PROVIDER + keys (see `complete`) — the
adapters are wired but never exercised in the default path.
"""

from __future__ import annotations

import glob
import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass
class Chunk:
    doc: str          # document name
    idx: int          # chunk index within the document
    text: str
    tokens: list[str] = field(default_factory=list)


def load_docs(folder: str) -> list[tuple[str, str]]:
    """Return (doc_name, text) for every .md/.txt file in folder."""
    docs = []
    for path in sorted(glob.glob(os.path.join(folder, "*"))):
        if path.lower().endswith((".md", ".txt")):
            with open(path, "r", encoding="utf-8") as fh:
                docs.append((os.path.basename(path), fh.read()))
    return docs


def chunk_text(doc: str, text: str, max_chars: int = 600) -> list[Chunk]:
    """Split a document into paragraph-ish chunks under max_chars."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        if buf and len(buf) + len(p) + 2 > max_chars:
            chunks.append(buf)
            buf = p
        else:
            buf = f"{buf}\n\n{p}" if buf else p
    if buf:
        chunks.append(buf)
    return [Chunk(doc, i, c, tokenize(c)) for i, c in enumerate(chunks)]


class TfidfIndex:
    """Minimal TF-IDF retriever (pure stdlib)."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        n = len(chunks) or 1
        df: Counter[str] = Counter()
        for ch in chunks:
            df.update(set(ch.tokens))
        self.idf = {t: math.log((n + 1) / (c + 1)) + 1 for t, c in df.items()}
        self.vectors = [self._vec(ch.tokens) for ch in chunks]
        self.norms = [math.sqrt(sum(v * v for v in vec.values())) or 1.0
                      for vec in self.vectors]

    def _vec(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        return {t: tf[t] * self.idf.get(t, 0.0) for t in tf}

    def query(self, q: str, k: int = 3) -> list[tuple[Chunk, float]]:
        qv = self._vec(tokenize(q))
        qn = math.sqrt(sum(v * v for v in qv.values())) or 1.0
        scored = []
        for ch, vec, norm in zip(self.chunks, self.vectors, self.norms):
            dot = sum(qv.get(t, 0.0) * w for t, w in vec.items())
            scored.append((ch, dot / (qn * norm)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s in scored[:k] if s[1] > 0]


def build_index(folder: str) -> TfidfIndex:
    chunks: list[Chunk] = []
    for doc, text in load_docs(folder):
        chunks.extend(chunk_text(doc, text))
    return TfidfIndex(chunks)


# --- Generation (pluggable) ---------------------------------------------------

def _best_sentences(query: str, text: str, n: int = 2) -> str:
    """Pick the sentences from a chunk most relevant to the query (stdlib)."""
    q = set(tokenize(query))
    sents = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    ranked = sorted(
        sents, key=lambda s: len(q & set(tokenize(s))), reverse=True
    )
    top = [s.strip() for s in ranked[:n] if s.strip()]
    return " ".join(top) if top else text[:200]


def complete(query: str, hits: list[tuple[Chunk, float]]) -> str:
    """Generate a grounded, cited answer.

    Default provider is a deterministic local stub. Set LLM_PROVIDER=azure or
    =anthropic (with the matching key env vars) to route to a real model — those
    adapters are defined but intentionally not called in the default path.
    """
    provider = os.environ.get("LLM_PROVIDER", "local").lower()
    if provider == "azure":   # pragma: no cover - requires real endpoint
        return _azure_complete(query, hits)
    if provider == "anthropic":  # pragma: no cover - requires real key
        return _anthropic_complete(query, hits)
    return _local_stub(query, hits)


def _local_stub(query: str, hits: list[tuple[Chunk, float]]) -> str:
    if not hits:
        return ("I couldn't find anything relevant in the documents. "
                "Try rephrasing, or add the source document.")
    parts = []
    for i, (ch, _score) in enumerate(hits, 1):
        parts.append(f"{_best_sentences(query, ch.text)} [{i}]")
    body = " ".join(parts)
    sources = "\n".join(
        f"  [{i}] {ch.doc} (chunk {ch.idx})" for i, (ch, _s) in enumerate(hits, 1)
    )
    return f"{body}\n\nSources:\n{sources}"


def _build_prompt(query: str, hits: list[tuple[Chunk, float]]) -> str:
    ctx = "\n\n".join(
        f"[{i}] ({ch.doc}) {ch.text}" for i, (ch, _s) in enumerate(hits, 1)
    )
    return (
        "Answer the question using ONLY the context. Cite sources as [n]. "
        "If the answer isn't in the context, say so.\n\n"
        f"Context:\n{ctx}\n\nQuestion: {query}\nAnswer:"
    )


def _azure_complete(query, hits):  # pragma: no cover
    """Azure OpenAI adapter (wired, not used by default). Uses stdlib urllib."""
    import json
    import urllib.request
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    key = os.environ["AZURE_OPENAI_API_KEY"]
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    url = (f"{endpoint}/openai/deployments/{deployment}/chat/completions"
           "?api-version=2024-06-01")
    body = json.dumps({"messages": [
        {"role": "user", "content": _build_prompt(query, hits)}]}).encode()
    req = urllib.request.Request(
        url, body, {"api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def _anthropic_complete(query, hits):  # pragma: no cover
    """Anthropic (Claude) adapter (wired, not used by default)."""
    import json
    import urllib.request
    key = os.environ["ANTHROPIC_API_KEY"]
    body = json.dumps({
        "model": os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8"),
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": _build_prompt(query, hits)}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", body,
        {"x-api-key": key, "anthropic-version": "2023-06-01",
         "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["content"][0]["text"]


def answer(query: str, index: TfidfIndex, k: int = 3) -> str:
    return complete(query, index.query(query, k))
