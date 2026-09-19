from app.models import Chunk


MAX_CHARS = 1200


def split_lines(
    lines: list[str],
) -> list[str]:

    chunks = []

    current = []
    current_length = 0

    for line in lines:

        extra_length = (
            len(line) + 1
        )

        if (
            current
            and current_length
            + extra_length
            > MAX_CHARS
        ):
            chunks.append(
                "\n".join(current)
            )

            current = []
            current_length = 0

        current.append(line)

        current_length += (
            extra_length
        )

    if current:
        chunks.append(
            "\n".join(current)
        )

    return chunks


def build_chunks(
    document_id: str,
    title: str,
    sections: list[dict],
) -> list[Chunk]:

    results = []

    chunk_index = 0

    for section in sections:

        pieces = split_lines(
            section["lines"]
        )

        for piece in pieces:

            text = (
                f"文档：{title}\n"
                f"章节：{section['section']}\n"
                f"{piece}"
            )

            results.append(
                Chunk(
                    chunk_id=(
                        f"{document_id}"
                        f"__C{chunk_index:03d}"
                    ),
                    document_id=document_id,
                    text=text,
                    page=None,
                    section=(
                        section["section"]
                    ),
                    chunk_index=(
                        chunk_index
                    ),
                )
            )

            chunk_index += 1

    return results