"""Run the RAG kit against a golden evaluation set and report pass/fail.

    python evals/run.py                              # default: golden.json + data/
    python evals/run.py golden-tech.json data-tech   # alternate corpus

Exit code is 0 if all cases pass, 1 otherwise — suitable for CI gating.
Each case asserts the top citation comes from the expected document.

Two corpora ship in the repo: the workplace one (HR / refunds / security)
under `data/`, and a technical-docs one (auth / rate-limits / webhooks)
under `data-tech/`. Each pairs with its own golden set.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from ragkit import build_index, rerank  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    golden_name = argv[0] if len(argv) > 0 else "golden.json"
    data_rel = argv[1] if len(argv) > 1 else "data"

    golden_path = (golden_name if os.path.isabs(golden_name)
                   else os.path.join(HERE, golden_name))
    data_path = (data_rel if os.path.isabs(data_rel)
                 else os.path.join(os.path.dirname(HERE), data_rel))

    with open(golden_path, encoding="utf-8") as fh:
        cases = json.load(fh)
    index = build_index(data_path)

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
    label = os.path.basename(golden_path)
    print(f"Eval ({label}): {len(passed)}/{total} passed ({rate:.0f}%)")
    if failed:
        print(f"\n{len(failed)} failed:")
        for f in failed:
            print(f"  [{f['id']}] {f['question']}")
            print(f"       top={f['top']!r} expected={f['expected']!r}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
