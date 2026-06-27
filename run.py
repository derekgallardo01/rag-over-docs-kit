"""CLI: answer a question from the sample docs with citations.

    python run.py "what is the refund policy?"
    python run.py            # runs a few sample questions
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ragkit import answer, build_index  # noqa: E402

SAMPLES = [
    "What is the refund policy?",
    "How many days of PTO do new employees get?",
    "Who do I contact about a security incident?",
]


def main(argv: list[str]) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    index = build_index(os.path.join(here, "data"))
    questions = [" ".join(argv)] if argv else SAMPLES
    for q in questions:
        print(f"\nQ: {q}\n" + "-" * 60)
        print(answer(q, index))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
