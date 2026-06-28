# FAQ

## Do I need API keys?

No. The default generator is a deterministic local stub. `LLM_PROVIDER`
env var routes to Azure OpenAI or Anthropic when you're ready — see
[customization.md §4](customization.md#4-plug-a-real-llm-azure-openai-or-anthropic).

## Why TF-IDF? Why not embeddings?

TF-IDF is dependency-free, deterministic, and good enough for the typical
client doc set (hundreds to low-thousands of chunks). The re-ranker
(query-sentence overlap) catches the cases where pure TF-IDF gets fooled
by token frequency. For larger corpora or fuzzy semantic similarity, swap
the `TfidfIndex` for an embeddings-based retriever — `rerank()`, the
`Chunk` dataclass, and `complete()` don't change.

## How does the re-ranker work?

After top-k TF-IDF retrieval (2k candidates by default in `answer()`),
each chunk is re-scored as `(1-α)·tfidf + α·sentence_overlap`. The
sentence-overlap term is the max number of query tokens that appear in
any single sentence of the chunk, divided by the count of unique query
tokens. `α = 0.35` by default. This punishes chunks where the query
tokens are scattered across paragraphs and rewards chunks where they
cluster in one sentence — which is usually the actual answer.

## How are citations generated?

Each chunk in the top-k is appended to the answer as `[1]`, `[2]`, etc.,
and a `Sources:` block lists the document name and chunk index for each.
The doc + chunk index together let a reviewer click straight to the
exact passage.

## What's the difference between the two corpora?

- **`data/`** (workplace) — HR, refunds, security. Used by default.
- **`data-tech/`** (technical) — API auth, rate limits, webhooks.
  Pass as the second arg to `evals/run.py` to evaluate against it.

Both prove the same engine works across domains without code changes.

## How do I add my own documents?

Drop `.md` or `.txt` files into `data/` (or any folder you point
`build_index(...)` at). The retriever re-indexes on construction; no
separate build step. For PDF / DOCX, extract text first (the kit
deliberately doesn't pull in a parser).

## Why are some questions phrased the way they are in the eval set?

The TF-IDF retriever has no stopword list — so common words like "what"
and "do" contribute to scores. Eval questions are phrased to give the
right document strong, distinctive tokens. A real production deployment
would either add a stopword list or use embeddings (which handle this
gracefully). See `evals/golden-tech.json` for examples — "HTTP 429
error - retry strategy and backoff" rather than "What does HTTP 429
mean?" because the latter's stopwords pull the score to the wrong doc.

## How do I run the screenshot workflow?

`gh workflow run screenshots.yml --repo derekgallardo01/rag-over-docs-kit`.
Or manually from the GitHub Actions UI. It uses Playwright in headless
chromium to capture the live Pages demo and commits PNGs to
`docs/screenshots/`.
