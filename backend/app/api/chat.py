from fastapi import APIRouter

from app.core.evidence_state_machine import (
    decide_evidence_state,
)
from app.core.retrieval_scope import (
    build_retrieval_scope,
)
from app.core.router_service import (
    route_query,
)
from app.db.vector_store import (
    load_chunks_by_document_ids,
)
from app.retrieval.hybrid_retriever_db import (
    hybrid_retrieve_scoped,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    EvidenceDebug,
)


router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
):

    # ============================================================
    # S3 Router
    # ============================================================
    routing = route_query(
        request.query
    )

    domain = routing["domain"]

    sensitivity = routing.get(
        "sensitivity"
    )

    version_mode = routing.get(
        "version_mode"
    )

    # ============================================================
    # Frozen Other branch
    #
    # Other 属于知识库范围外问题：
    # - 不进入 Permission / Version
    # - 不进入 Retrieval
    # - 不调用 Evidence Judge
    # - S7 decision = refuse
    # ============================================================
    if domain == "Other":

        return ChatResponse(
            status="out_of_scope",

            query=request.query,

            domain=domain,

            sensitivity=sensitivity,

            version_mode=version_mode,

            permission_decision="allowed",

            decision="refuse",

            reason=(
                "当前问题不属于本企业知识库"
                "能够支持的业务知识范围，"
                "没有可靠的企业知识证据"
                "可以用于回答。"
            ),

            clarifying_question="",

            evidence_ids=[],

            risk_flags=[],

            message=(
                "Query is outside the "
                "supported enterprise "
                "knowledge domains. "
                "S7 decision is refuse. "
                "Final Answer Generator "
                "is not executed yet."
            ),

            current_document_ids=[],

            historical_document_ids=[],

            allowed_document_ids=[],

            evidence_count=0,

            evidence=[],
        )

    # ============================================================
    # S4 Permission + S5 Version Scope
    # ============================================================
    scope = build_retrieval_scope(
        query=request.query,
        routing=routing,
        user=request.user,
    )

    permission_decision = scope[
        "permission_decision"
    ]

    # ============================================================
    # S4 no_access
    #
    # 必须在 Retrieval 之前返回。
    #
    # 重要：
    # - 不加载 private chunks
    # - 不运行 BM25
    # - 不运行 pgvector
    # - 不运行 Reranker
    # - 不调用 Evidence Judge
    # - 不泄漏文档标题、金额、审批链等内容
    # ============================================================
    if (
        permission_decision
        == "no_access"
    ):

        return ChatResponse(
            status="no_access",

            query=request.query,

            domain=domain,

            sensitivity=sensitivity,

            version_mode=version_mode,

            permission_decision="no_access",

            decision="no_access",

            reason=(
                "当前身份没有访问相关"
                "受限企业知识的权限。"
            ),

            clarifying_question="",

            evidence_ids=[],

            risk_flags=[],

            message=(
                "存在可能相关的受限知识，"
                "但当前账户没有对应访问权限。"
            ),

            current_document_ids=[],

            historical_document_ids=[],

            allowed_document_ids=[],

            evidence_count=0,

            evidence=[],
        )

    # ============================================================
    # S5 输出：
    # Permission + Version 过滤后真正允许进入检索的 Documents
    # ============================================================
    allowed_document_ids = scope[
        "allowed_document_ids"
    ]

    # ============================================================
    # 只加载 S4 / S5 允许的真实 Chunk
    #
    # 即：
    # Router
    #   ↓
    # Permission
    #   ↓
    # Version
    #   ↓
    # allowed_document_ids
    #   ↓
    # Chunk
    # ============================================================
    allowed_chunks = (
        load_chunks_by_document_ids(
            allowed_document_ids
        )
    )

    # ============================================================
    # S6 Hybrid Retrieval
    #
    # BM25 Top-N
    # +
    # pgvector Top-N
    # ↓
    # RRF
    # ↓
    # Reranker
    # ↓
    # Top-K Evidence
    # ============================================================
    retrieval = (
        hybrid_retrieve_scoped(
            query=request.query,

            allowed_chunks=(
                allowed_chunks
            ),

            allowed_document_ids=(
                allowed_document_ids
            ),

            top_n=20,

            top_k=10,
        )
    )

    # ============================================================
    # 保存真正进入 S7 的 RetrievalCandidate
    # ============================================================
    retrieval_candidates = (
        retrieval.reranked_candidates
    )

    # ============================================================
    # S6 Evidence Debug
    #
    # 这些字段继续返回给 Swagger，
    # 方便检查 Retrieval 实际召回了什么。
    # ============================================================
    evidence = [
        EvidenceDebug(
            chunk_id=item.chunk_id,

            document_id=(
                item.document_id
            ),

            text=item.text,

            page=item.page,

            section=item.section,

            retrieval_source=(
                item.retrieval_source
            ),

            raw_score=(
                item.raw_score
            ),

            fused_score=(
                item.fused_score
            ),

            rerank_score=(
                item.rerank_score
            ),
        )

        for item in retrieval_candidates
    ]

    # ============================================================
    # S5 Query Time Context
    # ============================================================
    time_context = scope[
        "time_context"
    ]

    query_date = None
    time_selector = None
    period_start = None
    period_end = None

    query_time_summary = ""

    if time_context is not None:

        time_selector = (
            time_context.selector
        )

        if (
            time_context.query_date
            is not None
        ):
            query_date = (
                time_context
                .query_date
                .isoformat()
            )

        if (
            time_context.period_start
            is not None
        ):
            period_start = (
                time_context
                .period_start
                .isoformat()
            )

        if (
            time_context.period_end
            is not None
        ):
            period_end = (
                time_context
                .period_end
                .isoformat()
            )

        # 给 S7 Evidence Judge 的时间上下文。
        #
        # 注意：
        # 真正的 Version Filter 已经在 S5 完成，
        # 这里是为了让 Judge 的 reason
        # 能理解当前时间语义。
        query_time_summary = (
            f"selector={time_selector}; "
            f"query_date={query_date}; "
            f"period_start={period_start}; "
            f"period_end={period_end}"
        )

    # ============================================================
    # S7 Evidence State Machine
    #
    # 已经完成：
    #
    # Finance deterministic conflict guard
    # HR deterministic clarify guard
    # Service deterministic clarify guard
    # Product P-FIX / 其他语义判断 -> Frozen LLM Judge
    #
    # Historical / Comparison / Restricted
    # 则继续遵守冻结 POC 分支逻辑。
    # ============================================================
    decision_result = (
        decide_evidence_state(
            query=request.query,

            domain=domain,

            sensitivity=sensitivity,

            version_mode=version_mode,

            permission_decision=(
                permission_decision
            ),

            evidence=(
                retrieval_candidates
            ),

            current_document_ids=scope[
                "current_document_ids"
            ],

            historical_document_ids=scope[
                "historical_document_ids"
            ],

            query_time_summary=(
                query_time_summary
            ),
        )
    )

    # ============================================================
    # S7 完成
    #
    # 当前仍然不生成最终业务 Answer。
    #
    # 当前接口只输出：
    #
    # decision
    # reason
    # clarifying_question
    # evidence_ids
    # risk_flags
    #
    # + S3~S6 Debug Context
    # ============================================================
    return ChatResponse(
        status="decision_complete",

        query=request.query,

        domain=domain,

        sensitivity=sensitivity,

        version_mode=version_mode,

        permission_decision=(
            permission_decision
        ),

        decision=(
            decision_result.decision
        ),

        reason=(
            decision_result.reason
        ),

        clarifying_question=(
            decision_result
            .clarifying_question
        ),

        evidence_ids=(
            decision_result
            .evidence_ids
        ),

        risk_flags=(
            decision_result
            .risk_flags
        ),

        message=(
            "S7 Evidence State Machine "
            "completed. "
            "Final Answer Generator and "
            "Citation Assembler are not "
            "executed yet."
        ),

        query_date=query_date,

        time_selector=time_selector,

        period_start=period_start,

        period_end=period_end,

        current_document_ids=scope[
            "current_document_ids"
        ],

        historical_document_ids=scope[
            "historical_document_ids"
        ],

        allowed_document_ids=(
            allowed_document_ids
        ),

        evidence_count=len(
            evidence
        ),

        evidence=evidence,
    )