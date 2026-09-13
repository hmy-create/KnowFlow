from datetime import date

from backend.app.core.query_time_resolver import (
    resolve_query_time,
)
from backend.app.core.version_filter import (
    filter_documents_by_version,
    is_applicable,
)
from backend.app.models import Document

from backend.app.core.permission_filter import (
    allowed_document,
)
from backend.app.models import User


def make_old_document():
    return Document(
        document_id="FIN-TRAVEL-V20",
        topic_id="travel_policy",
        title="差旅管理制度",
        version_no="V2.0",
        effective_at=date(
            2025, 6, 1
        ),
        expired_at=date(
            2026, 4, 30
        ),
        status="expired",
        department="finance",
        confidentiality="internal",
        allowed_roles=[
            "employee",
            "finance_manager",
        ],
        kb_id="KB_FINANCE_PUBLIC",
    )


def make_new_document():
    return Document(
        document_id="FIN-TRAVEL-V21",
        topic_id="travel_policy",
        title="差旅管理制度",
        version_no="V2.1",
        effective_at=date(
            2026, 5, 1
        ),
        expired_at=None,
        status="active",
        department="finance",
        confidentiality="internal",
        allowed_roles=[
            "employee",
            "finance_manager",
        ],
        kb_id="KB_FINANCE_PUBLIC",
    )


def make_future_supplement():
    return Document(
        document_id="FIN-TRAVEL-SUPP",
        topic_id="travel_policy",
        title="差旅住宿补充说明",
        version_no="V1.0",
        effective_at=date(
            2026, 5, 10
        ),
        expired_at=None,
        status="active",
        department="finance",
        confidentiality="internal",
        allowed_roles=[
            "employee",
            "finance_manager",
        ],
        kb_id="KB_FINANCE_PUBLIC",
    )

def test_expiry_date_is_inclusive():

    old_doc = make_old_document()

    assert is_applicable(
        old_doc,
        date(2026, 4, 30),
    )


def test_old_version_invalid_after_expiry():

    old_doc = make_old_document()

    assert not is_applicable(
        old_doc,
        date(2026, 5, 1),
    )


def test_new_version_valid_on_effective_date():

    new_doc = make_new_document()

    assert is_applicable(
        new_doc,
        date(2026, 5, 1),
    )


def test_future_document_not_yet_applicable():

    future_doc = (
        make_future_supplement()
    )

    assert not is_applicable(
        future_doc,
        date(2026, 5, 9),
    )

def test_v102_april_30_uses_old_version():

    docs = [
        make_old_document(),
        make_new_document(),
    ]

    context = resolve_query_time(
        query=(
            "2026年4月30日"
            "一线城市住宿标准是多少？"
        ),
        version_mode="Historical",
        request_date=date(
            2026, 9, 12
        ),
    )

    result = (
        filter_documents_by_version(
            docs,
            context,
        )
    )

    assert result.historical_document_ids == [
        "FIN-TRAVEL-V20"
    ]

    assert (
        "FIN-TRAVEL-V21"
        in result.blocked_document_ids
    )

def test_v102_may_1_uses_new_version():

    docs = [
        make_old_document(),
        make_new_document(),
    ]

    context = resolve_query_time(
        query=(
            "2026年5月1日"
            "一线城市住宿标准是多少？"
        ),
        version_mode="Current",
        request_date=date(
            2026, 9, 12
        ),
    )

    result = (
        filter_documents_by_version(
            docs,
            context,
        )
    )

    assert result.current_document_ids == [
        "FIN-TRAVEL-V21"
    ]

    assert (
        "FIN-TRAVEL-V20"
        in result.blocked_document_ids
    )

def test_v102_future_supplement_excluded():

    docs = [
        make_new_document(),
        make_future_supplement(),
    ]

    context = resolve_query_time(
        query=(
            "2026年5月9日"
            "一线城市住宿标准是多少？"
        ),
        version_mode="Current",
        request_date=date(
            2026, 9, 12
        ),
    )

    result = (
        filter_documents_by_version(
            docs,
            context,
        )
    )

    assert result.current_document_ids == [
        "FIN-TRAVEL-V21"
    ]

    assert (
        "FIN-TRAVEL-SUPP"
        in result.blocked_document_ids
    )

def test_historical_year_uses_period():

    context = resolve_query_time(
        query=(
            "2025年一线城市"
            "住宿标准是多少？"
        ),
        version_mode="Historical",
        request_date=date(
            2026, 9, 12
        ),
    )

    assert context.selector == "period"

    assert context.period_start == date(
        2025, 1, 1
    )

    assert context.period_end == date(
        2025, 12, 31
    )

def test_historical_year_keeps_overlapping_version():

    docs = [
        make_old_document(),
        make_new_document(),
    ]

    context = resolve_query_time(
        query=(
            "2025年一线城市"
            "住宿标准是多少？"
        ),
        version_mode="Historical",
        request_date=date(
            2026, 9, 12
        ),
    )

    result = (
        filter_documents_by_version(
            docs,
            context,
        )
    )

    assert (
        "FIN-TRAVEL-V20"
        in result.historical_document_ids
    )

    assert (
        "FIN-TRAVEL-V21"
        not in result.historical_document_ids
    )

