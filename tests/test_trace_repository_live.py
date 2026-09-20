import os
import uuid
from datetime import date

import pytest

from app.db.connection import (
    get_connection,
)
from app.db.trace_repository import (
    get_trace,
    save_trace,
)
from app.models import (
    Citation,
    TraceRecord,
)


RUN_LIVE = (
    os.getenv(
        "RUN_LIVE_TRACE_TESTS"
    )
    == "1"
)


def _make_trace_id(
    suffix: str,
) -> str:
    return (
        f"TR-TEST-{suffix}-"
        f"{uuid.uuid4().hex[:12].upper()}"
    )


def _delete_trace(
    trace_id: str,
) -> None:

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                DELETE FROM traces
                WHERE trace_id = %s;
                """,
                (trace_id,),
            )

        conn.commit()


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live trace repository test disabled",
)
def test_trace_round_trip():

    trace_id = _make_trace_id(
        "ROUNDTRIP"
    )

    citation = Citation(
        citation_id=(
            f"{trace_id}-CIT-001"
        ),
        chunk_id=(
            "PROD-POL-A-004__V2.0__C001"
        ),
        document_id=(
            "PROD-POL-A-004__V2.0"
        ),
        title=(
            "产品A退款与取消规则"
        ),
        version_no="V2.0",
        page=None,
        section="二、退款规则",
        original_text=(
            "付款后14个自然日内，"
            "若累计使用核心付费功能"
            "不超过3次，可申请全额退款。"
        ),
    )

    trace = TraceRecord(
        trace_id=trace_id,

        query=(
            "产品A付款10天，"
            "核心付费功能用了2次，"
            "可以退款吗？"
        ),

        user_id="U004",

        domain="Product",

        sensitivity=None,

        version_mode="Current",

        query_date=date(
            2026,
            9,
            20,
        ),

        permission_filter={
            "permission_decision":
                "allowed",
            "role":
                "employee",
        },

        version_filter={
            "version_mode":
                "Current",
            "allowed_document_ids": [
                "PROD-POL-A-004__V2.0"
            ],
        },

        retrieved_chunks=[
            {
                "chunk_id":
                    "PROD-POL-A-004__V2.0__C001",
                "document_id":
                    "PROD-POL-A-004__V2.0",
                "retrieval_source":
                    "hybrid",
                "fused_score":
                    0.03,
                "rerank_score":
                    0.98,
            }
        ],

        rerank_scores=[
            {
                "chunk_id":
                    "PROD-POL-A-004__V2.0__C001",
                "score":
                    0.98,
            }
        ],

        decision="answer",

        decision_reason=(
            "当前证据足以支持回答。"
        ),

        clarifying_question="",

        evidence_ids=[
            "PROD-POL-A-004__V2.0__C001"
        ],

        citations=[
            citation
        ],

        latency_ms=321,

        input_tokens=1200,

        output_tokens=80,

        prompt_version=(
            "baseline-v1"
        ),
    )

    try:

        save_trace(
            trace
        )

        saved = get_trace(
            trace_id
        )

        assert saved is not None

        assert (
            saved["trace_id"]
            == trace_id
        )

        assert (
            saved["query"]
            == trace.query
        )

        assert (
            saved["user_id"]
            == "U004"
        )

        assert (
            saved["domain"]
            == "Product"
        )

        assert (
            saved["version_mode"]
            == "Current"
        )

        assert (
            saved["query_date"]
            == date(
                2026,
                9,
                20,
            )
        )

        assert (
            saved["decision"]
            == "answer"
        )

        assert (
            saved["latency_ms"]
            == 321
        )

        assert (
            saved["input_tokens"]
            == 1200
        )

        assert (
            saved["output_tokens"]
            == 80
        )

        assert (
            saved["prompt_version"]
            == "baseline-v1"
        )

        assert len(
            saved[
                "retrieved_chunks"
            ]
        ) == 1

        assert (
            saved[
                "retrieved_chunks"
            ][0]["chunk_id"]
            ==
            "PROD-POL-A-004__V2.0__C001"
        )

        assert len(
            saved["citations"]
        ) == 1

        assert (
            saved[
                "citations"
            ][0]["chunk_id"]
            ==
            "PROD-POL-A-004__V2.0__C001"
        )

        assert (
            saved[
                "citations"
            ][0]["version_no"]
            == "V2.0"
        )

    finally:

        _delete_trace(
            trace_id
        )


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live trace repository test disabled",
)
def test_no_access_trace_has_no_evidence():

    trace_id = _make_trace_id(
        "NOACCESS"
    )

    trace = TraceRecord(
        trace_id=trace_id,

        query=(
            "预算调整超过10万元"
            "谁审批？"
        ),

        user_id="U001",

        domain="Finance",

        sensitivity="Restricted",

        version_mode=None,

        query_date=None,

        permission_filter={
            "permission_decision":
                "no_access",
        },

        version_filter={},

        retrieved_chunks=[],

        rerank_scores=[],

        decision="no_access",

        decision_reason=(
            "当前身份没有访问"
            "相关受限知识的权限。"
        ),

        clarifying_question="",

        evidence_ids=[],

        citations=[],

        latency_ms=12,

        input_tokens=0,

        output_tokens=0,

        prompt_version=(
            "baseline-v1"
        ),
    )

    try:

        save_trace(
            trace
        )

        saved = get_trace(
            trace_id
        )

        assert saved is not None

        assert (
            saved["decision"]
            == "no_access"
        )

        assert (
            saved["retrieved_chunks"]
            == []
        )

        assert (
            saved["rerank_scores"]
            == []
        )

        assert (
            saved["evidence_ids"]
            == []
        )

        assert (
            saved["citations"]
            == []
        )

        assert (
            saved["input_tokens"]
            == 0
        )

        assert (
            saved["output_tokens"]
            == 0
        )

    finally:

        _delete_trace(
            trace_id
        )