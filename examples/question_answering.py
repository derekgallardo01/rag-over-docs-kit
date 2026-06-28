"""End-to-end Q&A pipeline: ingest a doc set, index, query, answer with citations.

The standard RAG application workflow:

  1. Load a corpus from a folder of .md files
  2. Build a TF-IDF index over chunks (with the re-ranker enabled)
  3. Run a battery of representative questions
  4. For each: return the answer + the source chunks that backed it
  5. Optionally: run the eval suite to verify retrieval quality

Demonstrates the complete RAG loop end-to-end against two distinct
corpora (workplace policies + technical API docs).

Usage:
    python examples/question_answering.py
    python examples/question_answering.py --corpus data-tech
    python examples/question_answering.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ragkit import answer, build_index, complete, rerank  # noqa: E402


# Representative question sets per corpus
QUESTIONS = {
    "data": [
        "What's the policy on remote work for employees?",
        "How do I request a refund for a customer?",
        "What's our incident response procedure for a security breach?",
        "Can engineers access production data?",
        "How long do we keep customer support transcripts?",
    ],
    "data-tech": [
        "How do I authenticate API requests?",
        "What's the rate limit for the search endpoint?",
        "How do I subscribe to a webhook for a specific event type?",
        "What headers should I include in every API call?",
        "How do I retry a failed webhook delivery?",
    ],
}


def run_qa(corpus_dir: str, as_json: bool = False, k: int = 3) -> int:
    index = build_index(corpus_dir)

    # Pick the right question set based on the corpus
    questions = QUESTIONS.get(corpus_dir, QUESTIONS["data"])

    results = []
    for q in questions:
        # Use the lower-level pipeline so we can capture the citation chunks
        candidates = index.query(q, k=max(k * 2, k + 3))
        top = rerank(q, candidates)[:k]
        ans = complete(q, top)

        results.append({
            "question": q,
            "answer": ans,
            "citations": [
                {"doc": c.doc, "chunk_index": c.idx, "score": round(score, 3)}
                for c, score in top
            ],
        })

        if not as_json:
            print(f"\nQ: {q}")
            print(f"A: {ans}")
            print(f"   Citations:")
            for c, score in top:
                print(f"     - {c.doc} (chunk {c.idx}, score={score:.3f})")

    if as_json:
        print(json.dumps({
            "corpus": corpus_dir,
            "doc_count": len(set(c.doc for c, _ in index.query("anything", k=100))),
            "questions": results,
        }, indent=2))
    else:
        print(f"\n{'=' * 70}")
        print(f"Processed {len(questions)} questions against {corpus_dir}/")
        with_citations = sum(1 for r in results if r["citations"])
        print(f"  {with_citations}/{len(questions)} answered with citations")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="End-to-end RAG Q&A pipeline.")
    parser.add_argument("--corpus", default="data",
                        help="Corpus folder (default: data — workplace policies).")
    parser.add_argument("--k", type=int, default=3,
                        help="Top-k chunks to use per question.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return run_qa(args.corpus, as_json=args.json, k=args.k)


if __name__ == "__main__":
    sys.exit(main())
