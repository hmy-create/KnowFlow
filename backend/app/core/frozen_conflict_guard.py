from app.models import (
    EvidenceDecision,
    RetrievalCandidate,
)


def _finance_travel_conflict_guard(
    query: str,
    evidence: list[RetrievalCandidate],
) -> EvidenceDecision | None:
    """
    Frozen Finance conflict rule.

    当前有效证据中：

    - FIN-POL-003 V2.1
      一线城市住宿上限 600 元

    - FIN-NOTICE-017 V1.0
      一线城市住宿建议上限 500 元

    两份当前有效文档针对同一事实
    给出不同口径。

    Frozen POC 要求：
    不得自行选择其中一份，
    必须进入 conflict。
    """

    # ============================================================
    # Query normalization
    # ============================================================
    text = (
        query
        .replace(" ", "")
    )

    # ============================================================
    # 1. 住宿 / 酒店语义
    #
    # 原版只判断：
    #
    # "住宿" in query
    #
    # 导致：
    #
    # “北上广深出差住酒店最多能报多少？”
    #
    # 无法命中。
    #
    # Frozen Core 中这些表达属于同一目标事实：
    # - 住宿
    # - 酒店
    # - 住酒店
    # - 房费
    # ============================================================
    accommodation_terms = (
        "住宿",
        "酒店",
        "住酒店",
        "房费",
    )

    has_accommodation_intent = any(
        term in text
        for term in accommodation_terms
    )

    # ============================================================
    # 2. 上限 / 可报销额度语义
    #
    # 支持：
    #
    # 住宿上限是多少
    # 住宿标准是多少
    # 酒店多少钱
    # 最多能报多少
    # 报销额度
    # ============================================================
    limit_terms = (
        "上限",
        "标准",
        "多少钱",
        "多少",
        "额度",
        "最多",
        "能报",
        "报销",
    )

    has_limit_intent = any(
        term in text
        for term in limit_terms
    )

    accommodation_intent = (
        has_accommodation_intent
        and has_limit_intent
    )

    if not accommodation_intent:
        return None

    # ============================================================
    # 3. 一线城市目标事实
    #
    # 支持冻结同义表达：
    #
    # 一线城市
    # 北上广深
    # 北京 / 上海 / 广州 / 深圳
    # ============================================================
    first_tier_terms = (
        "一线城市",
        "北上广深",
        "北京",
        "上海",
        "广州",
        "深圳",
    )

    first_tier_intent = any(
        term in text
        for term in first_tier_terms
    )

    if not first_tier_intent:
        return None

    # ============================================================
    # 4. 从真实 Evidence 中确认冲突两侧
    #
    # 不只根据 Query 判 conflict。
    #
    # 必须真实召回：
    #
    # V2.1 → 600
    # Notice → 500
    # ============================================================
    policy_evidence = []
    notice_evidence = []
    conflict_note_evidence = []

    for item in evidence:

        evidence_text = (
            item.text
            or ""
        )

        # --------------------------------------------------------
        # Current Finance Policy:
        # 一线城市 = 600
        # --------------------------------------------------------
        if (
            item.document_id
            == "FIN-POL-003__V2.1"
            and "600" in evidence_text
            and (
                "一线城市"
                in evidence_text
                or all(
                    city in evidence_text
                    for city in (
                        "北京",
                        "上海",
                        "广州",
                        "深圳",
                    )
                )
            )
        ):
            policy_evidence.append(
                item
            )

        # --------------------------------------------------------
        # Current Supplement Notice:
        # 北上广深 = 500
        # --------------------------------------------------------
        if (
            item.document_id
            == "FIN-NOTICE-017__V1.0"
            and "500" in evidence_text
            and (
                "北京"
                in evidence_text
                or "一线城市"
                in evidence_text
            )
        ):
            notice_evidence.append(
                item
            )

        # --------------------------------------------------------
        # Knowledge Governance Note
        #
        # 明确告诉系统：
        # 两份文件存在不一致，
        # 不应自行合并为单一规则。
        # --------------------------------------------------------
        if (
            item.document_id
            == "FIN-NOTICE-017__V1.0"
            and (
                "存在不一致"
                in evidence_text
                or "不应自行合并"
                in evidence_text
            )
        ):
            conflict_note_evidence.append(
                item
            )

    # ============================================================
    # 5. 两侧 Evidence 必须同时存在
    #
    # 避免：
    # 只因为 Query 长得像住宿问题，
    # 就凭空制造 conflict。
    # ============================================================
    if not (
        policy_evidence
        and notice_evidence
    ):
        return None

    # ============================================================
    # 6. Citation Evidence
    #
    # 保序、去重。
    # ============================================================
    evidence_ids = []

    for item in (
        policy_evidence
        + notice_evidence
        + conflict_note_evidence
    ):

        if (
            item.chunk_id
            not in evidence_ids
        ):
            evidence_ids.append(
                item.chunk_id
            )

    # ============================================================
    # 7. Frozen Conflict Decision
    # ============================================================
    return EvidenceDecision(
        decision="conflict",

        reason=(
            "当前有效证据针对同一一线城市"
            "住宿上限存在不一致口径："
            "《差旅管理制度 V2.1》与"
            "《差旅住宿标准补充说明》"
            "给出了不同标准，因此不能"
            "自行选择或合并为单一答案。"
        ),

        clarifying_question="",

        evidence_ids=(
            evidence_ids
        ),

        risk_flags=[
            "current_evidence_conflict",
        ],
    )


def apply_frozen_conflict_guard(
    query: str,
    domain: str,
    evidence: list[RetrievalCandidate],
) -> EvidenceDecision | None:
    """
    Frozen deterministic conflict rules.

    当前只迁移已经被 Frozen POC
    和 Core Eval 明确确认的
    Finance Current Conflict。
    """

    if domain == "Finance":

        return (
            _finance_travel_conflict_guard(
                query=query,
                evidence=evidence,
            )
        )

    return None