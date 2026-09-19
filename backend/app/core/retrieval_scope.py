from datetime import date

from app.core.permission_filter import (
    allowed_document,
    check_route_permission,
)
from app.core.query_time_resolver import (
    resolve_query_time,
)
from app.core.version_filter import (
    filter_documents_by_version,
)
from app.db.document_repository import (
    list_documents_by_route,
)
from app.models import User


def build_retrieval_scope(
    query: str,
    routing: dict,
    user: User,
    request_date: date | None = None,
) -> dict:
    """
    S6-C3 Retrieval Scope。

    顺序严格固定：

    Router Scope
        ↓
    Permission
        ↓
    Version
        ↓
    allowed_document_ids

    Restricted Finance 不走普通 Version Resolver，
    与 Frozen POC 保持一致。
    """

    domain = routing.get("domain")

    sensitivity = routing.get(
        "sensitivity"
    )

    version_mode = routing.get(
        "version_mode"
    )

    # ---------------------------------
    # Other 不进入企业知识检索
    # ---------------------------------
    if domain == "Other":
        return {
            "permission_decision":
                "allowed",
            "reason":
                "Query is outside supported knowledge domains.",
            "route_document_ids": [],
            "permission_document_ids": [],
            "current_document_ids": [],
            "historical_document_ids": [],
            "allowed_document_ids": [],
            "time_context": None,
            "version_result": None,
        }

    # ---------------------------------
    # Frozen Route-level Permission
    # Finance Restricted 等
    # ---------------------------------
    route_permission = (
        check_route_permission(
            routing=routing,
            user=user,
        )
    )

    if (
        route_permission.decision
        == "no_access"
    ):
        return {
            "permission_decision":
                "no_access",
            "reason":
                route_permission.reason,
            "route_document_ids": [],
            "permission_document_ids": [],
            "current_document_ids": [],
            "historical_document_ids": [],
            "allowed_document_ids": [],
            "time_context": None,
            "version_result": None,
        }

    # ---------------------------------
    # Domain / Sensitivity Scope
    # ---------------------------------
    route_documents = (
        list_documents_by_route(
            domain=domain,
            sensitivity=sensitivity,
        )
    )

    route_document_ids = [
        doc.document_id
        for doc in route_documents
    ]

    # ---------------------------------
    # Document-level Permission
    # ---------------------------------
    permission_documents = [
        doc
        for doc in route_documents
        if allowed_document(
            doc,
            user,
        )
    ]

    permission_document_ids = [
        doc.document_id
        for doc in permission_documents
    ]

    # Router 范围存在文档，但用户一份都没权限
    if (
        route_documents
        and not permission_documents
    ):
        return {
            "permission_decision":
                "no_access",
            "reason":
                "当前用户无权访问该知识范围。",
            "route_document_ids":
                route_document_ids,
            "permission_document_ids": [],
            "current_document_ids": [],
            "historical_document_ids": [],
            "allowed_document_ids": [],
            "time_context": None,
            "version_result": None,
        }

    # ---------------------------------
    # Restricted Finance
    # Frozen POC 本来没有普通 Version 分流
    # ---------------------------------
    if version_mode is None:

        return {
            "permission_decision":
                "allowed",
            "reason":
                "Permission scope passed.",
            "route_document_ids":
                route_document_ids,
            "permission_document_ids":
                permission_document_ids,
            "current_document_ids": [],
            "historical_document_ids": [],
            "allowed_document_ids":
                permission_document_ids,
            "time_context": None,
            "version_result": None,
        }

    # ---------------------------------
    # S5 Query Time Resolver
    # ---------------------------------
    time_context = resolve_query_time(
        query=query,
        version_mode=version_mode,
        request_date=request_date,
    )

    # ---------------------------------
    # S5 Version Filter
    # ---------------------------------
    version_result = (
        filter_documents_by_version(
            permission_documents,
            time_context,
        )
    )

    current_ids = list(
        version_result.current_document_ids
    )

    historical_ids = list(
        version_result.historical_document_ids
    )

    # 保序去重
    allowed_document_ids = list(
        dict.fromkeys(
            current_ids
            + historical_ids
        )
    )

    return {
        "permission_decision":
            "allowed",
        "reason":
            "Permission and version scope passed.",
        "route_document_ids":
            route_document_ids,
        "permission_document_ids":
            permission_document_ids,
        "current_document_ids":
            current_ids,
        "historical_document_ids":
            historical_ids,
        "allowed_document_ids":
            allowed_document_ids,
        "time_context":
            time_context,
        "version_result":
            version_result,
    }