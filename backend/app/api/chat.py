from fastapi import APIRouter

from app.core.permission_filter import (
    check_route_permission,
)
from app.core.router_service import route_query
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

    routing = route_query(request.query)

    permission = check_route_permission(
        routing=routing,
        user=request.user,
    )

    if permission.decision == "no_access":
        return ChatResponse(
            status="no_access",
            query=request.query,
            domain=routing["domain"],
            sensitivity=routing["sensitivity"],
            version_mode=routing["version_mode"],
            permission_decision="no_access",
            message=(
                "存在可能相关的受限知识，"
                "但当前账户没有对应访问权限。"
            ),
        )

    return ChatResponse(
        status="permission_passed",
        query=request.query,
        domain=routing["domain"],
        sensitivity=routing["sensitivity"],
        version_mode=routing["version_mode"],
        permission_decision="allowed",
        message=(
            "S4 permission check passed. "
            "Version Filter, Retrieval and "
            "Evidence Judge are not executed yet."
        ),
    )