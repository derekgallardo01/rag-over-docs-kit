# Diagrams

Architecture / sequence / data diagrams beyond what's already inline in
[architecture.md](architecture.md).

## 1. End-to-end component model

```mermaid
flowchart TB
    subgraph Corpus["Corpus (per deployment)"]
      F1["data/*.md"]
      F2["data-tech/*.md"]
    end

    subgraph Index["Index build"]
      LD["load_docs()"]
      CT["chunk_text()<br/>(paragraph-ish, ≤600 chars)"]
      TI["TfidfIndex<br/>(IDF-weighted TF, cosine)"]
    end

    subgraph Query["Per-query path"]
      AN["answer()"]
      IQ["index.query(k=2k)"]
      RE["rerank()<br/>(α·sentence_overlap + (1-α)·tfidf)"]
      CO["complete()"]
      LS["_local_stub"]
      AZ["Azure OpenAI<br/>adapter"]
      AT["Anthropic<br/>adapter"]
    end

    F1 --> LD
    F2 -.-> LD
    LD --> CT
    CT --> TI
    AN --> IQ
    IQ --> TI
    TI --> IQ
    IQ --> RE
    RE --> CO
    CO --> LS
    CO -.-> AZ
    CO -.-> AT
    CO --> ANS["answer string<br/>+ [n] citations<br/>+ Sources list"]
```

## 2. Sequence — typical answered query

```mermaid
sequenceDiagram
    autonumber
    participant U as Caller
    participant A as answer()
    participant I as TfidfIndex
    participant R as rerank
    participant G as complete

    U->>A: answer("what is the refund policy?", index, k=3)
    A->>I: query("...", k=6)
    Note over I: Over-retrieve so rerank has options
    I-->>A: 6 (Chunk, tfidf_score) tuples
    A->>R: rerank("...", candidates, weight=0.35)
    R->>R: per chunk: best_sentence_overlap / |unique query tokens|
    R->>R: final = (1-α)·tfidf + α·bonus
    R-->>A: re-ordered list
    A->>A: slice to top-k
    A->>G: complete("...", [top 3 chunks])
    G->>G: _local_stub picks best sentence per chunk
    G-->>A: "...portal.example.com [1] ...\n\nSources:\n  [1] refunds.md (chunk 0)\n  [2] ..."
    A-->>U: cited answer string
```

## 3. Re-ranking — why it matters

```mermaid
flowchart LR
    Q["Query: 'how many days do I have to request a refund?'"]
    Q --> T["TF-IDF only<br/>(top 3)"]
    Q --> R["After rerank<br/>(top 3)"]

    T --> T1["0.484 refunds.md (chunk 0)"]
    T --> T2["0.167 security.md (chunk 0)"]
    T --> T3["0.084 hr-policy.md (chunk 0)"]

    R --> R1["0.659 refunds.md (chunk 0)"]
    R --> R2["0.237 security.md (chunk 0)"]
    R --> R3["0.154 hr-policy.md (chunk 0)"]

    style T1 fill:#fff7e6,stroke:#d97706
    style R1 fill:#dcfce7,stroke:#16a34a
```

Same chunks come back; the re-ranker pushes the right-doc score higher
relative to the others when the query tokens cluster in a single sentence
of the chunk. For ambiguous queries this changes the top — see
[evaluation.md](evaluation.md) for the workflow when you catch the kit
getting the order wrong on a real query.

## 4. Provider seam (where the real LLM plugs in)

```mermaid
flowchart LR
    complete["complete(query, hits)"] --> CK{"LLM_PROVIDER<br/>env var?"}
    CK -- "unset / 'local'" --> LS["_local_stub<br/>(deterministic, stdlib)"]
    CK -- "'azure'" --> AZ["_azure_complete<br/>(urllib → Azure OpenAI)"]
    CK -- "'anthropic'" --> AT["_anthropic_complete<br/>(urllib → Claude API)"]
    LS --> ANS["cited answer string"]
    AZ --> ANS
    AT --> ANS
```

The retrieval and re-ranking layers don't change when you swap providers
— only the final answer-text generation routes differently. The eval
harness can run against the local stub OR a real model; you'd switch the
env var in CI.
