"""Interactive REPL for the RAG kit.

    python cli.py

Commands: 'k N' to change top-k (default 3), 'quit' / 'exit' / Ctrl-D to exit.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ragkit import answer, build_index  # noqa: E402


def main() -> int:
    index = build_index(os.path.join(HERE, "data"))
    k = 3
    print("RAG REPL. Commands: 'k N' to change top-k, 'quit' to exit.\n")
    while True:
        try:
            line = input("ask> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        if line.lower() in {"quit", "exit"}:
            return 0
        if line.lower().startswith("k ") and line[2:].strip().isdigit():
            k = int(line[2:].strip())
            print(f"(top-k = {k})\n")
            continue
        print(answer(line, index, k=k) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
