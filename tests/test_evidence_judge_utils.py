from app.core.evidence_judge import (
    _normalize_evidence_id,
)


def test_normalize_plain_evidence_id():

    assert (
        _normalize_evidence_id(
            "ABC__C001"
        )
        == "ABC__C001"
    )


def test_normalize_prefixed_evidence_id():

    assert (
        _normalize_evidence_id(
            "EVIDENCE_ID=ABC__C001"
        )
        == "ABC__C001"
    )