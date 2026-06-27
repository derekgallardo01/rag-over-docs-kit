import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from ragkit import build_index, rerank  # noqa: E402

INDEX = build_index(os.path.join(os.path.dirname(HERE), "data"))


def test_rerank_is_deterministic():
    candidates = INDEX.query("refund policy", k=6)
    a = rerank("refund policy", candidates)
    b = rerank("refund policy", candidates)
    assert [c.idx for c, _ in a] == [c.idx for c, _ in b]
    assert [c.doc for c, _ in a] == [c.doc for c, _ in b]


def test_rerank_returns_same_chunks():
    candidates = INDEX.query("refund policy", k=6)
    before = sorted((c.doc, c.idx) for c, _ in candidates)
    after = sorted((c.doc, c.idx) for c, _ in rerank("refund policy", candidates))
    assert before == after


def test_rerank_preserves_strong_winner():
    # "refund" is unambiguous: the top should still be refunds.md after rerank.
    candidates = INDEX.query("what is the refund policy?", k=6)
    ranked = rerank("what is the refund policy?", candidates)
    assert ranked[0][0].doc == "refunds.md"


def test_rerank_weight_zero_keeps_tfidf_top():
    candidates = INDEX.query("refund", k=4)
    same = rerank("refund", candidates, weight=0.0)
    assert same[0][0].doc == candidates[0][0].doc
    assert same[0][0].idx == candidates[0][0].idx
