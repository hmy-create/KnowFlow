from app.db.citation_repository import (
    get_citation_sources,
)
from app.models import Citation


def assemble_citations(
    trace_id: str,
    evidence_ids: list[str],
) -> list[Citation]:

    # 保序去重
    unique_ids = list(
        dict.fromkeys(
            evidence_ids
        )
    )

    if not unique_ids:
        return []

    sources = get_citation_sources(
        unique_ids
    )

    source_map = {
        item["chunk_id"]: item
        for item in sources
    }

    missing_ids = [
        chunk_id
        for chunk_id in unique_ids
        if chunk_id not in source_map
    ]

    if missing_ids:
        raise RuntimeError(
            "Citation mapping failed. "
            f"Missing chunk ids: "
            f"{missing_ids}"
        )

    citations = []

    for index, chunk_id in enumerate(
        unique_ids,
        start=1,
    ):
        source = source_map[
            chunk_id
        ]

        citation_id = (
            f"{trace_id}-CIT-"
            f"{index:03d}"
        )

        citations.append(
            Citation(
                citation_id=citation_id,
                chunk_id=chunk_id,
                document_id=(
                    source["document_id"]
                ),
                title=source["title"],
                version_no=(
                    source["version_no"]
                ),
                page=source["page"],
                section=source["section"],
                original_text=(
                    source["original_text"]
                ),
            )
        )

    return citations