def test_current_query_uses_request_date():

    context = resolve_query_time(
        query="现在住宿标准是多少？",
        version_mode="Current",
        request_date=date(
            2026, 9, 12
        ),
    )

    assert (
        context.query_date
        == date(2026, 9, 12)
    )

    assert (
        context.selector
        == "request_time"
    )

def test_comparison_separates_versions():

    docs = [
        make_old_document(),
        make_new_document(),
    ]

    context = resolve_query_time(
        query=(
            "产品现在和旧版"
            "有什么区别？"
        ),
        version_mode="Comparison",
        request_date=date(
            2026, 9, 12
        ),
    )

    result = (
        filter_documents_by_version(
            docs,
            context,
        )
    )

    assert (
        "FIN-TRAVEL-V21"
        in result.current_document_ids
    )

    assert (
        "FIN-TRAVEL-V20"
        in result.historical_document_ids
    )

def make_pending_document():
    return Document(
        document_id="FIN-PENDING",
        topic_id="travel_policy",
        title="待发布制度",
        version_no="V3.0",
        effective_at=date(
            2026, 1, 1
        ),
        expired_at=None,
        status="pending",
        department="finance",
        confidentiality="internal",
        allowed_roles=["employee"],
        kb_id="KB_FINANCE_PUBLIC",
    )

def test_pending_document_not_current():

    docs = [
        make_new_document(),
        make_pending_document(),
    ]

    context = resolve_query_time(
        query="现在住宿标准是多少？",
        version_mode="Current",
        request_date=date(
            2026, 9, 12
        ),
    )

    result = (
        filter_documents_by_version(
            docs,
            context,
        )
    )

    assert (
        "FIN-PENDING"
        not in result.current_document_ids
    )

def test_permission_then_version_order():

    public_doc = make_new_document()

    private_doc = Document(
        document_id="FIN-PRIVATE-V1",
        topic_id="budget",
        title="预算审批规则",
        version_no="V1.0",
        effective_at=date(
            2026, 1, 1
        ),
        expired_at=None,
        status="active",
        department="finance",
        confidentiality="restricted",
        allowed_roles=[
            "finance_manager",
        ],
        kb_id="KB_FINANCE_PRIVATE",
    )

    employee = User(
        user_id="U001",
        department="finance",
        role="employee",
        authorized_kb_ids=[
            "KB_FINANCE_PUBLIC",
        ],
    )

    all_docs = [
        public_doc,
        private_doc,
    ]

    permission_scope = [
        doc
        for doc in all_docs
        if allowed_document(
            doc,
            employee,
        )
    ]

    assert [
        doc.document_id
        for doc in permission_scope
    ] == [
        "FIN-TRAVEL-V21"
    ]

    context = resolve_query_time(
        query="现在差旅标准是多少？",
        version_mode="Current",
        request_date=date(
            2026, 9, 12
        ),
    )

    result = (
        filter_documents_by_version(
            permission_scope,
            context,
        )
    )

    assert result.current_document_ids == [
        "FIN-TRAVEL-V21"
    ]

    assert (
        "FIN-PRIVATE-V1"
        not in result.current_document_ids
    )

def make_current_conflict_document_a():
    return Document(
        document_id="FIN-CONFLICT-A",
        topic_id="travel_policy",
        title="差旅住宿规则 A",
        version_no="V2.1-A",
        effective_at=date(2026, 5, 1),
        expired_at=None,
        status="active",
        department="finance",
        confidentiality="internal",
        allowed_roles=[
            "employee",
            "finance_manager",
        ],
        kb_id="KB_FINANCE_PUBLIC",
    )


def make_current_conflict_document_b():
    return Document(
        document_id="FIN-CONFLICT-B",
        topic_id="travel_policy",
        title="差旅住宿规则 B",
        version_no="V2.1-B",
        effective_at=date(2026, 6, 1),
        expired_at=None,
        status="active",
        department="finance",
        confidentiality="internal",
        allowed_roles=[
            "employee",
            "finance_manager",
        ],
        kb_id="KB_FINANCE_PUBLIC",
    )

def test_multiple_current_valid_documents_are_all_kept():
    docs = [
        make_current_conflict_document_a(),
        make_current_conflict_document_b(),
    ]

    context = resolve_query_time(
        query="现在一线城市住宿标准是多少？",
        version_mode="Current",
        request_date=date(2026, 9, 12),
    )

    result = filter_documents_by_version(
        docs,
        context,
    )

    assert set(
        result.current_document_ids
    ) == {
        "FIN-CONFLICT-A",
        "FIN-CONFLICT-B",
    }

    assert result.historical_document_ids == []

    assert result.blocked_document_ids == []