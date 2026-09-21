from app.core.frozen_conflict_guard import (
    apply_frozen_conflict_guard,
)
from app.models import (
    RetrievalCandidate,
)


def make_evidence(
    chunk_id: str,
    document_id: str,
    text: str,
):
    return RetrievalCandidate(
        chunk_id=chunk_id,
        document_id=document_id,
        text=text,
        retrieval_source="hybrid",
        raw_score={},
        fused_score=0.0,
        rerank_score=1.0,
    )


CURRENT_TRAVEL_EVIDENCE = [
    make_evidence(
        "FIN-POL-003__V2.1__C001",
        "FIN-POL-003__V2.1",
        (
            "城市级别：一线城市"
            "（北京、上海、广州、深圳）；"
            "住宿上限：600元/间夜。"
        ),
    ),
    make_evidence(
        "FIN-NOTICE-017__V1.0__C001",
        "FIN-NOTICE-017__V1.0",
        (
            "北京、上海、广州、深圳的"
            "常规住宿建议上限为"
            "500元/间夜。"
        ),
    ),
    make_evidence(
        "FIN-NOTICE-017__V1.0__C003",
        "FIN-NOTICE-017__V1.0",
        (
            "本文件与财务部"
            "《差旅管理制度 V2.1》"
            "关于一线城市住宿上限的"
            "口径存在不一致。"
            "系统不应自行合并为单一规则。"
        ),
    ),
]


def test_current_first_tier_travel_conflict():

    result = apply_frozen_conflict_guard(
        query=(
            "现在一线城市"
            "出差住宿上限是多少？"
        ),
        domain="Finance",
        evidence=CURRENT_TRAVEL_EVIDENCE,
    )

    assert result is not None

    assert (
        result.decision
        == "conflict"
    )

    assert (
        "FIN-POL-003__V2.1__C001"
        in result.evidence_ids
    )

    assert (
        "FIN-NOTICE-017__V1.0__C001"
        in result.evidence_ids
    )


def test_unrelated_finance_query_not_conflict():

    result = apply_frozen_conflict_guard(
        query="电子发票可以报销吗？",
        domain="Finance",
        evidence=CURRENT_TRAVEL_EVIDENCE,
    )

    assert result is None


def test_only_one_side_not_conflict():

    result = apply_frozen_conflict_guard(
        query=(
            "现在一线城市"
            "住宿上限是多少？"
        ),
        domain="Finance",
        evidence=[
            CURRENT_TRAVEL_EVIDENCE[0]
        ],
    )

    assert result is None

def test_beishangguangshen_hotel_wording_conflict():

    result = apply_frozen_conflict_guard(
        query=(
            "北上广深出差住酒店"
            "最多能报多少？"
        ),
        domain="Finance",
        evidence=(
            CURRENT_TRAVEL_EVIDENCE
        ),
    )

    assert result is not None

    assert (
        result.decision
        == "conflict"
    )


def test_unrelated_hotel_query_not_conflict():

    result = apply_frozen_conflict_guard(
        query=(
            "其他城市住酒店"
            "最多能报多少？"
        ),
        domain="Finance",
        evidence=(
            CURRENT_TRAVEL_EVIDENCE
        ),
    )

    assert result is None