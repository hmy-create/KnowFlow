from app.models import (
    EvidenceDecision,
    RetrievalCandidate,
)


PLAN_TERMS = (
    "涨薪",
    "降薪",
    "涨价",
    "降价",
    "扩招",
    "裁员",
    "增加夜班",
    "减少夜班",
    "年终奖",
)


FUTURE_TERMS = (
    "今年",
    "明年",
    "未来",
    "会不会",
    "是否会",
    "会",
    "计划",
)


def apply_frozen_refuse_guard(
    query: str,
    domain: str,
    evidence: list[RetrievalCandidate],
) -> EvidenceDecision | None:

    text = (
        query
        .replace(" ", "")
    )

    target_terms = [
        term
        for term in PLAN_TERMS
        if term in text
    ]

    if not target_terms:
        return None

    has_future_intent = any(
        term in text
        for term in FUTURE_TERMS
    )

    if not has_future_intent:
        return None

    # ============================================================
    # 只有当企业 Evidence 本身确实没有支持这个计划时
    # 才确定性 refuse。
    #
    # 避免未来真实文档明确写了计划，
    # 却被 Guard 无条件拒答。
    # ============================================================
    evidence_text = "\n".join(
        item.text
        for item in evidence
    )

    has_direct_support = any(
        term in evidence_text
        for term in target_terms
    )

    if has_direct_support:
        return None

    return EvidenceDecision(
        decision="refuse",

        reason=(
            "当前企业知识证据中没有找到"
            "能够支持该未来计划、预测或"
            "组织安排的可靠依据。"
        ),

        clarifying_question="",

        evidence_ids=[],

        risk_flags=[
            "unsupported_future_plan"
        ],
    )