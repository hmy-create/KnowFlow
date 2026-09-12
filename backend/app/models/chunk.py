from pydantic import BaseModel, Field


class Chunk(BaseModel):
    chunk_id: str = Field(
        ...,
        description="Chunk 唯一 ID"
    )

    document_id: str = Field(
        ...,
        description="所属文档 ID"
    )

    text: str = Field(
        ...,
        min_length=1,
        description="Chunk 原始文本"
    )

    page: int | None = Field(
        default=None,
        ge=1,
        description="来源页码"
    )

    section: str | None = Field(
        default=None,
        description="来源章节"
    )

    chunk_index: int = Field(
        ...,
        ge=0,
        description="Chunk 在文档中的顺序"
    )