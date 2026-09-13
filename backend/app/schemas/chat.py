from pydantic import BaseModel, Field

from app.models import User


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="用户输入的企业知识问题",
    )

    user: User


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