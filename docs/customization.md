# Customization

Six things you'll typically tune per deployment. Each is a small, localized
change in [ragkit.py](../ragkit.py) (or the data folder).

## 1. Swap the document corpus

Drop your `.md` or `.txt` files into [data/](../data/). The index is rebuilt on
`build_index(...)` — no separate build step or vector store.

```python
index = build_index("path/to/your/docs")
```

For larger corpora, `chunk_text` keeps chunks under 600 characters, which is a
reasonable starting point for sentence-level cosine retrieval. Tune it (next
section) if your documents are unusually long or short.

## 2. Chunk size

```python
chunks = chunk_text(doc_name, text, max_chars=400)  # tighter chunks
```

Smaller chunks → more precise citations but more index entries. Larger chunks →
more context per hit but less precise location. Start with the default 600,
re-run the eval set, and adjust if precision drops.

## 3. top-k and re-ranking weight

```python
answer(query, index, k=5)             # request more sources
```

For the re-rank weight, edit `RERANK_WEIGHT` (default `0.35`) in
[ragkit.py](../ragkit.py):

- **Lower (e.g. 0.10)** → re-rank is barely advisory; TF-IDF order dominates.
  Use when your queries are short and high-signal.
- **Higher (e.g. 0.60)** → sentence-overlap dominates; better when queries have
  context phrases that should match a specific sentence rather than scattered
  tokens.

Re-run [evals/run.py](../evals/run.py) after every change.

## 4. Plug a real LLM (Azure OpenAI or Anthropic)

The adapters are already wired in [ragkit.py](../ragkit.py); the default path
just uses the deterministic local stub so the kit runs without keys. Set the
provider via env var:

```bash
export LLM_PROVIDER=azure
export AZURE_OPENAI_ENDPOINT="https://<your>.openai.azure.com"
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_DEPLOYMENT="gpt-4o"     # or your deployment name
python run.py
```

```bash
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY="..."
export ANTHROPIC_MODEL="claude-opus-4-7"    # or another available model
python run.py
```

The prompt template used by both adapters is `_build_prompt(query, hits)` —
plain text with `Context:` and `Question:` blocks. Mirror this template in your
production prompt store so simulator behaviour matches production.

## 5. Add a new document type / preprocessing

`load_docs` only ingests `.md` and `.txt`. To handle PDF, HTML, or DOCX you'd
extract plain text first and either (a) write the text to a `.txt` next to the
source, or (b) widen `load_docs` to dispatch by extension to your text
extractor. The downstream `chunk_text` and `TfidfIndex` don't care where the
text came from — they only see the string.

## 6. Tune the eval set

The eval set in [evals/golden.json](../evals/golden.json) is the regression net.
After any change to chunking, re-rank weight, or model, run:

```bash
python evals/run.py
```

When you find a real-world query the kit gets wrong, add it to the golden set
**before** changing parameters — that way you can confirm both the fix lands
and the existing cases don't regress.

## Validating any change

After any of the above:

```bash
python -m pytest -q       # 9 unit tests
python evals/run.py       # CI-gating golden set
python run.py             # smoke-test the end-to-end path
```

All three should be green before shipping.
