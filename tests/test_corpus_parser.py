from app.corpus.manifest import (
    load_manifest,
)
from app.corpus.parser import (
    parse_docx_sections,
)
from app.corpus.chunker import (
    build_chunks,
)


def get_chunks(
    document_id: str,
):

    item = next(
        doc
        for doc in load_manifest()
        if doc.document_id
        == document_id
    )

    sections = parse_docx_sections(
        item.source_path
    )

    return build_chunks(
        document_id=item.document_id,
        title=item.title,
        sections=sections,
    )


def test_travel_table_is_preserved():

    chunks = get_chunks(
        "FIN-POL-003__V2.1"
    )

    text = "\n".join(
        chunk.text
        for chunk in chunks
    )

    assert "一线城市" in text
    assert "600" in text


def test_private_budget_table_is_preserved():

    chunks = get_chunks(
        "FIN-CONF-009__V1.0"
    )

    text = "\n".join(
        chunk.text
        for chunk in chunks
    )

    assert "100,000" in text
    assert "CEO" in text


def test_metadata_table_is_not_evidence():

    chunks = get_chunks(
        "FIN-POL-003__V2.1"
    )

    text = "\n".join(
        chunk.text
        for chunk in chunks
    )

    assert "知识负责人" not in text