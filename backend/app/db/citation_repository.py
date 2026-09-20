from app.db.connection import get_connection


def get_citation_sources(
    chunk_ids: list[str],
) -> list[dict]:

    if not chunk_ids:
        return []

    sql = """
    SELECT
        ce.chunk_id,
        ce.document_id,
        d.title,
        d.version_no,
        ce.page,
        ce.section,
        ce.text
    FROM chunk_embeddings ce
    JOIN documents d
      ON d.document_id = ce.document_id
    WHERE ce.chunk_id = ANY(%s);
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                sql,
                (chunk_ids,),
            )

            rows = cur.fetchall()

    return [
        {
            "chunk_id": row[0],
            "document_id": row[1],
            "title": row[2],
            "version_no": row[3],
            "page": row[4],
            "section": row[5],
            "original_text": row[6],
        }
        for row in rows
    ]