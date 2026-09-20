from typing import Literal

from pydantic import BaseModel, Field


class EvidenceDecision(BaseModel):
    decision: Literal[
        "answer",
        "clarify",
        "conflict",
        "refuse",
        "no_access",
    ]

    reason: str

    clarifying_question: str = ""

    evidence_ids: list[str] = Field(
        default_factory=list
    )

    risk_flags: list[str] = Field(
        default_factory=list
    )
    input_tokens: int = 0
    output_tokens: int = 0

    model_name: str | None = None

    prompt_version: str = "baseline-v1"