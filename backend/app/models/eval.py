from pydantic import BaseModel, Field


class EvalCase(BaseModel):
    case_id: str = Field(
        ...,
        description="评测 Case 唯一 ID"
    )

    query: str = Field(
        ...,
        description="评测问题"
    )

    expected_domain: str | None = None

    expected_version_mode: str | None = None

    expected_decision: str | None = None

    expected_answer_keypoints: list[str] = Field(
        default_factory=list
    )

    user_role: str = "employee"

    department: str | None = None

    query_date: str | None = None