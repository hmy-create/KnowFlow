from pydantic import BaseModel, Field


class RetrievalCandidate(BaseModel):
    chunk_id: str
    document_id: str
    text: str

    page: int | None = None
    section: str | None = None
    chunk_index: int = 0

    retrieval_source: str

    raw_score: dict[str, float] = Field(
        default_factory=dict
    )

    fused_score: float = 0.0

    rerank_score: float | None = None


class HybridRetrievalResult(BaseModel):
    query: str
    rewritten_query: str

    bm25_candidates: list[RetrievalCandidate] = Field(
        default_factory=list
    )

    vector_candidates: list[RetrievalCandidate] = Field(
        default_factory=list
    )

    merged_candidates: list[RetrievalCandidate] = Field(
        default_factory=list
    )

    reranked_candidates: list[RetrievalCandidate] = Field(
        default_factory=list
    )