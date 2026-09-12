from collections.abc import Iterable

from app.models import (
    Document,
    PermissionResult,
    User,
)


def allowed_document(
    doc: Document,
    user: User,
) -> bool:
    """
    判断单份文档是否允许进入后续检索范围。

    两层条件：
    1. 用户必须拥有该 kb_id
    2. 如果文档指定 allowed_roles，
       用户角色必须在其中
    """

    if doc.kb_id not in user.authorized_kb_ids:
        return False

    if (
        doc.allowed_roles
        and user.role not in doc.allowed_roles
    ):
        return False

    return True


def filter_authorized_documents(
    documents: Iterable[Document],
    user: User,
) -> PermissionResult:
    """
    在 Retrieval 之前执行 ACL / Metadata Filter。
    无权限文档不会进入后续候选集。
    """

    documents = list(documents)

    allowed_docs = [
        doc
        for doc in documents
        if allowed_document(doc, user)
    ]

    return PermissionResult(
        decision=(
            "allowed"
            if allowed_docs
            else "no_access"
        ),
        reason=(
            "至少存在一份用户有权访问的文档。"
            if allowed_docs
            else "当前用户无权访问候选知识范围。"
        ),
        allowed_document_ids=[
            doc.document_id
            for doc in allowed_docs
        ],
        blocked_count=(
            len(documents) - len(allowed_docs)
        ),
    )

FINANCE_PRIVATE_KB_ID = "KB_FINANCE_PRIVATE"

FINANCE_PRIVATE_ROLES = {
    "finance_manager",
    "admin",
}


def can_access_finance_private(
    user: User,
) -> bool:
    """
    迁移 Frozen POC 中 Finance Restricted 的权限检查。
    """

    if (
        FINANCE_PRIVATE_KB_ID
        not in user.authorized_kb_ids
    ):
        return False

    if user.role not in FINANCE_PRIVATE_ROLES:
        return False

    return True

def check_route_permission(
    routing: dict,
    user: User,
) -> PermissionResult:
    """
    当前只迁移 Frozen POC 已存在的
    Finance Restricted 权限分支。

    其他 Domain 暂不新增人为权限规则。
    """

    if (
        routing.get("domain") == "Finance"
        and routing.get("sensitivity")
        == "Restricted"
    ):
        allowed = can_access_finance_private(
            user
        )

        if not allowed:
            return PermissionResult(
                decision="no_access",
                reason=(
                    "当前用户无权访问受限财务知识。"
                ),
                allowed_document_ids=[],
                blocked_count=0,
            )

    return PermissionResult(
        decision="allowed",
        reason="当前路由未触发权限拦截。",
        allowed_document_ids=[],
        blocked_count=0,
    )