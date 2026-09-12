from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="用户输入的企业知识问题",
    )


class ChatResponse(BaseModel):
    status: str
    message: str
    query: str