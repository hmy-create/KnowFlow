from app.corpus.manifest import (
    load_manifest,
)
from app.corpus.parser import (
    parse_docx_sections,
)
from app.corpus.chunker import (
    build_chunks,
)
from app.db.document_repository import (
    upsert_document,
)
from app.db.vector_store import (
    delete_document_chunks,
    upsert_chunk_embeddings,
)
from app.db.schema import (
    init_database,
)


def main():

    init_database()

    manifest = load_manifest()

    total_chunks = 0

    print(
        f"Documents to ingest: "
        f"{len(manifest)}"
    )

    for index, item in enumerate(
        manifest,
        start=1,
    ):

        print(
            f"[{index}/{len(manifest)}] "
            f"{item.source_file}"
        )

        if not item.source_path.exists():
            raise FileNotFoundError(
                item.source_path
            )

        upsert_document(item)

        sections = (
            parse_docx_sections(
                item.source_path
            )
        )

        chunks = build_chunks(
            document_id=(
                item.document_id
            ),
            title=item.title,
            sections=sections,
        )

        delete_document_chunks(
            item.document_id
        )

        count = (
            upsert_chunk_embeddings(
                chunks
            )
        )

        total_chunks += count

        print(
            f"  chunks={count}"
        )

    print("")
    print(
        "Corpus ingestion completed."
    )
    print(
        f"documents={len(manifest)}"
    )
    print(
        f"chunks={total_chunks}"
    )


if __name__ == "__main__":
    main()