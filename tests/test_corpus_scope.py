from datetime import date

from app.core.retrieval_scope import (
    build_retrieval_scope,
)
from app.models import User


def make_finance_employee():
    return User(
        user_id="U001",
        department="finance",
        role="employee",
        authorized_kb_ids=[
            "KB_FINANCE_PUBLIC",
        ],
    )


def make_finance_manager():
    return User(
        user_id="U002",
        department="finance",
        role="finance_manager",
        authorized_kb_ids=[
            "KB_FINANCE_PUBLIC",
            "KB_FINANCE_PRIVATE",
        ],
    )


def test_historical_travel_scope():

    routing = {
        "domain": "Finance",
        "sensitivity": "Normal",
        "version_mode": "Historical",
    }

    result = build_retrieval_scope(
        query=(
            "2025年一线城市"
            "住宿上限是多少？"
        ),
        routing=routing,
        user=make_finance_employee(),
        request_date=date(
            2026, 9, 19
        ),
    )

    assert (
        result["permission_decision"]
        == "allowed"
    )

    assert (
        result[
            "allowed_document_ids"
        ]
        == [
            "FIN-POL-003__V2.0"
        ]
    )


def test_current_finance_scope():

    routing = {
        "domain": "Finance",
        "sensitivity": "Normal",
        "version_mode": "Current",
    }

    result = build_retrieval_scope(
        query=(
            "现在一线城市"
            "出差住宿上限是多少？"
        ),
        routing=routing,
        user=make_finance_employee(),
        request_date=date(
            2026, 9, 19
        ),
    )

    ids = set(
        result[
            "allowed_document_ids"
        ]
    )

    assert ids == {
        "FIN-POL-003__V2.1",
        "FIN-NOTICE-017__V1.0",
        "FIN-FAQ-002__V1.2",
    }


def test_restricted_employee_is_blocked():

    routing = {
        "domain": "Finance",
        "sensitivity": "Restricted",
        "version_mode": None,
    }

    result = build_retrieval_scope(
        query=(
            "预算调整超过10万元"
            "谁审批？"
        ),
        routing=routing,
        user=make_finance_employee(),
        request_date=date(
            2026, 9, 19
        ),
    )

    assert (
        result["permission_decision"]
        == "no_access"
    )

    assert (
        result[
            "allowed_document_ids"
        ]
        == []
    )


def test_restricted_manager_only_sees_private():

    routing = {
        "domain": "Finance",
        "sensitivity": "Restricted",
        "version_mode": None,
    }

    result = build_retrieval_scope(
        query=(
            "预算调整超过10万元"
            "谁审批？"
        ),
        routing=routing,
        user=make_finance_manager(),
        request_date=date(
            2026, 9, 19
        ),
    )

    assert (
        result["permission_decision"]
        == "allowed"
    )

    assert (
        result[
            "allowed_document_ids"
        ]
        == [
            "FIN-CONF-009__V1.0"
        ]
    )