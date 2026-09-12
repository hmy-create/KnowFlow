from typing import Literal

from pydantic import BaseModel, Field


class PermissionResult(BaseModel):
    decision: Literal["allowed", "no_access"]

    reason: str = Field(
        ...,
        description="权限判定原因"
    )

    allowed_document_ids: list[str] = Field(
        default_factory=list,
        description="权限过滤后允许进入后续流程的文档 ID"
    )

    blocked_count: int = Field(
        default=0,
        ge=0,
        description="因权限被过滤掉的文档数量"
    )