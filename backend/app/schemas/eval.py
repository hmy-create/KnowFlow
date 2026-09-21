from pydantic import (
    BaseModel,
    Field,
)


class EvalRunRequest(BaseModel):

    dataset: str = "core_61"

    limit: int | None = Field(
        default=None,
        ge=1,
    )

    case_ids: list[str] = Field(
        default_factory=list
    )


class EvalRunResponse(BaseModel):

    run_id: str

    dataset_name: str

    total_cases: int

    passed_cases: int

    failed_cases: int

    pass_rate: float

    metrics: dict = Field(
        default_factory=dict
    )

    report_paths: dict = Field(
        default_factory=dict
    )