from backend.app.models import Chunk
from backend.app.retrieval.bm25_retriever import (
    bm25_retrieve,
)


def make_test_chunks():
    return [
        Chunk(
            chunk_id="TEST-C1",
            document_id="TEST-D1",
            text=(
                "TEST_ONLY 财务差旅报销 "
                "电子发票 行程凭证"
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
                "试用期 人事制度"
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
                "退款资格 产品规则"
            ),
            page=1,
            section="test",
            chunk_index=0,
        ),
    ]


def test_bm25_finance_retrieval():

    results = bm25_retrieve(
        "差旅报销电子发票",
        make_test_chunks(),
        top_n=20,
    )

    assert results

    assert (
        results[0].chunk_id
        == "TEST-C1"
    )

    assert (
        results[0].retrieval_source
        == "bm25"
    )

    assert (
        "bm25"
        in results[0].raw_score
    )