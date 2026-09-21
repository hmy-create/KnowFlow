from app.models import (
    EvidenceDecision,
    RetrievalCandidate,
)


def _join_evidence_text(
    evidence: list[RetrievalCandidate],
) -> str:
    return "\n".join(
        item.text
        for item in evidence
    )


def _evidence_ids_matching(
    evidence: list[RetrievalCandidate],
    keywords: list[str],
) -> list[str]:
    ids = []

    for item in evidence:
        if any(
            keyword in item.text
            for keyword in keywords
        ):
            ids.append(
                item.chunk_id
            )

    return list(
        dict.fromkeys(ids)
    )


def _hr_trial_period_guard(
    query: str,
    evidence: list[RetrievalCandidate],
) -> EvidenceDecision | None:
    """
    冻结 HR clarify 规则：

    当用户只问“试用期多久”，
    而有效证据中不同招聘类型对应不同试用期，
    且用户没有说明适用对象时，
    必须 clarify。
    """

    if "试用期" not in query:
        return None

    # 用户已经明确了决定性适用对象，
    # 不在这里强制澄清，交还 Evidence Judge。
    explicit_subjects = (
        "社会招聘",
        "社招",
        "校园招聘",
        "校招",
        "实习生",
    )

    if any(
        subject in query
        for subject in explicit_subjects
    ):
        return None

    evidence_text = (
        _join_evidence_text(
            evidence
        )
    )

    has_social_rule = (
        "社会招聘员工试用期"
        in evidence_text
    )

    has_campus_rule = (
        "校园招聘员工试用期"
        in evidence_text
    )

    # 只有确实检索到了多个不同适用口径，
    # 才触发 clarify。
    if not (
        has_social_rule
        and has_campus_rule
    ):
        return None

    evidence_ids = (
        _evidence_ids_matching(
            evidence,
            [
                "社会招聘员工试用期",
                "校园招聘员工试用期",
                "实习生",
            ],
        )
    )

    return EvidenceDecision(
        decision="clarify",
        reason=(
            "当前有效证据显示，不同招聘类型"
            "对应不同试用期口径，而用户尚未说明"
            "其适用的招聘类型，因此现有条件不足以"
            "唯一确定答案。"
        ),
        clarifying_question=(
            "请确认您想查询的是社会招聘员工、"
            "校园招聘员工，还是实习生的试用期？"
        ),
        evidence_ids=evidence_ids,
        risk_flags=[],
    )


def _service_response_time_guard(
    query: str,
    evidence: list[RetrievalCandidate],
) -> EvidenceDecision | None:
    """
    冻结 Service clarify 规则：

    用户询问投诉回复/响应时效，
    如果 P1/P2/P3 对应不同时效，
    用户又没有提供能够唯一确定等级的条件，
    必须 clarify。
    """

    has_complaint_intent = (
        "投诉" in query
    )

    has_time_intent = any(
        token in query
        for token in (
            "多久",
            "回复",
            "响应",
            "首响",
            "时效",
            "多长时间",
        )
    )

    if not (
        has_complaint_intent
        and has_time_intent
    ):
        return None

    # 已明确等级，不需要本规则澄清。
    if any(
        level in query.upper()
        for level in (
            "P1",
            "P2",
            "P3",
        )
    ):
        return None

    # 这些信息在冻结 SOP 中可以明确映射到
    # 某个投诉等级，因此也不要强制澄清。
    explicit_issue_signals = (
        # P1
        "数据泄露",
        "重大服务中断",
        "舆情升级",
        "大客户高层投诉",

        # P2
        "核心功能受阻",
        "重复故障",
        "退款",
        "解约",

        # P3
        "一般体验问题",
        "单点功能异常",
        "服务态度投诉",
    )

    if any(
        signal in query
        for signal in explicit_issue_signals
    ):
        return None

    evidence_text = (
        _join_evidence_text(
            evidence
        )
    )

    has_multi_level_rule = all(
        marker in evidence_text
        for marker in (
            "等级：P1",
            "等级：P2",
            "等级：P3",
        )
    )

    has_different_response_times = (
        "首次响应" in evidence_text
        and "15分钟" in evidence_text
        and "30分钟" in evidence_text
        and "2小时" in evidence_text
    )

    if not (
        has_multi_level_rule
        and has_different_response_times
    ):
        return None

    evidence_ids = (
        _evidence_ids_matching(
            evidence,
            [
                "等级：P1",
                "等级：P2",
                "等级：P3",
                "首次响应",
            ],
        )
    )

    return EvidenceDecision(
        decision="clarify",
        reason=(
            "当前有效证据显示，不同投诉等级"
            "对应不同首次响应时效，而用户没有"
            "提供投诉等级或足以唯一确定等级的"
            "问题严重程度，因此不能选择唯一口径。"
        ),
        clarifying_question=(
            "请补充投诉等级（P1/P2/P3），"
            "或说明具体投诉事项和严重程度。"
        ),
        evidence_ids=evidence_ids,
        risk_flags=[],
    )


