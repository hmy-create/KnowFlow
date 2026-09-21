import csv
import json
import re
import sys
from pathlib import Path


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

BACKEND_DIR = (
    REPO_ROOT
    / "backend"
)

if (
    str(BACKEND_DIR)
    not in sys.path
):
    sys.path.insert(
        0,
        str(BACKEND_DIR),
    )


from app.db.connection import (  # noqa: E402
    get_connection,
)


CSV_PATH = (
    REPO_ROOT
    / "eval"
    / "core_61.csv"
)

REPORT_PATH = (
    REPO_ROOT
    / "eval"
    / "core_61_document_gold_report.json"
)


def normalize_filename(
    value: str,
) -> str:

    return (
        Path(value)
        .name
        .strip()
        .lower()
    )


def load_document_map():

    result = {}

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    document_id,
                    source_file
                FROM documents
                ORDER BY document_id;
                """
            )

            rows = (
                cur.fetchall()
            )

    for (
        document_id,
        source_file,
    ) in rows:

        key = normalize_filename(
            source_file
        )

        result[key] = (
            document_id
        )

    return result


def extract_docx_names(
    expected_source: str,
) -> list[str]:

    source = (
        expected_source
        or ""
    ).strip()

    if not source:
        return []

    if (
        source.upper()
        == "NONE"
    ):
        return []

    # 抽取所有 .docx 文件名，
    # 支持：
    #
    # A.docx / B.docx
    # A.docx + B.docx
    names = re.findall(
        r"[^/+|\n\r]+?\.docx",
        source,
        flags=re.IGNORECASE,
    )

    result = []

    for name in names:

        clean = (
            name.strip()
        )

        if (
            clean
            and clean
            not in result
        ):
            result.append(
                clean
            )

    return result


def main():

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            CSV_PATH
        )

    document_map = (
        load_document_map()
    )

    with CSV_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        rows = list(
            reader
        )

        fieldnames = (
            reader.fieldnames
        )

    if fieldnames is None:
        raise RuntimeError(
            "CSV has no header."
        )

    unresolved = []

    enriched = 0

    no_source = 0

    for row in rows:

        case_id = row[
            "case_id"
        ]

        expected_source = (
            row.get(
                "expected_source"
            )
            or ""
        )

        filenames = (
            extract_docx_names(
                expected_source
            )
        )

        if not filenames:

            row[
                "relevant_document_ids_json"
            ] = "[]"

            no_source += 1

            continue

        document_ids = []

        case_unresolved = []

        for filename in filenames:

            key = normalize_filename(
                filename
            )

            document_id = (
                document_map.get(
                    key
                )
            )

            if document_id is None:

                case_unresolved.append(
                    filename
                )

                continue

            if (
                document_id
                not in document_ids
            ):
                document_ids.append(
                    document_id
                )

        # 只有全部文件都能映射，
        # 才认为该 Case 拥有完整 document Gold。
        if case_unresolved:

            row[
                "relevant_document_ids_json"
            ] = "[]"

            unresolved.append(
                {
                    "case_id":
                        case_id,

                    "expected_source":
                        expected_source,

                    "unresolved_files":
                        case_unresolved,
                }
            )

        else:

            row[
                "relevant_document_ids_json"
            ] = (
                json.dumps(
                    document_ids,
                    ensure_ascii=False,
                    separators=(
                        ",",
                        ":",
                    ),
                )
            )

            enriched += 1

    # 先备份
    backup_path = (
        CSV_PATH.with_name(
            "core_61_before_document_gold.csv"
        )
    )

    backup_path.write_bytes(
        CSV_PATH.read_bytes()
    )

    with CSV_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    report = {
        "total_cases":
            len(rows),

        "enriched_cases":
            enriched,

        "no_structured_source_cases":
            no_source,

        "unresolved_cases":
            len(unresolved),

        "unresolved":
            unresolved,

        "backup":
            str(
                backup_path
            ),

        "output":
            str(
                CSV_PATH
            ),
    }

    REPORT_PATH.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 90)
    print(
        "KnowFlow Document Gold Enrichment"
    )
    print("=" * 90)

    print(
        f"total_cases={len(rows)}"
    )

    print(
        f"enriched_cases={enriched}"
    )

    print(
        f"no_structured_source_cases="
        f"{no_source}"
    )

    print(
        f"unresolved_cases="
        f"{len(unresolved)}"
    )

    if unresolved:

        print()
        print(
            "UNRESOLVED:"
        )

        for item in unresolved:

            print(
                f"- {item['case_id']}: "
                f"{item['unresolved_files']}"
            )

    print()
    print(
        f"report={REPORT_PATH}"
    )

    print("=" * 90)


if __name__ == "__main__":
    main()