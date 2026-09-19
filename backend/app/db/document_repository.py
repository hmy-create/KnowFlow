from app.corpus.manifest import (
    CorpusManifestEntry,
)
from app.db.connection import (
    get_connection,
)


def upsert_document(
    item: CorpusManifestEntry,
):

    sql = """
    INSERT INTO documents (
        document_id,
        source_doc_no,
        source_file,
        domain,
        topic_id,
        title,
        version_no,
        effective_at,
        expired_at,
        status,
        department,
        confidentiality,
        allowed_roles,
        kb_id
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (document_id)
    DO UPDATE SET
        source_doc_no =
            EXCLUDED.source_doc_no,
        source_file =
            EXCLUDED.source_file,
        domain =
            EXCLUDED.domain,
        topic_id =
            EXCLUDED.topic_id,
        title =
            EXCLUDED.title,
        version_no =
            EXCLUDED.version_no,
        effective_at =
            EXCLUDED.effective_at,
        expired_at =
            EXCLUDED.expired_at,
        status =
            EXCLUDED.status,
        department =
            EXCLUDED.department,
        confidentiality =
            EXCLUDED.confidentiality,
        allowed_roles =
            EXCLUDED.allowed_roles,
        kb_id =
            EXCLUDED.kb_id;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                sql,
                (
                    item.document_id,
                    item.source_doc_no,
                    item.source_file,
                    item.domain,
                    item.topic_id,
                    item.title,
                    item.version_no,
                    item.effective_at,
                    item.expired_at,
                    item.status,
                    item.department,
                    item.confidentiality,
                    item.allowed_roles,
                    item.kb_id,
                ),
            )

        conn.commit()

from app.models import Document


PUBLIC_KB_BY_DOMAIN = {
    "HR": "KB_HR_PUBLIC",
    "Finance": "KB_FINANCE_PUBLIC",
    "Product": "KB_PRODUCT_PUBLIC",
    "Service": "KB_SERVICE_PUBLIC",
}


def get_route_kb_id(
    domain: str,
    sensitivity: str | None,
) -> str | None:
    """
    将 Frozen POC Router 结果转成知识库范围。

    Finance:
    - Normal     -> KB_FINANCE_PUBLIC
    - Restricted -> KB_FINANCE_PRIVATE

    其他 Domain:
    - 使用对应 Public KB
    """

    if domain == "Finance":
        if sensitivity == "Restricted":
            return "KB_FINANCE_PRIVATE"

        return "KB_FINANCE_PUBLIC"

    return PUBLIC_KB_BY_DOMAIN.get(domain)


def list_documents_by_route(
    domain: str,
    sensitivity: str | None = None,
) -> list[Document]:
    """
    只加载当前 Router 分支允许进入后续流程的 Document。

    这里已经先完成 Domain / Sensitivity Scope，
    后面才做 Permission 和 Version。
    """

    kb_id = get_route_kb_id(
        domain,
        sensitivity,
    )

    if kb_id is None:
        return []

    sql = """
    SELECT
        document_id,
        topic_id,
        title,
        version_no,
        effective_at,
        expired_at,
        status,
        department,
        confidentiality,
        allowed_roles,
        kb_id
    FROM documents
    WHERE domain = %s
      AND kb_id = %s
    ORDER BY effective_at, document_id;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                sql,
                (
                    domain,
                    kb_id,
                ),
            )

            rows = cur.fetchall()

    return [
        Document(
            document_id=row[0],
            topic_id=row[1],
            title=row[2],
            version_no=row[3],
            effective_at=row[4],
            expired_at=row[5],
            status=row[6],
            department=row[7],
            confidentiality=row[8],
            allowed_roles=list(
                row[9] or []
            ),
            kb_id=row[10],
        )
        for row in rows
    ]

def get_documents_by_ids(
    document_ids: list[str],
) -> list[Document]:

    if not document_ids:
        return []

    sql = """
    SELECT
        document_id,
        topic_id,
        title,
        version_no,
        effective_at,
        expired_at,
        status,
        department,
        confidentiality,
        allowed_roles,
        kb_id
    FROM documents
    WHERE document_id = ANY(%s)
    ORDER BY document_id;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                sql,
                (document_ids,),
            )

            rows = cur.fetchall()

    return [
        Document(
            document_id=row[0],
            topic_id=row[1],
            title=row[2],
            version_no=row[3],
            effective_at=row[4],
            expired_at=row[5],
            status=row[6],
            department=row[7],
            confidentiality=row[8],
            allowed_roles=list(
                row[9] or []
            ),
            kb_id=row[10],
        )
        for row in rows
    ]