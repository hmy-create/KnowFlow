import os
from datetime import date

import pytest

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
        "RUN_LIVE_CORPUS_TESTS"
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
        ],
    )


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live corpus retrieval disabled",
)
def test_historical_travel_retrieval():

    routing = {
        "domain": "Finance",
        "sensitivity": "Normal",
        "version_mode": "Historical",
    }

    scope = build_retrieval_scope(
        query=(
            "2025年一线城市"
            "住宿上限是多少？"
        ),
        routing=routing,
        user=make_employee(),
        request_date=date(
            2026, 9, 19
        ),
    )

    assert (
        scope[
            "allowed_document_ids"
        ]
        == [
            "FIN-POL-003__V2.0"
        ]
    )

    chunks = (
        load_chunks_by_document_ids(
            scope[
                "allowed_document_ids"
            ]
        )
    )

    result = (
        hybrid_retrieve_scoped(
            query=(
                "2025年一线城市"
                "住宿上限是多少？"
            ),
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

    assert (
        result.reranked_candidates
    )

    assert all(
        item.document_id
        == "FIN-POL-003__V2.0"
        for item in (
            result.reranked_candidates
        )
    )


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live corpus retrieval disabled",
)
def test_current_conflict_sources_are_retrieved():

    routing = {
        "domain": "Finance",
        "sensitivity": "Normal",
        "version_mode": "Current",
    }

    query = (
        "现在一线城市"
        "出差住宿上限是多少？"
    )

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

    result = (
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

    returned_ids = {
        item.document_id
        for item in (
            result.reranked_candidates
        )
    }

    assert (
        "FIN-POL-003__V2.1"
        in returned_ids
    )

    assert (
        "FIN-NOTICE-017__V1.0"
        in returned_ids
    )