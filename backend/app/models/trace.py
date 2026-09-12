from datetime import date

from pydantic import BaseModel, Field


class Trace(BaseModel):
    trace_id: str = Field(
        ...,
        description="一次请求的唯一 Trace ID"
    )

    query: str = Field(
        ...,
        description="用户原始 Query"
    )

    domain: str | None = None

    version_mode: str | None = None

    query_date: date | None = None

    permission_filter: dict = Field(
        default_factory=dict
    )

    version_filter: dict = Field(
        default_factory=dict
    )

    retrieved_chunks: list[str] = Field(
        default_factory=list
    )

    rerank_scores: list[float] = Field(
        default_factory=list
    )

    decision: str | None = None

    citations: list[str] = Field(
        default_factory=list
    )

    latency_ms: int = 0

    input_tokens: int = 0

    output_tokens: int = 0

    prompt_version: str = "baseline-v1"