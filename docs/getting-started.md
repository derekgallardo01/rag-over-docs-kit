# Getting started

A 5-minute walkthrough — no LLM keys, no `pip install` other than pytest.

## 1. Clone and run the demo

```bash
git clone https://github.com/derekgallardo01/rag-over-docs-kit.git
cd rag-over-docs-kit
python run.py
```

You should see three sample questions answered with `[1]` / `[2]`
citations to specific documents and chunks under `data/`.

## 2. Run the eval set

```bash
python evals/run.py
```

`Eval (golden.json): 14/14 passed (100%)`. There's a second corpus
(technical / API docs):

```bash
python evals/run.py golden-tech.json data-tech
```

`Eval (golden-tech.json): 12/12 passed (100%)`.

## 3. Try the interactive REPL

```bash
python cli.py
ask> what is the refund policy?
ask> k 5
ask> how do I create an API key?
```

`k N` changes the top-k for subsequent questions.

## 4. Plug in a real LLM (optional)

The default generator is a deterministic local stub so the demo runs
without keys. To use Azure OpenAI:

```bash
export LLM_PROVIDER=azure
export AZURE_OPENAI_ENDPOINT="https://<your>.openai.azure.com"
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_DEPLOYMENT="gpt-4o"
python run.py
```

Or Anthropic:

```bash
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY="..."
python run.py
```

The retrieval + chunking + citation layers don't change — only the
final answer generation routes to the real model.

## 5. Run in Docker (optional)

```bash
docker build -t rag-kit .
docker run --rm rag-kit
```

## What to read next

- [Architecture](architecture.md) · [Customization](customization.md) ·
  [Evaluation](evaluation.md) · [Diagrams](diagrams.md) · [FAQ](faq.md)
