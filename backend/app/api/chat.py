import time
import uuid

from fastapi import APIRouter

from app.core.evidence_state_machine import (
    decide_evidence_state,
)
from app.core.response_assembler import (
    assemble_citations,
)
from app.core.retrieval_scope import (
    build_retrieval_scope,
)
from app.core.router_service import (
    route_query,
)
from app.db.trace_repository import (
    save_trace,
)
from app.db.vector_store import (
    load_chunks_by_document_ids,
)
from app.models import (
    TraceRecord,
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


# ================================================================
# S8 Trace Helpers
# ================================================================
def _new_trace_id() -> str:

    return (
        "TR-"
        + uuid.uuid4().hex.upper()
    )


def _elapsed_ms(
    started_at: float,
) -> int:

    value = int(
        (
            time.perf_counter()
            - started_at
        )
        * 1000
    )

    # 极短路径也至少记为 1ms，
    # 避免 Trace 中出现不可读的 0ms。
    return max(
        1,
        value,
    )


def _json_safe(
    value,
):
    """
    把 numpy scalar 等对象转换为
    PostgreSQL JSONB 可安全序列化的类型。
    """

    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if isinstance(
        value,
        dict,
    ):
        return {
            str(key):
                _json_safe(item)
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):
        return [
            _json_safe(item)
            for item in value
        ]

    # numpy scalar 通常支持 .item()
    if hasattr(
        value,
        "item",
    ):
        try:
            return _json_safe(
                value.item()
            )
        except Exception:
            pass

    return str(value)


def _extract_time_context(
    scope: dict,
):

    time_context = scope.get(
        "time_context"
    )

    query_date = None
    trace_query_date = None

    time_selector = None
    period_start = None
    period_end = None

    query_time_summary = ""

    if time_context is None:

        return (
            query_date,
            trace_query_date,
            time_selector,
            period_start,
            period_end,
            query_time_summary,
        )

    time_selector = (
        time_context.selector
    )

    if (
        time_context.query_date
        is not None
    ):
        trace_query_date = (
            time_context.query_date
        )

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

    query_time_summary = (
        f"selector={time_selector}; "
        f"query_date={query_date}; "
        f"period_start={period_start}; "
        f"period_end={period_end}"
    )

    return (
        query_date,
        trace_query_date,
        time_selector,
        period_start,
        period_end,
        query_time_summary,
    )


def _build_retrieved_chunks(
    candidates,
) -> list[dict]:

    return [
        {
            "chunk_id":
                item.chunk_id,

            "document_id":
                item.document_id,

            "page":
                item.page,

            "section":
                item.section,

            "retrieval_source":
                item.retrieval_source,

            "raw_score":
                _json_safe(
                    item.raw_score
                ),

            "fused_score":
                _json_safe(
                    item.fused_score
                ),

            "rerank_score":
                _json_safe(
                    item.rerank_score
                ),
        }

        for item in candidates
    ]


def _build_rerank_scores(
    candidates,
) -> list[dict]:

    return [
        {
            "chunk_id":
                item.chunk_id,

            "score":
                _json_safe(
                    item.rerank_score
                ),
        }

        for item in candidates
    ]


# ================================================================
# /chat
# ================================================================
@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
):

    # ============================================================
    # S8 Trace 从请求进入的第一刻开始计时
    # ============================================================
    started_at = (
        time.perf_counter()
    )

    trace_id = (
        _new_trace_id()
    )

    # ============================================================
    # S3 Router
    # ============================================================
    routing = route_query(
        request.query
    )

    domain = routing[
        "domain"
    ]

    sensitivity = routing.get(
        "sensitivity"
    )

    version_mode = routing.get(
        "version_mode"
    )

    # ============================================================
    # Frozen Other Branch
    #
    # S8 要求：
    # Other 即使不进行 Retrieval，
    # 也必须生成 Trace。
    # ============================================================
    if domain == "Other":

        reason = (
            "当前问题不属于本企业知识库"
            "能够支持的业务知识范围，"
            "没有可靠的企业知识证据"
            "可以用于回答。"
        )

        latency_ms = (
            _elapsed_ms(
                started_at
            )
        )

        trace = TraceRecord(
            trace_id=trace_id,

            query=request.query,

            user_id=(
                request.user.user_id
            ),

            domain=domain,

            sensitivity=sensitivity,

            version_mode=version_mode,

            query_date=None,

            permission_filter={
                "permission_decision":
                    "not_applicable",
                "reason":
                    "domain_other",
            },

            version_filter={
                "version_mode":
                    version_mode,
                "time_selector":
                    None,
            },

            retrieved_chunks=[],

            rerank_scores=[],

            decision="refuse",

            decision_reason=reason,

            clarifying_question="",

            evidence_ids=[],

            citations=[],

            latency_ms=latency_ms,

            input_tokens=0,

            output_tokens=0,

            prompt_version=(
                "baseline-v1"
            ),
        )

        save_trace(
            trace
        )

        return ChatResponse(
            status="out_of_scope",

            trace_id=trace_id,

            query=request.query,

            domain=domain,

            sensitivity=sensitivity,

            version_mode=version_mode,

            permission_decision=(
                "allowed"
            ),

            decision="refuse",

            reason=reason,

            clarifying_question="",

            evidence_ids=[],

            risk_flags=[],

            citation_ids=[],

            citations=[],

            message=(
                "Query is outside the "
                "supported enterprise "
                "knowledge domains. "
                "S8 trace recorded. "
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
    # S5 Time Context
    #
    # 提前提取，是为了 no_access Trace
    # 也能够记录请求时间语义，
    # 但不记录任何受限 Document / Chunk。
    # ============================================================
    (
        query_date,
        trace_query_date,
        time_selector,
        period_start,
        period_end,
        query_time_summary,
    ) = _extract_time_context(
        scope
    )

    # ============================================================
    # S4 no_access
    #
    # 必须在 Retrieval 之前直接返回。
    #
    # S8 Trace 同样不得让 Private Chunk
    # 为了“记录 Trace”而重新进入系统。
    # ============================================================
    if (
        permission_decision
        == "no_access"
    ):

        reason = (
            "当前身份没有访问相关"
            "受限企业知识的权限。"
        )

        latency_ms = (
            _elapsed_ms(
                started_at
            )
        )

        trace = TraceRecord(
            trace_id=trace_id,

            query=request.query,

            user_id=(
                request.user.user_id
            ),

            domain=domain,

            sensitivity=sensitivity,

            version_mode=version_mode,

            query_date=(
                trace_query_date
            ),

            permission_filter={
                "permission_decision":
                    "no_access",

                "department":
                    request.user.department,

                "role":
                    request.user.role,
            },

            # 注意：
            # no_access Trace 不保存
            # private document ids。
            version_filter={
                "version_mode":
                    version_mode,

                "time_selector":
                    time_selector,

                "query_date":
                    query_date,

                "period_start":
                    period_start,

                "period_end":
                    period_end,
            },

            retrieved_chunks=[],

            rerank_scores=[],

            decision="no_access",

            decision_reason=reason,

            clarifying_question="",

            evidence_ids=[],

            citations=[],

            latency_ms=latency_ms,

            input_tokens=0,

            output_tokens=0,

            prompt_version=(
                "baseline-v1"
            ),
        )

        save_trace(
            trace
        )

        return ChatResponse(
            status="no_access",

            trace_id=trace_id,

            query=request.query,

            domain=domain,

            sensitivity=sensitivity,

            version_mode=version_mode,

            permission_decision=(
                "no_access"
            ),

            decision="no_access",

            reason=reason,

            clarifying_question="",

            evidence_ids=[],

            risk_flags=[],

            citation_ids=[],

            citations=[],

            message=(
                "存在可能相关的受限知识，"
                "但当前账户没有对应访问权限。"
            ),

            query_date=query_date,

            time_selector=time_selector,

            period_start=period_start,

            period_end=period_end,

            current_document_ids=[],

            historical_document_ids=[],

            allowed_document_ids=[],

            evidence_count=0,

            evidence=[],
        )

    # ============================================================
    # S5 Permission + Version 最终允许进入 S6 的 Documents
    # ============================================================
    allowed_document_ids = list(
        scope[
            "allowed_document_ids"
        ]
    )

    current_document_ids = list(
        scope[
            "current_document_ids"
        ]
    )

    historical_document_ids = list(
        scope[
            "historical_document_ids"
        ]
    )

    # ============================================================
    # S6 只加载 S4 / S5 已允许的 Chunk
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
    # BGE Reranker
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

    retrieval_candidates = list(
        retrieval
        .reranked_candidates
    )

    # ============================================================
    # S6 Swagger Evidence Debug
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
    # S7 Evidence State Machine
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

            current_document_ids=(
                current_document_ids
            ),

            historical_document_ids=(
                historical_document_ids
            ),

            query_time_summary=(
                query_time_summary
            ),
        )
    )

    # ============================================================
    # S8 Citation Assembler
    #
    # 注意：
    # Citation 只允许从 S7 最终 evidence_ids
    # 映射。
    #
    # 不允许 LLM 自己编文件名、版本、页码。
    # ============================================================
    citations = assemble_citations(
        trace_id=trace_id,

        evidence_ids=(
            decision_result
            .evidence_ids
        ),
    )

    citation_ids = [
        item.citation_id
        for item in citations
    ]

    # ============================================================
    # S8 Trace Retrieval Data
    # ============================================================
    retrieved_chunks = (
        _build_retrieved_chunks(
            retrieval_candidates
        )
    )

    rerank_scores = (
        _build_rerank_scores(
            retrieval_candidates
        )
    )

    # ============================================================
    # S8 Token Usage
    #
    # Structured Guard:
    #   0 / 0
    #
    # LLM Judge:
    #   使用 evidence_judge.py
    #   返回的真实 usage。
    # ============================================================
    input_tokens = int(
        getattr(
            decision_result,
            "input_tokens",
            0,
        )
        or 0
    )

    output_tokens = int(
        getattr(
            decision_result,
            "output_tokens",
            0,
        )
        or 0
    )

    prompt_version = (
        getattr(
            decision_result,
            "prompt_version",
            "baseline-v1",
        )
        or "baseline-v1"
    )

    # ============================================================
    # S8 Trace
    # ============================================================
    latency_ms = (
        _elapsed_ms(
            started_at
        )
    )

    trace = TraceRecord(
        trace_id=trace_id,

        query=request.query,

        user_id=(
            request.user.user_id
        ),

        domain=domain,

        sensitivity=sensitivity,

        version_mode=version_mode,

        query_date=(
            trace_query_date
        ),

        # --------------------------------------------------------
        # S4 Permission Trace
        # --------------------------------------------------------
        permission_filter={
            "permission_decision":
                permission_decision,

            "department":
                request.user.department,

            "role":
                request.user.role,

            "authorized_kb_ids":
                list(
                    request
                    .user
                    .authorized_kb_ids
                    or []
                ),
        },

        # --------------------------------------------------------
        # S5 Version Trace
        # --------------------------------------------------------
        version_filter={
            "version_mode":
                version_mode,

            "time_selector":
                time_selector,

            "query_date":
                query_date,

            "period_start":
                period_start,

            "period_end":
                period_end,

            "current_document_ids":
                current_document_ids,

            "historical_document_ids":
                historical_document_ids,

            "allowed_document_ids":
                allowed_document_ids,
        },

        # --------------------------------------------------------
        # S6 Retrieval Trace
        # --------------------------------------------------------
        retrieved_chunks=(
            retrieved_chunks
        ),

        rerank_scores=(
            rerank_scores
        ),

        # --------------------------------------------------------
        # S7 Decision Trace
        # --------------------------------------------------------
        decision=(
            decision_result
            .decision
        ),

        decision_reason=(
            decision_result
            .reason
        ),

        clarifying_question=(
            decision_result
            .clarifying_question
        ),

        evidence_ids=list(
            decision_result
            .evidence_ids
        ),

        # --------------------------------------------------------
        # S8 Citation Trace
        # --------------------------------------------------------
        citations=(
            citations
        ),

        latency_ms=latency_ms,

        input_tokens=(
            input_tokens
        ),

        output_tokens=(
            output_tokens
        ),

        prompt_version=(
            prompt_version
        ),
    )

    # ============================================================
    # Trace 持久化
    #
    # S8 阶段 Trace 是正式交付物，
    # 因此存储失败时不要静默吞掉异常。
    # ============================================================
    save_trace(
        trace
    )

    # ============================================================
    # S8 Response
    #
    # 注意：
    # 仍然没有最终 Answer Generator。
    # S8 只增加：
    #
    # trace_id
    # citation_ids
    # citations
    # ============================================================
    return ChatResponse(
        status="decision_complete",

        trace_id=trace_id,

        query=request.query,

        domain=domain,

        sensitivity=sensitivity,

        version_mode=version_mode,

        permission_decision=(
            permission_decision
        ),

        decision=(
            decision_result
            .decision
        ),

        reason=(
            decision_result
            .reason
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

        citation_ids=(
            citation_ids
        ),

        citations=(
            citations
        ),

        message=(
            "S8 Citation & Trace "
            "completed. "
            "Final Answer Generator "
            "is not executed yet."
        ),

        query_date=query_date,

        time_selector=time_selector,

        period_start=period_start,

        period_end=period_end,

        current_document_ids=(
            current_document_ids
        ),

        historical_document_ids=(
            historical_document_ids
        ),

        allowed_document_ids=(
            allowed_document_ids
        ),

        evidence_count=len(
            evidence
        ),

        evidence=evidence,
    )