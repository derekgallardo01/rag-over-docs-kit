"""Run the RAG kit against the golden evaluation set and report pass/fail.

    python evals/run.py

Exit code is 0 if all cases pass, 1 otherwise — suitable for CI gating.
Each case asserts the top citation comes from the expected document.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from ragkit import build_index, rerank  # noqa: E402


def main() -> int:
    with open(os.path.join(HERE, "golden.json"), encoding="utf-8") as fh:
        cases = json.load(fh)
    data = os.path.join(os.path.dirname(HERE), "data")
    index = build_index(data)

    passed, failed = [], []
    for case in cases:
        candidates = index.query(case["question"], k=6)
        ranked = rerank(case["question"], candidates)
        top_doc = ranked[0][0].doc if ranked else None
        expected = case["expect"]["top_doc"]
        rec = {"id": case["id"], "question": case["question"],
               "top": top_doc, "expected": expected}
        (passed if top_doc == expected else failed).append(rec)

    total = len(cases)
    rate = (len(passed) / total * 100) if total else 0.0
    print(f"Eval: {len(passed)}/{total} passed ({rate:.0f}%)")
    if failed:
        print(f"\n{len(failed)} failed:")
        for f in failed:
            print(f"  [{f['id']}] {f['question']}")
            print(f"       top={f['top']!r} expected={f['expected']!r}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
