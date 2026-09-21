from app.services.eval_loader import (
    load_eval_cases,
)


def test_core_61_loads():

    cases = load_eval_cases(
        "core_61"
    )

    assert len(cases) == 61


def test_core_61_ids_unique():

    cases = load_eval_cases(
        "core_61"
    )

    ids = [
        item.case_id
        for item in cases
    ]

    assert len(ids) == len(
        set(ids)
    )


def test_f001_frozen_gold():

    cases = load_eval_cases(
        "core_61"
    )

    case = next(
        item
        for item in cases
        if item.case_id == "F001"
    )

    assert (
        case.expected_domain
        == "Finance"
    )

    assert (
        case.expected_sensitivity
        == "Normal"
    )

    assert (
        case.expected_version_mode
        == "Current"
    )

    assert (
        case.expected_decision
        == "conflict"
    )

    assert (
        case.frozen_actual_decision
        == "conflict"
    )