from app.core.frozen_clarify_guard import (
    apply_frozen_clarify_guard,
)
from app.models import (
    RetrievalCandidate,
)


def evidence(
    chunk_id: str,
    document_id: str,
    text: str,
):
    return RetrievalCandidate(
        chunk_id=chunk_id,
        document_id=document_id,
        text=text,
        retrieval_source="hybrid",
        raw_score={},
        fused_score=0.0,
        rerank_score=1.0,
    )


HR_EVIDENCE = [
    evidence(
        "HR-C1",
        "HR-POL-001__V2.0",
        (
            "社会招聘员工试用期原则上为3个月；"
            "表现优秀者可在入职满2个月后申请提前转正。"
            "校园招聘员工试用期原则上为6个月；"
            "表现优秀者可在入职满4个月后申请提前转正。"
        ),
    ),
    evidence(
        "HR-C2",
        "HR-POL-001__V2.0",
        (
            "适用于社会招聘与校园招聘员工。"
            "实习生不适用本制度。"
        ),
    ),
]


SERVICE_EVIDENCE = [
    evidence(
        "SERVICE-C1",
        "CS-SOP-001__V3.0",
        (
            "等级：P1；定义：涉及数据泄露；"
            "首次响应：15分钟内\n"
            "等级：P2；定义：核心功能受阻；"
            "首次响应：30分钟内\n"
            "等级：P3；定义：一般体验问题；"
            "首次响应：2小时内"
        ),
    ),
]


def test_hr_generic_trial_period_clarifies():

    result = apply_frozen_clarify_guard(
        query="试用期多久？",
        domain="HR",
        evidence=HR_EVIDENCE,
    )

    assert result is not None
    assert result.decision == "clarify"


def test_hr_explicit_social_recruit_does_not_force_clarify():

    result = apply_frozen_clarify_guard(
        query="社会招聘员工试用期多久？",
        domain="HR",
        evidence=HR_EVIDENCE,
    )

    assert result is None


def test_service_generic_complaint_time_clarifies():

    result = apply_frozen_clarify_guard(
        query="客户投诉多久回复？",
        domain="Service",
        evidence=SERVICE_EVIDENCE,
    )

    assert result is not None
    assert result.decision == "clarify"


def test_service_explicit_level_does_not_force_clarify():

    result = apply_frozen_clarify_guard(
        query="P1投诉多久回复？",
        domain="Service",
        evidence=SERVICE_EVIDENCE,
    )

    assert result is None


def test_service_specific_issue_does_not_force_clarify():

    result = apply_frozen_clarify_guard(
        query="数据泄露投诉多久回复？",
        domain="Service",
        evidence=SERVICE_EVIDENCE,
    )

    assert result is None