from datetime import date

from pydantic import BaseModel, Field


class Document(BaseModel):
    document_id: str = Field(
        ...,
        description="文档唯一 ID"
    )

    topic_id: str = Field(
        ...,
        description="知识主题 ID，例如 travel_policy"
    )

    title: str = Field(
        ...,
        description="文档名称"
    )

    version_no: str = Field(
        ...,
        description="版本号，例如 V2.1"
    )

    effective_at: date = Field(
        ...,
        description="文档生效日期"
    )

    expired_at: date | None = Field(
        default=None,
        description="文档失效日期；None 表示当前没有明确失效时间"
    )

    status: str = Field(
        ...,
        description="版本状态，例如 active / expired / pending"
    )

    department: str = Field(
        ...,
        description="文档所属业务部门"
    )

    confidentiality: str = Field(
        ...,
        description="保密级别，例如 internal / restricted"
    )

    allowed_roles: list[str] = Field(
        default_factory=list,
        description="允许访问该文档的角色"
    )

    kb_id: str = Field(
        ...,
        description="文档所属知识库 ID"
    )