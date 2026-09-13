from app.models import Chunk
from app.retrieval.bm25_retriever import (
    bm25_retrieve,
)


def test_retrieval_cannot_see_blocked_chunk():

    allowed_chunks = [
        Chunk(
            chunk_id="PUBLIC-C1",
            document_id="PUBLIC-D1",
            text=(
                "TEST_ONLY 普通财务报销说明"
            ),
            chunk_index=0,
        ),
    ]

    # PRIVATE-C1 根本没有放进 allowed_chunks

    results = bm25_retrieve(
        query="财务报销",
        chunks=allowed_chunks,
        top_n=20,
    )

    returned_ids = {
        item.chunk_id
        for item in results
    }

    assert (
        "PRIVATE-C1"
        not in returned_ids
    )