from fastapi import APIRouter

from app.core.permission_filter import (
    check_route_permission,
)
from app.core.query_time_resolver import (
    resolve_query_time,
)
from app.core.router_service import (
    route_query,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)


router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):
    """
    KnowFlow 当前阶段问答入口。

    当前执行链路：

    1. S3 Router
       - Domain
       - Finance Sensitivity
       - Version Mode

    2. S4 Permission
       - Finance Restricted 权限检查
       - no_access 时立即终止

    3. S5 Query Time Resolver
       - exact_date
       - period
       - request_time
       - comparison

    当前尚未执行：
    - S5 Document Version Filter
    - S6 Hybrid Retrieval
    - S7 Evidence Judge
    - Answer Generation
    - Citation Assembler
    """

    # ==================================================
    # S3: Router
    # ==================================================
    routing = route_query(
        request.query
    )

    # ==================================================
    # S4: Permission Check
    # ==================================================
    permission = check_route_permission(
        routing=routing,
        user=request.user,
    )

    # --------------------------------------------------
    # 权限不足：立即结束
    #
    # 注意：
    # no_access 属于 Permission Layer，
    # 不进入后续 Version / Retrieval / LLM。
    # --------------------------------------------------
    if permission.decision == "no_access":
        return ChatResponse(
            status="no_access",
            query=request.query,
            domain=routing["domain"],
            sensitivity=routing[
                "sensitivity"
            ],
            version_mode=routing[
                "version_mode"
            ],
            permission_decision=(
                "no_access"
            ),
            query_date=None,
            time_selector=None,
            period_start=None,
            period_end=None,
            message=(
                "存在可能相关的受限知识，"
                "但当前账户没有对应访问权限。"
            ),
        )

    # ==================================================
    # S5: Query Time Resolver
    # ==================================================
    time_context = None

    if routing["version_mode"] is not None:
        time_context = resolve_query_time(
            query=request.query,
            version_mode=routing[
                "version_mode"
            ],
        )

    # ==================================================
    # 将时间上下文转换成 API 可返回格式
    # ==================================================

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

    # ==================================================
    # 当前阶段正常返回
    #
    # 注意：
    # 这里仍然没有真正检索知识库，
    # 所以不能回答用户的企业知识问题。
    # ==================================================
    return ChatResponse(
        status="version_context_resolved",
        query=request.query,
        domain=routing["domain"],
        sensitivity=routing[
            "sensitivity"
        ],
        version_mode=routing[
            "version_mode"
        ],
        permission_decision="allowed",
        query_date=query_date,
        time_selector=time_selector,
        period_start=period_start,
        period_end=period_end,
        message=(
            "S5 query time resolved. "
            "Document Version Filter, "
            "Hybrid Retrieval and "
            "Evidence Judge are not "
            "executed yet."
        ),
    )