from app.core.evidence_judge import (
    judge_current_evidence,
)
from app.core.frozen_clarify_guard import (
    apply_frozen_clarify_guard,
)
from app.core.frozen_conflict_guard import (
    apply_frozen_conflict_guard,
)
from app.core.frozen_refuse_guard import (
    apply_frozen_refuse_guard,
)
from app.models import (
    EvidenceDecision,
    RetrievalCandidate,
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

    # ============================================================
    # S4 Permission Layer
    #
    # no_access 只能由权限层产生。
    #
    # 一旦 no_access：
    # - 不进入 Evidence Judge
    # - 不引用任何 Evidence
    # ============================================================
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

    # ============================================================
    # Other
    #
    # Frozen POC：
    # 企业知识库范围外问题直接 refuse。
    # ============================================================
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

    # ============================================================
    # No Evidence
    #
    # 没有企业知识证据时不能生成答案。
    # ============================================================
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

    # ============================================================
    # Finance Restricted
    #
    # Frozen POC：
    #
    # Finance
    # → Restricted
    # → Role / Permission Check
    #
    # 权限已经通过，而且已经有 Private Evidence，
    # 才允许 answer。
    #
    # no_access 已经在函数最前面被拦截。
    # ============================================================
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

    # ============================================================
    # Historical
    #
    # Frozen POC：
    #
    # Version Resolver + S5 已经完成
    # query_date / effective_at /
    # expired_at / status 过滤。
    #
    # Historical 有有效 Evidence 时
    # 直接进入历史回答状态。
    # ============================================================
    if (
        version_mode
        == "Historical"
    ):

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

    # ============================================================
    # Comparison
    #
    # Frozen POC：
    # 必须同时具备 Current + Historical Evidence。
    # ============================================================
    if (
        version_mode
        == "Comparison"
    ):

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

    # ============================================================
    # Current Evidence State
    #
    # 当前顺序：
    #
    # 1. Unsupported Future Plan Refuse Guard
    # 2. Conflict Guard
    # 3. Clarify Guard
    # 4. Frozen LLM Evidence Judge
    #
    # 这些 Guard 都只迁移冻结 POC
    # 已经明确的确定性业务边界。
    # ============================================================

    # ============================================================
    # 1. Current deterministic refuse rules
    #
    # 用于：
    # - 今年会不会涨薪
    # - 明年会不会涨价 / 降价
    # - 客服是否增加夜班
    # - 年终奖未来安排
    #
    # 前提：
    # 当前 Evidence 本身没有直接支持
    # 对应未来计划。
    # ============================================================
    refuse_decision = (
        apply_frozen_refuse_guard(
            query=query,
            domain=domain,
            evidence=evidence,
        )
    )

    if (
        refuse_decision
        is not None
    ):
        return refuse_decision

    # ============================================================
    # 2. Current deterministic conflict rules
    #
    # 例如：
    # 当前 Finance 一线城市住宿标准
    # 同时存在 600 / 500 两个有效口径。
    # ============================================================
    conflict_decision = (
        apply_frozen_conflict_guard(
            query=query,
            domain=domain,
            evidence=evidence,
        )
    )

    if (
        conflict_decision
        is not None
    ):
        return conflict_decision

    # ============================================================
    # 3. Current deterministic clarify rules
    #
    # 例如：
    # HR 试用期缺员工类型
    # Service 投诉时效缺投诉等级
    # ============================================================
    clarify_decision = (
        apply_frozen_clarify_guard(
            query=query,
            domain=domain,
            evidence=evidence,
        )
    )

    if (
        clarify_decision
        is not None
    ):
        return clarify_decision

    # ============================================================
    # 4. Other Current cases
    #
    # 其余无法被确定性规则安全判断的
    # Current Case，
    # 继续使用 Frozen LLM Evidence Judge。
    # ============================================================
    return judge_current_evidence(
        query=query,
        domain=domain,
        evidence=evidence,
        query_time_summary=(
            query_time_summary
        ),
    )