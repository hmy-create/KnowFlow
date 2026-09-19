from collections.abc import Iterable

from app.db.connection import get_connection
from app.models import (
    Chunk,
    RetrievalCandidate,
)
from app.retrieval.vector_retriever import (
    encode_dense,
)


def upsert_chunk_embeddings(
    chunks: Iterable[Chunk],
) -> int:
    """
    对 Chunk 生成 BGE-M3 dense embedding，
    并写入 PostgreSQL + pgvector。

    chunk_id 已存在时执行更新。
    """

    chunks = list(chunks)

    if not chunks:
        return 0

    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = encode_dense(texts)

    sql = """
    INSERT INTO chunk_embeddings (
        chunk_id,
        document_id,
        text,
        page,
        section,
        chunk_index,
        embedding
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (chunk_id)
    DO UPDATE SET
        document_id = EXCLUDED.document_id,
        text = EXCLUDED.text,
        page = EXCLUDED.page,
        section = EXCLUDED.section,
        chunk_index = EXCLUDED.chunk_index,
        embedding = EXCLUDED.embedding;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            for chunk, embedding in zip(
                chunks,
                embeddings,
            ):
                cur.execute(
                    sql,
                    (
                        chunk.chunk_id,
                        chunk.document_id,
                        chunk.text,
                        chunk.page,
                        chunk.section,
                        chunk.chunk_index,
                        embedding,
                    ),
                )

        conn.commit()

    return len(chunks)

def scoped_vector_search(
    query: str,
    allowed_document_ids: list[str],
    top_n: int = 20,
) -> list[RetrievalCandidate]:
    """
    pgvector 向量检索。

    强制要求调用方提供已经经过
    Permission + Version Filter 的
    allowed_document_ids。

    如果 scope 为空，直接返回空列表，
    绝不执行全库检索。
    """

    if not allowed_document_ids:
        return []

    query_vector = encode_dense(
        [query]
    )[0]

    sql = """
    SELECT
        chunk_id,
        document_id,
        text,
        page,
        section,
        chunk_index,
        1 - (embedding <=> %s) AS vector_score
    FROM chunk_embeddings
    WHERE document_id = ANY(%s)
    ORDER BY embedding <=> %s
    LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                sql,
                (
                    query_vector,
                    allowed_document_ids,
                    query_vector,
                    top_n,
                ),
            )

            rows = cur.fetchall()

    return [
        RetrievalCandidate(
            chunk_id=row[0],
            document_id=row[1],
            text=row[2],
            page=row[3],
            section=row[4],
            chunk_index=row[5],
            retrieval_source="vector",
            raw_score={
                "vector": float(row[6])
            },
        )
        for row in rows
    ]

def delete_chunks(
    chunk_ids: list[str],
) -> int:
    """
    主要用于测试清理。
    """

    if not chunk_ids:
        return 0

    sql = """
    DELETE FROM chunk_embeddings
    WHERE chunk_id = ANY(%s);
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                sql,
                (chunk_ids,),
            )

            deleted = cur.rowcount

        conn.commit()

    return deleted

def delete_document_chunks(
    document_id: str,
) -> int:

    sql = """
    DELETE FROM chunk_embeddings
    WHERE document_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                sql,
                (document_id,),
            )

            deleted = cur.rowcount

        conn.commit()

    return deleted