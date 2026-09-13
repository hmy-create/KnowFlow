from app.db.connection import (
    get_connection,
)


CREATE_EXTENSION_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
"""


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS chunk_embeddings (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    text TEXT NOT NULL,

    page INTEGER,
    section TEXT,
    chunk_index INTEGER NOT NULL,

    embedding vector(1024) NOT NULL
);
"""


CREATE_DOCUMENT_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS
idx_chunk_embeddings_document_id
ON chunk_embeddings(document_id);
"""


def init_database():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                CREATE_EXTENSION_SQL
            )

            cur.execute(
                CREATE_TABLE_SQL
            )

            cur.execute(
                CREATE_DOCUMENT_INDEX_SQL
            )

        conn.commit()