from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str = Field(..., description="用户唯一标识")

    department: str = Field(
        ...,
        description="用户所属部门"
    )

    role: str = Field(
        ...,
        description="用户角色，例如 employee / finance_manager / admin"
    )

    authorized_kb_ids: list[str] = Field(
        default_factory=list,
        description="用户有权访问的知识库 ID 列表"
    )