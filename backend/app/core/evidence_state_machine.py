from app.core.evidence_judge import (
    judge_current_evidence,
)
from app.models import (
    EvidenceDecision,
    RetrievalCandidate,
)
from app.core.frozen_clarify_guard import (
    apply_frozen_clarify_guard,
)
from app.core.frozen_conflict_guard import (
    apply_frozen_conflict_guard,
)

def _all_evidence_ids(
    evidence: list[
        RetrievalCandidate
    ],
) -> list[str]:

    return [
        item.chunk_id
        for item in evidence
    ]


def decide_evidence_state(
    query: str,
    domain: str,
    sensitivity: str | None,
    version_mode: str | None,
    permission_decision: str,
    evidence: list[
        RetrievalCandidate
    ],
    current_document_ids: list[str],
    historical_document_ids: list[str],
    query_time_summary: str = "",
) -> EvidenceDecision:

    # =====================================
    # no_access 只属于 Permission Layer
    # =====================================
    if (
        permission_decision
        == "no_access"
    ):
        return EvidenceDecision(
            decision="no_access",
            reason=(
                "当前身份未通过受限知识"
                "访问权限校验。"
            ),
            clarifying_question="",
            evidence_ids=[],
        )

    # =====================================
    # Other
    # =====================================
    if domain == "Other":
        return EvidenceDecision(
            decision="refuse",
            reason=(
                "问题不属于当前企业"
                "知识库可支持的业务范围。"
            ),
            clarifying_question="",
            evidence_ids=[],
        )

    # =====================================
    # 没有证据
    # =====================================
    if not evidence:
        return EvidenceDecision(
            decision="refuse",
            reason=(
                "当前检索结果没有足够"
                "企业知识证据支持回答。"
            ),
            clarifying_question="",
            evidence_ids=[],
        )

    # =====================================
    # Finance Restricted
    #
    # Frozen POC:
    # ROLE CHECK
    # → PRIVATE RETRIEVAL
    # → ANSWER_FINANCE_PRIVATE
    # =====================================
    if (
        domain == "Finance"
        and sensitivity
        == "Restricted"
    ):
        return EvidenceDecision(
            decision="answer",
            reason=(
                "当前身份已通过受限知识"
                "权限校验，且已检索到"
                "对应受限企业知识。"
            ),
            clarifying_question="",
            evidence_ids=(
                _all_evidence_ids(
                    evidence
                )
            ),
        )

    # =====================================
    # Historical
    #
    # Frozen POC 直接进入历史 Answer
    # 不额外新增 Current Judge 逻辑
    # =====================================
    if version_mode == "Historical":

        return EvidenceDecision(
            decision="answer",
            reason=(
                "已按照用户历史时间范围"
                "完成版本过滤，并检索到"
                "适用的历史企业知识。"
            ),
            clarifying_question="",
            evidence_ids=(
                _all_evidence_ids(
                    evidence
                )
            ),
        )

    # =====================================
    # Product Comparison
    #
    # 冻结 POC 必须同时读取：
    # Current + Historical
    # =====================================
    if version_mode == "Comparison":

        returned_document_ids = {
            item.document_id
            for item in evidence
        }

        has_current = any(
            document_id
            in returned_document_ids
            for document_id
            in current_document_ids
        )

        has_historical = any(
            document_id
            in returned_document_ids
            for document_id
            in historical_document_ids
        )

        if (
            has_current
            and has_historical
        ):
            return EvidenceDecision(
                decision="answer",
                reason=(
                    "当前版本与历史版本"
                    "证据均已检索到，"
                    "可以进入版本比较回答。"
                ),
                clarifying_question="",
                evidence_ids=(
                    _all_evidence_ids(
                        evidence
                    )
                ),
            )

        return EvidenceDecision(
            decision="refuse",
            reason=(
                "版本比较需要同时具备"
                "当前与历史证据，"
                "当前证据不完整。"
            ),
            clarifying_question="",
            evidence_ids=(
                _all_evidence_ids(
                    evidence
                )
            ),
        )

    # =====================================
    # Current
    #
    # HR / Finance / Product / Service
    # 使用冻结 Evidence Judge
    # =====================================
    # =====================================
    # Current deterministic conflict rules
    # =====================================
    conflict_decision = (
        apply_frozen_conflict_guard(
            query=query,
            domain=domain,
            evidence=evidence,
        )
    )

    if conflict_decision is not None:
        return conflict_decision


    # =====================================
    # Current deterministic clarify rules
    # =====================================
    clarify_decision = (
        apply_frozen_clarify_guard(
            query=query,
            domain=domain,
            evidence=evidence,
        )
    )

    if clarify_decision is not None:
        return clarify_decision


    # =====================================
    # Other Current cases
    # continue Frozen LLM Evidence Judge
    # =====================================
    return judge_current_evidence(
        query=query,
        domain=domain,
        evidence=evidence,
        query_time_summary=(
            query_time_summary
        ),
    )


    # =====================================
    # 其余 Current Case
    # 继续使用 Frozen Evidence Judge
    # =====================================
    return judge_current_evidence(
        query=query,
        domain=domain,
        evidence=evidence,
        query_time_summary=(
            query_time_summary
        ),
    )