# Evaluation

The eval harness answers the only question that matters when you change
chunking, the re-rank weight, or the model: **did this make the kit better,
worse, or the same?** It's deliberately small — the format is plain JSON so a
non-engineer client owner can extend it.

## What it does

[evals/run.py](../evals/run.py) loads [evals/golden.json](../evals/golden.json),
runs each query through the same `index.query` → `rerank` pipeline `answer()`
uses, and checks that the top citation's document matches the expected document.
It prints a pass rate + per-failure breakdown, and exits non-zero if anything
fails — so it can gate CI.

```text
Eval: 14/14 passed (100%)
```

On failure you get the specific mismatch:

```text
Eval: 13/14 passed (93%)

1 failed:
  [pto-carryover] can unused PTO carry over into next year?
       top='it-support.md' expected='hr-policy.md'
```

## Case format

Each case in `golden.json`:

```json
{
  "id": "refund-policy",
  "question": "what is the refund policy?",
  "expect": { "top_doc": "refunds.md" }
}
```

| Field in `expect` | Meaning |
|-------------------|---------|
| `top_doc` | Filename the top citation must come from. |

The harness deliberately only asserts on the *top* citation. Use the unit tests
in [tests/](../tests/) for finer-grained assertions (e.g. that a specific chunk
appears in the top-3, or that re-rank preserves a specific order).

## Adding cases

Three patterns to use when you bring this to a real client:

**1. Capture every real question the kit gets wrong.** Paste it into
`golden.json` with the correct expected doc. The eval set should be a
*regression net*: anything that broke once becomes a permanent test.

**2. Add paraphrases of the same question.** "What is the refund policy?",
"How do I get my money back?", "Returns policy?". If all three route to
`refunds.md` you have signal that retrieval is robust; if only one does you have
work to do.

**3. Add adversarial out-of-corpus questions.** Questions whose answer isn't in
the documents at all. Today the eval set doesn't include these because the
default `_local_stub` will still cite the closest chunk — adding "abstain"
behaviour (decline to answer when scores are weak) is a worthwhile follow-up
and would unlock testing those cases.

## Workflow when tuning

1. Add the new failing case(s) to `golden.json`.
2. Run `python evals/run.py` and see them fail.
3. Change `RERANK_WEIGHT`, chunk size, prompt template, or the corpus.
4. Re-run. Iterate until the pass rate is back to 100% and existing cases
   didn't regress.

This is the same loop that scales to a real model — the only difference is
runtime per case. With a real LLM, run evals on a smaller sample during
iteration and the full set in CI.

## What an eval set is not

- **Not a replacement for spot-checking real answers.** Read transcripts.
  Cited-doc-is-right doesn't guarantee answer-is-right.
- **Not a substitute for grounding evals.** A future improvement: check that
  the answer text actually quotes the cited chunk, not text from outside it.
- **Not exhaustive.** 14 cases here are illustrative. A serious deployment runs
  with 100+ cases and adds to the set every time something goes wrong.
