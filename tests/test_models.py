import pytest
from pydantic import ValidationError

from datetime import date

from backend.app.models import User, Document, Chunk


def test_create_user():
    user = User(
        user_id="U001",
        department="finance",
        role="employee",
        authorized_kb_ids=["KB_FINANCE_PUBLIC"],
    )

    assert user.user_id == "U001"
    assert user.role == "employee"
    assert "KB_FINANCE_PUBLIC" in user.authorized_kb_ids


def test_create_current_document():
    doc = Document(
        document_id="FIN-POL-003",
        topic_id="travel_policy",
        title="差旅管理制度",
        version_no="V2.1",
        effective_at=date(2026, 5, 1),
        expired_at=None,
        status="active",
        department="finance",
        confidentiality="internal",
        allowed_roles=["employee", "finance_manager"],
        kb_id="KB_FINANCE_PUBLIC",
    )

    assert doc.version_no == "V2.1"
    assert doc.expired_at is None
    assert doc.status == "active"


def test_create_historical_document():
    doc = Document(
        document_id="FIN-POL-002",
        topic_id="travel_policy",
        title="差旅管理制度",
        version_no="V2.0",
        effective_at=date(2025, 6, 1),
        expired_at=date(2026, 4, 30),
        status="expired",
        department="finance",
        confidentiality="internal",
        allowed_roles=["employee", "finance_manager"],
        kb_id="KB_FINANCE_PUBLIC",
    )

    assert doc.version_no == "V2.0"
    assert doc.expired_at == date(2026, 4, 30)


def test_create_private_document():
    doc = Document(
        document_id="FIN-PRIVATE-001",
        topic_id="budget_adjustment",
        title="年度预算调整审批办法",
        version_no="V1.0",
        effective_at=date(2026, 1, 1),
        expired_at=None,
        status="active",
        department="finance",
        confidentiality="restricted",
        allowed_roles=["finance_manager", "admin"],
        kb_id="KB_FINANCE_PRIVATE",
    )

    assert doc.confidentiality == "restricted"
    assert "employee" not in doc.allowed_roles


def test_create_chunk():
    chunk = Chunk(
        chunk_id="FIN-POL-003-C014",
        document_id="FIN-POL-003",
        text="一线城市住宿标准为每晚 600 元。",
        page=4,
        section="住宿标准",
        chunk_index=13,
    )

    assert chunk.document_id == "FIN-POL-003"
    assert chunk.page == 4

def test_chunk_rejects_invalid_page():
    with pytest.raises(ValidationError):
        Chunk(
            chunk_id="C001",
            document_id="D001",
            text="测试文本",
            page=0,
            section="测试",
            chunk_index=0,
        )