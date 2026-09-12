from pydantic import BaseModel, Field


class Badcase(BaseModel):
    badcase_id: str = Field(
        ...,
        description="Badcase 唯一 ID"
    )

    trace_id: str = Field(
        ...,
        description="关联 Trace ID"
    )

    query: str = Field(
        ...,
        description="导致 Badcase 的用户问题"
    )

    badcase_type: str = Field(
        ...,
        description="错误类型，例如 version_error"
    )

    root_cause: str = ""

    fix: str = ""

    status: str = Field(
        default="open",
        description="open / fixed / regressed / closed"
    )

    regression_run_id: str | None = None