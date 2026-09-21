from app.models import (
    EvidenceDecision,
    RetrievalCandidate,
)


# ============================================================
# Frozen unsupported future-plan semantics
#
# 这些词只有在 Query 同时具有未来 / 计划语义时，
# 才进入 refuse 判断。
#
# 不能只因为出现关键词就 refuse。
# ============================================================
PLAN_TERMS = (
    # HR
    "涨薪",
    "降薪",
    "裁员",
    "扩招",
    "缩招",
    "年终奖",

    # Product
    "涨价",
    "降价",
    "新增功能",
    "增加功能",

    # Service / staffing
    "增加夜班",
    "减少夜班",
    "轮班",
    "排班调整",
)


FUTURE_TERMS = (
    "今年",
    "明年",
    "未来",
    "以后",
    "会不会",
    "是否会",
    "会",
    "计划",
    "准备",
    "将",
    "改成",
)


def apply_frozen_refuse_guard(
    query: str,
    domain: str,
    evidence: list[
        RetrievalCandidate
    ],
) -> EvidenceDecision | None:
    """
    Frozen unsupported future-plan guard.

    处理已经由 Frozen Core / Gold Eval
    明确确认的业务边界：

    用户询问未来的人事、产品、价格、
    排班等计划，但当前企业知识库
    没有直接支持该计划的可靠证据时，
    必须 refuse，而不是猜测、answer
    或因为条件不明而 clarify。

    例如：

    - 公司明年会统一涨薪吗？
    - 公司今年有没有裁员计划？
    - 产品A明年会涨价吗？
    - 产品A明年会新增哪些功能？
    - 客服团队明年会扩招吗？
    - 客服今年会改成24小时轮班吗？
    """

    text = (
        query
        .replace(" ", "")
    )

    # ========================================================
    # 1. Query 必须命中明确的计划主题
    # ========================================================
    target_terms = [
        term
        for term in PLAN_TERMS
        if term in text
    ]

    if not target_terms:
        return None

    # ========================================================
    # 2. 必须存在未来 / 计划语义
    #
    # 避免误伤：
    #
    # “现在客服轮班制度是什么？”
    #
    # 这种是现行制度查询，
    # 不应该被 Future Refuse Guard 拦截。
    # ========================================================
    has_future_intent = any(
        term in text
        for term in FUTURE_TERMS
    )

    if not has_future_intent:
        return None

    # ========================================================
    # 3. 检查 Evidence 是否真的直接支持该计划
    #
    # 只有当前企业 Evidence 没有直接出现
    # 对应目标事实时才 refuse。
    #
    # 特别注意：
    #
    # G096 中 Evidence 虽然出现：
    # - 值班主管
    # - 工作时间
    # - 24小时内给反馈
    #
    # 但这些都不是“轮班制度”证据。
    #
    # 因此这里只用 target_terms 做直接支持判断，
    # 不用“24小时”这种过宽关键词。
    # ========================================================
    evidence_text = "\n".join(
        (
            item.text
            or ""
        )
        for item in evidence
    )

    has_direct_support = any(
        term in evidence_text
        for term in target_terms
    )

    if has_direct_support:
        return None

    # ========================================================
    # 4. Frozen Refuse
    # ========================================================
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