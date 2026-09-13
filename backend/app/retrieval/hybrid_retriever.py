from app.models import (
    Chunk,
    HybridRetrievalResult,
)
from app.retrieval.bm25_retriever import (
    bm25_retrieve,
)
from app.retrieval.vector_retriever import (
    vector_retrieve,
)
from app.retrieval.fusion import (
    reciprocal_rank_fusion,
)
from app.retrieval.reranker import (
    rerank_candidates,
)
from app.retrieval.query_rewrite import (
    rewrite_query,
)


def hybrid_retrieve(
    query: str,
    chunks: list[Chunk],
    top_n: int = 20,
    top_k: int = 10,
) -> HybridRetrievalResult:

    rewritten_query = (
        rewrite_query(query)
    )

    bm25_candidates = (
        bm25_retrieve(
            rewritten_query,
            chunks,
            top_n=top_n,
        )
    )

    vector_candidates = (
        vector_retrieve(
            rewritten_query,
            chunks,
            top_n=top_n,
        )
    )

    merged_candidates = (
        reciprocal_rank_fusion(
            bm25_candidates,
            vector_candidates,
        )
    )

    reranked_candidates = (
        rerank_candidates(
            rewritten_query,
            merged_candidates,
            top_k=top_k,
        )
    )

    return HybridRetrievalResult(
        query=query,
        rewritten_query=rewritten_query,
        bm25_candidates=(
            bm25_candidates
        ),
        vector_candidates=(
            vector_candidates
        ),
        merged_candidates=(
            merged_candidates
        ),
        reranked_candidates=(
            reranked_candidates
        ),
    )