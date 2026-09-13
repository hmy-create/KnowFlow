from backend.app.models import (
    RetrievalCandidate,
)
from backend.app.retrieval.fusion import (
    reciprocal_rank_fusion,
)


def candidate(
    chunk_id: str,
    source: str,
    score: float,
):
    return RetrievalCandidate(
        chunk_id=chunk_id,
        document_id=f"D-{chunk_id}",
        text="TEST_ONLY",
        retrieval_source=source,
        raw_score={
            source: score
        },
    )


def test_rrf_merges_duplicate_chunk():

    bm25 = [
        candidate(
            "C1",
            "bm25",
            8.0,
        )
    ]

    vector = [
        candidate(
            "C1",
            "vector",
            0.91,
        )
    ]

    merged = (
        reciprocal_rank_fusion(
            bm25,
            vector,
        )
    )

    assert len(merged) == 1

    assert (
        merged[0].retrieval_source
        == "hybrid"
    )

    assert (
        "bm25"
        in merged[0].raw_score
    )

    assert (
        "vector"
        in merged[0].raw_score
    )

    assert (
        merged[0].fused_score
        > 0
    )