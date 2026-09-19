from fastapi import APIRouter

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

    # =================================
    # S3 Router
    # =================================
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

    # =================================
    # Frozen Other branch
    # =================================
    if domain == "Other":

        return ChatResponse(
            status="out_of_scope",
            query=request.query,
            domain=domain,
            sensitivity=sensitivity,
            version_mode=version_mode,
            permission_decision="allowed",
            message=(
                "Query is outside the "
                "supported enterprise "
                "knowledge domains. "
                "Evidence Judge is not "
                "executed yet."
            ),
        )

    # =================================
    # S4 + S5 Scope
    # =================================
    scope = build_retrieval_scope(
        query=request.query,
        routing=routing,
        user=request.user,
    )

    # =================================
    # no_access 必须在 Retrieval 前返回
    # =================================
    if (
        scope[
            "permission_decision"
        ]
        == "no_access"
    ):

        return ChatResponse(
            status="no_access",
            query=request.query,
            domain=domain,
            sensitivity=sensitivity,
            version_mode=version_mode,
            permission_decision=(
                "no_access"
            ),
            message=(
                "存在可能相关的受限知识，"
                "但当前账户没有对应访问权限。"
            ),
        )

    allowed_document_ids = (
        scope[
            "allowed_document_ids"
        ]
    )

    # =================================
    # 只加载 S4/S5 允许的 Chunk
    # =================================
    allowed_chunks = (
        load_chunks_by_document_ids(
            allowed_document_ids
        )
    )

    # =================================
    # S6 Hybrid Retrieval
    # =================================
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
        for item in (
            retrieval.reranked_candidates
        )
    ]

    time_context = scope[
        "time_context"
    ]

    query_date = None
    time_selector = None
    period_start = None
    period_end = None

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

    return ChatResponse(
        status="retrieval_complete",
        query=request.query,
        domain=domain,
        sensitivity=sensitivity,
        version_mode=version_mode,
        permission_decision=(
            "allowed"
        ),
        message=(
            "S6 hybrid retrieval complete. "
            "Evidence Judge and Answer "
            "Generator are not executed yet."
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