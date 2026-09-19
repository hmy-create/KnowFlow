from app.core.evidence_state_machine import (
    decide_evidence_state,
)
from app.models import (
    RetrievalCandidate,
)


def make_evidence(
    chunk_id: str,
    document_id: str,
):
    return RetrievalCandidate(
        chunk_id=chunk_id,
        document_id=document_id,
        text="TEST_ONLY evidence",
        retrieval_source="hybrid",
        raw_score={
            "bm25": 1.0,
            "vector": 0.9,
        },
        fused_score=0.03,
        rerank_score=0.9,
    )


def test_no_access_bypasses_judge():

    result = decide_evidence_state(
        query="预算调整超过10万元谁审批？",
        domain="Finance",
        sensitivity="Restricted",
        version_mode=None,
        permission_decision="no_access",
        evidence=[],
        current_document_ids=[],
        historical_document_ids=[],
    )

    assert (
        result.decision
        == "no_access"
    )

    assert result.evidence_ids == []


def test_historical_with_evidence_answers():

    result = decide_evidence_state(
        query="2025年住宿标准是多少？",
        domain="Finance",
        sensitivity="Normal",
        version_mode="Historical",
        permission_decision="allowed",
        evidence=[
            make_evidence(
                "FIN-V20-C1",
                "FIN-POL-003__V2.0",
            )
        ],
        current_document_ids=[],
        historical_document_ids=[
            "FIN-POL-003__V2.0"
        ],
    )

    assert (
        result.decision
        == "answer"
    )


def test_historical_without_evidence_refuses():

    result = decide_evidence_state(
        query="2024年某规则是什么？",
        domain="Finance",
        sensitivity="Normal",
        version_mode="Historical",
        permission_decision="allowed",
        evidence=[],
        current_document_ids=[],
        historical_document_ids=[],
    )

    assert (
        result.decision
        == "refuse"
    )


def test_private_allowed_answers():

    result = decide_evidence_state(
        query="预算调整超过10万元谁审批？",
        domain="Finance",
        sensitivity="Restricted",
        version_mode=None,
        permission_decision="allowed",
        evidence=[
            make_evidence(
                "PRIVATE-C1",
                "FIN-CONF-009__V1.0",
            )
        ],
        current_document_ids=[],
        historical_document_ids=[],
    )

    assert (
        result.decision
        == "answer"
    )


def test_comparison_requires_both_sides():

    evidence = [
        make_evidence(
            "CUR-C1",
            "PROD-POL-A-004__V2.0",
        ),
    ]

    result = decide_evidence_state(
        query=(
            "产品A现在和旧版"
            "退款规则有什么区别？"
        ),
        domain="Product",
        sensitivity=None,
        version_mode="Comparison",
        permission_decision="allowed",
        evidence=evidence,
        current_document_ids=[
            "PROD-POL-A-004__V2.0"
        ],
        historical_document_ids=[
            "PROD-POL-A-004__V1.0"
        ],
    )

    assert (
        result.decision
        == "refuse"
    )


def test_other_refuses():

    result = decide_evidence_state(
        query="今天天气怎么样？",
        domain="Other",
        sensitivity=None,
        version_mode=None,
        permission_decision="allowed",
        evidence=[],
        current_document_ids=[],
        historical_document_ids=[],
    )

    assert (
        result.decision
        == "refuse"
    )