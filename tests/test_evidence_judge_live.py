import os
from datetime import date

import pytest

from app.core.evidence_state_machine import (
    decide_evidence_state,
)
from app.core.retrieval_scope import (
    build_retrieval_scope,
)
from app.db.vector_store import (
    load_chunks_by_document_ids,
)
from app.models import User
from app.retrieval.hybrid_retriever_db import (
    hybrid_retrieve_scoped,
)


RUN_LIVE = (
    os.getenv(
        "RUN_LIVE_JUDGE_TESTS"
    )
    == "1"
)


def make_employee():
    return User(
        user_id="U001",
        department="finance",
        role="employee",
        authorized_kb_ids=[
            "KB_FINANCE_PUBLIC",
            "KB_HR_PUBLIC",
            "KB_PRODUCT_PUBLIC",
            "KB_SERVICE_PUBLIC",
        ],
    )


def run_current_case(
    query: str,
    routing: dict,
):

    scope = build_retrieval_scope(
        query=query,
        routing=routing,
        user=make_employee(),
        request_date=date(
            2026, 9, 19
        ),
    )

    chunks = (
        load_chunks_by_document_ids(
            scope[
                "allowed_document_ids"
            ]
        )
    )

    retrieval = (
        hybrid_retrieve_scoped(
            query=query,
            allowed_chunks=chunks,
            allowed_document_ids=(
                scope[
                    "allowed_document_ids"
                ]
            ),
            top_n=20,
            top_k=10,
        )
    )

    return decide_evidence_state(
        query=query,
        domain=routing["domain"],
        sensitivity=routing.get(
            "sensitivity"
        ),
        version_mode=routing.get(
            "version_mode"
        ),
        permission_decision=(
            scope[
                "permission_decision"
            ]
        ),
        evidence=(
            retrieval
            .reranked_candidates
        ),
        current_document_ids=(
            scope[
                "current_document_ids"
            ]
        ),
        historical_document_ids=(
            scope[
                "historical_document_ids"
            ]
        ),
        query_time_summary=(
            "request_date=2026-09-19"
        ),
    )


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live Evidence Judge disabled",
)
def test_finance_current_conflict():

    result = run_current_case(
        query=(
            "现在一线城市出差"
            "住宿上限是多少？"
        ),
        routing={
            "domain": "Finance",
            "sensitivity": "Normal",
            "version_mode": "Current",
        },
    )

    assert (
        result.decision
        == "conflict"
    )

    assert result.evidence_ids


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live Evidence Judge disabled",
)
def test_hr_ambiguous_trial_period_clarify():

    result = run_current_case(
        query="试用期多久？",
        routing={
            "domain": "HR",
            "sensitivity": None,
            "version_mode": "Current",
        },
    )

    assert (
        result.decision
        == "clarify"
    )

    assert (
        result.clarifying_question
    )


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live Evidence Judge disabled",
)
def test_product_pfix_answer():

    result = run_current_case(
        query=(
            "产品A付款10天，"
            "核心付费功能用了2次，"
            "可以退款吗？"
        ),
        routing={
            "domain": "Product",
            "sensitivity": None,
            "version_mode": "Current",
        },
    )

    assert (
        result.decision
        == "answer"
    )

    assert (
        result.clarifying_question
        == ""
    )


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live Evidence Judge disabled",
)
def test_service_missing_level_clarify():

    result = run_current_case(
        query="客户投诉多久回复？",
        routing={
            "domain": "Service",
            "sensitivity": None,
            "version_mode": None,
        },
    )

    assert (
        result.decision
        == "clarify"
    )