import json
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


REPO_ROOT = Path(__file__).resolve().parents[3]

MANIFEST_PATH = (
    REPO_ROOT
    / "docs"
    / "corpus"
    / "manifest.json"
)

CORPUS_DIR = (
    REPO_ROOT
    / "docs"
    / "corpus"
    / "KnowFlow_Corpus_V1.0"
)


class CorpusManifestEntry(BaseModel):
    document_id: str
    source_doc_no: str
    source_file: str

    domain: Literal[
        "HR",
        "Finance",
        "Product",
        "Service",
    ]

    topic_id: str
    title: str
    version_no: str

    effective_at: date
    expired_at: date | None

    status: Literal[
        "active",
        "expired",
    ]

    department: str

    confidentiality: Literal[
        "internal",
        "restricted",
    ]

    allowed_roles: list[str]

    kb_id: str

    @property
    def source_path(self) -> Path:
        return CORPUS_DIR / self.source_file


def load_manifest() -> list[CorpusManifestEntry]:

    raw = json.loads(
        MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    return [
        CorpusManifestEntry(
            **item
        )
        for item in raw["documents"]
    ]