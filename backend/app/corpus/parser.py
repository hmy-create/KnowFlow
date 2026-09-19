import re
from pathlib import Path

from docx import Document as DocxDocument
from docx.table import Table
from docx.text.paragraph import Paragraph

from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P


METADATA_KEYS = {
    "文档编号",
    "所属部门",
    "版本号",
    "状态",
    "生效日期",
    "失效日期",
    "知识负责人",
    "保密级别",
}


def clean_text(text: str) -> str:
    return " ".join(
        text.replace("\n", " ").split()
    )


def iter_blocks(doc):
    for child in doc.element.body.iterchildren():

        if isinstance(child, CT_P):
            yield Paragraph(
                child,
                doc,
            )

        elif isinstance(child, CT_Tbl):
            yield Table(
                child,
                doc,
            )


def is_metadata_table(
    table: Table,
) -> bool:

    first_column = {
        clean_text(
            row.cells[0].text
        )
        for row in table.rows
        if row.cells
    }

    return (
        "文档编号" in first_column
        and "版本号" in first_column
    )


def serialize_business_table(
    table: Table,
) -> list[str]:

    if not table.rows:
        return []

    headers = [
        clean_text(cell.text)
        for cell
        in table.rows[0].cells
    ]

    results = []

    for row in table.rows[1:]:

        cells = [
            clean_text(cell.text)
            for cell in row.cells
        ]

        parts = []

        for index, value in enumerate(
            cells
        ):
            if not value:
                continue

            header = (
                headers[index]
                if index < len(headers)
                else f"字段{index + 1}"
            )

            parts.append(
                f"{header}：{value}"
            )

        if parts:
            results.append(
                "；".join(parts)
            )

    return results


def is_section_heading(
    paragraph: Paragraph,
    text: str,
) -> bool:

    if (
        paragraph.style
        and paragraph.style.name
        and paragraph.style.name.startswith(
            "Heading"
        )
    ):
        return True

    return bool(
        re.match(
            r"^[一二三四五六七八九十]+、",
            text,
        )
    )


def parse_docx_sections(
    path: Path,
) -> list[dict]:

    doc = DocxDocument(path)

    sections = []

    current_section = "文档概述"
    current_lines = []

    # 公司名、标题通常是前两行，
    # 标题后续由 manifest 单独加到 chunk
    intro_count = 0

    def flush():
        nonlocal current_lines

        if current_lines:
            sections.append(
                {
                    "section":
                        current_section,
                    "lines":
                        current_lines,
                }
            )

            current_lines = []

    for block in iter_blocks(doc):

        if isinstance(
            block,
            Paragraph,
        ):
            text = clean_text(
                block.text
            )

            if not text:
                continue

            if intro_count < 2:
                intro_count += 1
                continue

            if is_section_heading(
                block,
                text,
            ):
                flush()

                current_section = text

                continue

            current_lines.append(text)

        elif isinstance(
            block,
            Table,
        ):

            if is_metadata_table(
                block
            ):
                continue

            table_lines = (
                serialize_business_table(
                    block
                )
            )

            current_lines.extend(
                table_lines
            )

    flush()

    return sections