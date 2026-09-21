import csv
import json
from pathlib import Path

from app.models import (
    EvalCase,
    EvalUser,
)


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)


DATASET_PATHS = {
    "core_61": (
        REPO_ROOT
        / "eval"
        / "core_61.csv"
    ),
    "gold_v1": (
        REPO_ROOT
        / "eval"
        / "gold_v1.csv"
    ),
}


def _optional_text(
    value: str | None,
) -> str | None:

    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    return value


def _parse_json_list(
    value: str | None,
) -> list[str]:

    if value is None:
        return []

    value = value.strip()

    if not value:
        return []

    payload = json.loads(
        value
    )

    if not isinstance(
        payload,
        list,
    ):
        raise ValueError(
            f"Expected JSON list, got: "
            f"{value}"
        )

    return [
        str(item)
        for item in payload
    ]


def _parse_bool(
    value: str | None,
) -> bool:

    if value is None:
        return False

    normalized = (
        value.strip().lower()
    )

    if normalized in {
        "true",
        "1",
        "yes",
        "y",
    }:
        return True

    if normalized in {
        "false",
        "0",
        "no",
        "n",
        "",
    }:
        return False

    raise ValueError(
        f"Invalid boolean: {value}"
    )


def get_dataset_path(
    dataset_name: str,
) -> Path:

    path = DATASET_PATHS.get(
        dataset_name
    )

    if path is None:
        raise ValueError(
            f"Unknown eval dataset: "
            f"{dataset_name}"
        )

    if not path.exists():
        raise FileNotFoundError(
            path
        )

    return path


def _row_to_case(
    row: dict,
) -> EvalCase:

    user = EvalUser(
        user_id=row[
            "user_id"
        ].strip(),

        department=row[
            "department"
        ].strip(),

        role=row[
            "role"
        ].strip(),

        authorized_kb_ids=(
            _parse_json_list(
                row.get(
                    "authorized_kb_ids_json"
                )
            )
        ),
    )

    return EvalCase(
        case_id=row[
            "case_id"
        ].strip(),

        set_name=(
            row.get(
                "set_name"
            )
            or "core_61"
        ).strip(),

        category=(
            row.get(
                "category"
            )
            or ""
        ).strip(),

        query=row[
            "query"
        ].strip(),

        user=user,

        expected_domain=(
            _optional_text(
                row.get(
                    "expected_domain"
                )
            )
        ),

        expected_sensitivity=(
            _optional_text(
                row.get(
                    "expected_sensitivity"
                )
            )
        ),

        expected_version_mode=(
            _optional_text(
                row.get(
                    "expected_version_mode"
                )
            )
        ),

        expected_permission_decision=(
            _optional_text(
                row.get(
                    "expected_permission_decision"
                )
            )
        ),

        expected_decision=(
            _optional_text(
                row.get(
                    "expected_decision"
                )
            )
        ),

        relevant_document_ids=(
            _parse_json_list(
                row.get(
                    "relevant_document_ids_json"
                )
            )
        ),

        relevant_chunk_ids=(
            _parse_json_list(
                row.get(
                    "relevant_chunk_ids_json"
                )
            )
        ),

        expected_citation_document_ids=(
            _parse_json_list(
                row.get(
                    "expected_citation_document_ids_json"
                )
            )
        ),

        expected_citation_chunk_ids=(
            _parse_json_list(
                row.get(
                    "expected_citation_chunk_ids_json"
                )
            )
        ),

        require_clarifying_question=(
            _parse_bool(
                row.get(
                    "require_clarifying_question"
                )
            )
        ),

        expected_answer_keypoints=(
            row.get(
                "expected_answer_keypoints"
            )
            or ""
        ).strip(),

        expected_source=(
            row.get(
                "expected_source"
            )
            or ""
        ).strip(),

        route_expectation=(
            row.get(
                "route_expectation"
            )
            or ""
        ).strip(),

        notes=(
            row.get(
                "notes"
            )
            or ""
        ).strip(),

        frozen_stage=(
            row.get(
                "frozen_stage"
            )
            or ""
        ).strip(),

        frozen_domain_actual=(
            _optional_text(
                row.get(
                    "frozen_domain_actual"
                )
            )
        ),

        frozen_actual_decision=(
            _optional_text(
                row.get(
                    "frozen_actual_decision"
                )
            )
        ),

        frozen_actual_result_summary=(
            row.get(
                "frozen_actual_result_summary"
            )
            or ""
        ).strip(),

        frozen_actual_source=(
            row.get(
                "frozen_actual_source"
            )
            or ""
        ).strip(),

        frozen_route_actual=(
            row.get(
                "frozen_route_actual"
            )
            or ""
        ).strip(),

        frozen_pass=(
            _parse_bool(
                row.get(
                    "frozen_pass"
                )
            )
        ),

        test_type=(
            row.get(
                "test_type"
            )
            or ""
        ).strip(),
    )


def load_eval_cases(
    dataset_name: str = "core_61",
) -> list[EvalCase]:

    path = get_dataset_path(
        dataset_name
    )

    with path.open(
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

    cases = [
        _row_to_case(
            row
        )
        for row in rows
    ]

    if not cases:
        raise RuntimeError(
            f"Eval dataset is empty: "
            f"{path}"
        )

    ids = [
        item.case_id
        for item in cases
    ]

    if (
        len(ids)
        != len(set(ids))
    ):
        raise RuntimeError(
            "Duplicate case_id found "
            "in eval dataset."
        )

    return cases