def apply_frozen_clarify_guard(
    query: str,
    domain: str,
    evidence: list[RetrievalCandidate],
) -> EvidenceDecision | None:
    """
    只迁移已经在 Frozen POC 中确认的
    necessary-condition clarify 规则。

    返回 None：
        没有命中结构化规则，
        继续交给原 Frozen Evidence Judge。

    返回 EvidenceDecision：
        命中冻结的确定性规则，
        直接使用该状态。
    """

    if domain == "HR":
        return _hr_trial_period_guard(
            query=query,
            evidence=evidence,
        )

    if domain == "Service":
        return _service_response_time_guard(
            query=query,
            evidence=evidence,
        )

    if domain == "Product":
        return _product_refund_scope_guard(
            query=query,
            evidence=evidence,
        )

    return None

def _product_refund_scope_guard(
    query: str,
    evidence: list[RetrievalCandidate],
) -> EvidenceDecision | None:
    """
    Frozen Product refund clarify rule.

    只处理真正缺少必要范围信息的
    泛化退款流程问题。

    必须避免 Product P-FIX 回退：

    - 产品A退款规则是多少天？
      → answer

    - 产品A付款15天后还能无理由退款吗？
      → answer

    - 产品A付款10天、核心功能用了2次，
      可以退款吗？
      → answer

    只有类似：

    - 产品A怎么退款？
    - 产品A退款怎么办？
    - 产品A如何申请退款？

    且 Evidence 明确显示不同产品类型
    适用不同规则时，才 clarify。
    """

    text = (
        query
        .replace(" ", "")
    )

    # ============================================================
    # 必须明确是 Product A Refund
    # ============================================================
    if (
        "产品A" not in text
        or "退款" not in text
    ):
        return None

    # ============================================================
    # 1. 已经在直接询问某条规则 / 条件
    #
    # 这些问题应该由 Evidence Judge
    # 根据真实退款规则判断，
    # 不能过度 clarify。
    # ============================================================
    direct_rule_terms = (
        "多少天",
        "几天",
        "期限",
        "规则",
        "条件",
        "能退款",
        "可以退款",
        "还能退款",
        "还能无理由退款",
        "无理由退款",
        "退款资格",
    )

    if any(
        term in text
        for term in direct_rule_terms
    ):
        return None

    # ============================================================
    # 2. 用户已经提供退款资格事实
    #
    # P002 / P302:
    #   付款15天后
    #
    # P-FIX:
    #   付款10天 + 使用2次
    #
    # 都不应该 clarify。
    # ============================================================
    eligibility_terms = (
        "付款",
        "支付",
        "用了",
        "使用",
        "核心功能",
        "核心付费功能",
        "使用次数",
    )

    if any(
        term in text
        for term in eligibility_terms
    ):
        return None

    # ============================================================
    # 3. 用户已经明确 Product Scope
    # ============================================================
    explicit_scope_terms = (
        "标准版",
        "月度订阅",
        "年度订阅",
        "企业定制",
        "定制合同",
    )

    if any(
        term in text
        for term in explicit_scope_terms
    ):
        return None

    # ============================================================
    # 4. 只有真正泛化的退款流程问题才可能 clarify
    # ============================================================
    vague_refund_terms = (
        "怎么退款",
        "如何退款",
        "退款怎么办",
        "怎么退",
        "如何申请退款",
        "怎么申请退款",
    )

    if not any(
        term in text
        for term in vague_refund_terms
    ):
        return None

    # ============================================================
    # 5. Evidence 必须真的证明存在 Scope 差异
    #
    # 不能只根据 Query 凭空 clarify。
    # ============================================================
    evidence_text = "\n".join(
        item.text
        for item in evidence
    )

    has_standard_scope = (
        "标准版" in evidence_text
        or "月度" in evidence_text
        or "年度" in evidence_text
    )

    has_custom_scope = (
        "企业定制" in evidence_text
        or "定制合同" in evidence_text
        or "合同条款" in evidence_text
    )

    if not (
        has_standard_scope
        and has_custom_scope
    ):
        return None

    # ============================================================
    # 6. Citation Evidence
    # ============================================================
    evidence_ids = []

    for item in evidence:

        section = (
            item.section
            or ""
        )

        if (
            "适用产品" in section
            or "退款规则" in section
        ):

            if (
                item.chunk_id
                not in evidence_ids
            ):
                evidence_ids.append(
                    item.chunk_id
                )

    return EvidenceDecision(
        decision="clarify",

        reason=(
            "当前企业知识显示，产品A"
            "标准订阅与企业定制合同"
            "适用的退款规则不同，"
            "而当前问题尚未说明"
            "具体产品类型。"
        ),

        clarifying_question=(
            "请确认您使用的是产品A标准版"
            "月度/年度订阅，还是企业定制合同？"
        ),

        evidence_ids=(
            evidence_ids
        ),

        risk_flags=[],
    )