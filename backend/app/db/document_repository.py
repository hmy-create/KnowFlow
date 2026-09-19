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