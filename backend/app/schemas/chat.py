from pydantic import BaseModel, Field

from app.models import User
from app.models import Citation

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

    decision: str | None = None

    reason: str | None = None

    clarifying_question: str = ""

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

    evidence_ids: list[str] = Field(
    default_factory=list
    )

    risk_flags: list[str] = Field(
        default_factory=list
    )

    trace_id: str | None = None

    citation_ids: list[str] = Field(
        default_factory=list
    )

    citations: list[Citation] = Field(
        default_factory=list
    )