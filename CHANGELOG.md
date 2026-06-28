# Changelog

Notable changes to the RAG-over-your-docs kit. Dates are when the change
landed on `main`.

## 2026-06-27 — Docker support
- Dockerfile so the kit runs via `docker run` without a Python install
- README "Run in Docker" section

## 2026-06-27 — Second worked corpus (technical docs)
- `data-tech/` (API auth / rate limits / webhooks) — proves the kit isn't
  just for workplace HR/refunds/security docs
- `evals/golden-tech.json` — 12 cases across the technical corpus
- `evals/run.py` now accepts positional args for the golden file + data folder
- CI runs both eval sets on every push

## 2026-06-27 — GitHub Actions CI
- `.github/workflows/ci.yml` running pytest + eval + smoke-test on Python 3.11
- CI status badge added to README

## 2026-06-27 — Build-out: re-ranking, evals, docs
- `rerank()` combining TF-IDF score with a query-sentence-overlap bonus;
  `answer()` over-retrieves 2k candidates and re-ranks
- `evals/golden.json` (14 cases) + `evals/run.py` with CI-gating exit code
- `cli.py` interactive REPL with adjustable top-k
- `tests/test_rerank.py` covering determinism, chunk preservation,
  strong-winner preservation, weight-zero behaviour
- `docs/architecture.md`, `customization.md`, `evaluation.md`
- `docs/sample-run.txt` (UTF-8 captured single + re-rank before/after +
  cross-doc citation output)
- README rewritten with architecture, sample, eval, customization sections

## 2026-06-27 — Initial public release
- TF-IDF retrieval + chunking pipeline over a document folder
- Source-cited grounded answers (document + chunk index per citation)
- Local stub generator + Azure OpenAI / Anthropic adapters via `LLM_PROVIDER`
- 5 unit tests
