from app.db.document_repository import (
    get_documents_by_ids,
)
from app.models import (
    RetrievalCandidate,
)


def build_evidence_context(
    evidence: list[
        RetrievalCandidate
    ],
) -> str:

    if not evidence:
        return (
            "当前没有可用企业知识证据。"
        )

    document_ids = list(
        dict.fromkeys(
            item.document_id
            for item in evidence
        )
    )

    documents = (
        get_documents_by_ids(
            document_ids
        )
    )

    document_map = {
        doc.document_id: doc
        for doc in documents
    }

    blocks = []

    for item in evidence:

        doc = document_map.get(
            item.document_id
        )

        metadata_lines = []

        if doc is not None:

            metadata_lines = [
                f"document_id: "
                f"{doc.document_id}",

                f"title: "
                f"{doc.title}",

                f"version_no: "
                f"{doc.version_no}",

                f"effective_at: "
                f"{doc.effective_at}",

                f"expired_at: "
                f"{doc.expired_at}",

                f"status: "
                f"{doc.status}",
            ]

        block = "\n".join(
            [
                (
                    f"[EVIDENCE_ID="
                    f"{item.chunk_id}]"
                ),
                *metadata_lines,
                (
                    f"section: "
                    f"{item.section or ''}"
                ),
                (
                    f"rerank_score: "
                    f"{item.rerank_score}"
                ),
                "content:",
                item.text,
            ]
        )

        blocks.append(block)

    return "\n\n".join(blocks)