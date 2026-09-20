from pydantic import BaseModel


class Citation(BaseModel):
    citation_id: str

    chunk_id: str
    document_id: str

    title: str
    version_no: str

    page: int | None = None
    section: str | None = None

    original_text: str