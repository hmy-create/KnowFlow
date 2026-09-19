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
      一线城市住宿上限 600
    - FIN-NOTICE-017 V1.0
      一线城市住宿建议上限 500

    两份文档在当前时间同时有效，
    且针对同一事实给出不同口径，
    按冻结 POC 必须 conflict。
    """

    # 只处理住宿标准相关问题
    accommodation_intent = (
        "住宿" in query
        and any(
            token in query
            for token in (
                "上限",
                "标准",
                "多少钱",
                "多少",
                "额度",
            )
        )
    )

    if not accommodation_intent:
        return None

    # 必须指向一线城市这一目标事实
    first_tier_intent = any(
        token in query
        for token in (
            "一线城市",
            "北京",
            "上海",
            "广州",
            "深圳",
        )
    )

    if not first_tier_intent:
        return None

    policy_evidence = []
    notice_evidence = []
    conflict_note_evidence = []

    for item in evidence:

        text = item.text

        if (
            item.document_id
            == "FIN-POL-003__V2.1"
            and "600" in text
            and (
                "一线城市" in text
                or all(
                    city in text
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

        if (
            item.document_id
            == "FIN-NOTICE-017__V1.0"
            and "500" in text
            and (
                "北京" in text
                or "一线城市" in text
            )
        ):
            notice_evidence.append(
                item
            )

        if (
            item.document_id
            == "FIN-NOTICE-017__V1.0"
            and (
                "存在不一致" in text
                or "不应自行合并" in text
            )
        ):
            conflict_note_evidence.append(
                item
            )

    # 必须两边证据同时存在
    if not (
        policy_evidence
        and notice_evidence
    ):
        return None

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
        evidence_ids=evidence_ids,
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
    只迁移 Frozen POC 中已确认的
    deterministic conflict rule。
    """

    if domain == "Finance":
        return (
            _finance_travel_conflict_guard(
                query=query,
                evidence=evidence,
            )
        )

    return None