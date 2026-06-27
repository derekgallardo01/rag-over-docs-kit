import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from ragkit import answer, build_index  # noqa: E402

INDEX = build_index(os.path.join(os.path.dirname(HERE), "data"))


def test_retrieval_finds_right_doc():
    hits = INDEX.query("what is the refund policy?", k=1)
    assert hits, "expected at least one hit"
    assert hits[0][0].doc == "refunds.md"


def test_pto_question_routes_to_hr():
    hits = INDEX.query("how many days of PTO do new employees get?", k=1)
    assert hits[0][0].doc == "hr-policy.md"


def test_answer_includes_citation_and_sources():
    out = answer("what is the refund policy?", INDEX)
    assert "[1]" in out
    assert "Sources:" in out
    assert "refunds.md" in out


def test_deterministic():
    a = answer("security incident contact", INDEX)
    b = answer("security incident contact", INDEX)
    assert a == b


def test_unknown_query_is_graceful():
    out = answer("what is the airspeed velocity of an unladen swallow?", INDEX)
    assert isinstance(out, str) and out
