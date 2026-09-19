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