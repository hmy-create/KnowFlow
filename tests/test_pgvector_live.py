import os

import pytest

from app.db.connection import (
    get_connection,
)


RUN_LIVE_DB = (
    os.getenv("RUN_LIVE_DB_TESTS")
    == "1"
)


@pytest.mark.skipif(
    not RUN_LIVE_DB,
    reason="Live database test disabled",
)
def test_pgvector_connection():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT extversion
                FROM pg_extension
                WHERE extname = 'vector';
                """
            )

            result = cur.fetchone()

    assert result is not None

from app.db.vector_store import (
    delete_chunks,
    scoped_vector_search,
    upsert_chunk_embeddings,
)
from app.models import Chunk


def make_test_chunks():

    return [
        Chunk(
            chunk_id="TEST-PGV-C1",
            document_id="TEST-PUBLIC-D1",
            text=(
                "TEST_ONLY "
                "差旅报销需要电子发票和行程凭证。"
            ),
            page=1,
            section="测试财务",
            chunk_index=0,
        ),
        Chunk(
            chunk_id="TEST-PGV-C2",
            document_id="TEST-HR-D1",
            text=(
                "TEST_ONLY "
                "员工转正需要完成试用期考核。"
            ),
            page=1,
            section="测试人事",
            chunk_index=0,
        ),
        Chunk(
            chunk_id="TEST-PGV-C3",
            document_id="TEST-PRIVATE-D1",
            text=(
                "TEST_ONLY "
                "受限预算审批内部管理规则。"
            ),
            page=1,
            section="测试受限财务",
            chunk_index=0,
        ),
    ]

@pytest.mark.skipif(
    not RUN_LIVE_DB,
    reason="Live database test disabled",
)
def test_upsert_chunk_embeddings():

    chunks = make_test_chunks()

    ids = [
        chunk.chunk_id
        for chunk in chunks
    ]

    try:
        count = (
            upsert_chunk_embeddings(
                chunks
            )
        )

        assert count == 3

        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM chunk_embeddings
                    WHERE chunk_id = ANY(%s);
                    """,
                    (ids,),
                )

                count_in_db = (
                    cur.fetchone()[0]
                )

        assert count_in_db == 3

    finally:
        delete_chunks(ids)

@pytest.mark.skipif(
    not RUN_LIVE_DB,
    reason="Live database test disabled",
)
def test_scoped_vector_search_blocks_private_document():

    chunks = make_test_chunks()

    ids = [
        chunk.chunk_id
        for chunk in chunks
    ]

    try:
        upsert_chunk_embeddings(
            chunks
        )

        results = scoped_vector_search(
            query="预算审批规则是什么？",
            allowed_document_ids=[
                "TEST-PUBLIC-D1",
                "TEST-HR-D1",
            ],
            top_n=20,
        )

        returned_document_ids = {
            item.document_id
            for item in results
        }

        assert (
            "TEST-PRIVATE-D1"
            not in returned_document_ids
        )

    finally:
        delete_chunks(ids)

@pytest.mark.skipif(
    not RUN_LIVE_DB,
    reason="Live database test disabled",
)
def test_empty_scope_returns_nothing():

    results = scoped_vector_search(
        query="预算审批规则",
        allowed_document_ids=[],
        top_n=20,
    )

    assert results == []

@pytest.mark.skipif(
    not RUN_LIVE_DB,
    reason="Live database test disabled",
)
def test_public_vector_search():

    chunks = make_test_chunks()

    ids = [
        chunk.chunk_id
        for chunk in chunks
    ]

    try:
        upsert_chunk_embeddings(
            chunks
        )

        results = scoped_vector_search(
            query="差旅报销需要哪些材料？",
            allowed_document_ids=[
                "TEST-PUBLIC-D1",
            ],
            top_n=20,
        )

        assert results

        assert (
            results[0].document_id
            == "TEST-PUBLIC-D1"
        )

        assert (
            results[0].chunk_id
            == "TEST-PGV-C1"
        )

        assert (
            results[0].retrieval_source
            == "vector"
        )

        assert (
            "vector"
            in results[0].raw_score
        )

    finally:
        delete_chunks(ids)