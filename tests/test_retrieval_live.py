import os

import pytest

from app.models import Chunk
from app.retrieval.hybrid_retriever import (
    hybrid_retrieve,
)


RUN_LIVE = (
    os.getenv(
        "RUN_LIVE_RETRIEVAL_TESTS"
    )
    == "1"
)


@pytest.mark.skipif(
    not RUN_LIVE,
    reason=(
        "Live retrieval test disabled"
    ),
)
def test_hybrid_retrieval():

    chunks = [
        Chunk(
            chunk_id="TEST-C1",
            document_id="TEST-D1",
            text=(
                "TEST_ONLY 财务差旅报销 "
                "需要关注电子发票与行程凭证。"
            ),
            page=1,
            section="test",
            chunk_index=0,
        ),
        Chunk(
            chunk_id="TEST-C2",
            document_id="TEST-D2",
            text=(
                "TEST_ONLY 员工转正 "
                "涉及试用期和人事管理。"
            ),
            page=1,
            section="test",
            chunk_index=0,
        ),
        Chunk(
            chunk_id="TEST-C3",
            document_id="TEST-D3",
            text=(
                "TEST_ONLY 产品A退款 "
                "属于产品退款规则。"
            ),
            page=1,
            section="test",
            chunk_index=0,
        ),
    ]

    result = hybrid_retrieve(
        query="差旅报销需要哪些材料？",
        chunks=chunks,
        top_n=20,
        top_k=10,
    )

    assert result.reranked_candidates

    assert (
        result.reranked_candidates[
            0
        ].chunk_id
        == "TEST-C1"
    )

    top = (
        result.reranked_candidates[
            0
        ]
    )

    assert top.rerank_score is not None

    assert top.retrieval_source in {
        "bm25",
        "vector",
        "hybrid",
    }

    assert top.raw_score