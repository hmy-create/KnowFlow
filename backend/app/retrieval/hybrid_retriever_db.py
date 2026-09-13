from app.db.vector_store import (
    scoped_vector_search,
)
from app.models import (
    Chunk,
    HybridRetrievalResult,
)
from app.retrieval.bm25_retriever import (
    bm25_retrieve,
)
from app.retrieval.fusion import (
    reciprocal_rank_fusion,
)
from app.retrieval.query_rewrite import (
    rewrite_query,
)
from app.retrieval.reranker import (
    rerank_candidates,
)


def hybrid_retrieve_scoped(
    query: str,
    allowed_chunks: list[Chunk],
    allowed_document_ids: list[str],
    top_n: int = 20,
    top_k: int = 10,
) -> HybridRetrievalResult:
    """
    S6 PostgreSQL / pgvector 版本 Hybrid Retrieval。

    调用前要求：
    - allowed_chunks 已经过 S4 + S5
    - allowed_document_ids 已经过 S4 + S5

    BM25 和 Vector 使用相同的权限/版本 scope。
    """

    if not allowed_document_ids:
        return HybridRetrievalResult(
            query=query,
            rewritten_query=(
                rewrite_query(query)
            ),
        )

    rewritten_query = (
        rewrite_query(query)
    )

    bm25_candidates = (
        bm25_retrieve(
            query=rewritten_query,
            chunks=allowed_chunks,
            top_n=top_n,
        )
    )

    vector_candidates = (
        scoped_vector_search(
            query=rewritten_query,
            allowed_document_ids=(
                allowed_document_ids
            ),
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
            query=rewritten_query,
            candidates=merged_candidates,
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