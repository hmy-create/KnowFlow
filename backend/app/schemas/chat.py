from pydantic import BaseModel, Field

from app.models import User


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
    )

    user: User


class EvidenceDebug(BaseModel):
    chunk_id: str
    document_id: str

    text: str

    page: int | None = None
    section: str | None = None

    retrieval_source: str

    raw_score: dict[str, float] = Field(
        default_factory=dict
    )

    fused_score: float = 0.0

    rerank_score: float | None = None


class ChatResponse(BaseModel):
    status: str

    query: str

    domain: str

    sensitivity: str | None = None

    version_mode: str | None = None

    permission_decision: str

    message: str

    query_date: str | None = None

    time_selector: str | None = None

    period_start: str | None = None
    period_end: str | None = None

    current_document_ids: list[str] = Field(
        default_factory=list
    )

    historical_document_ids: list[str] = Field(
        default_factory=list
    )

    allowed_document_ids: list[str] = Field(
        default_factory=list
    )

    evidence_count: int = 0

    evidence: list[EvidenceDebug] = Field(
        default_factory=list
    )