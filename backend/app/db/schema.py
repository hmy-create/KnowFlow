from app.db.connection import (
    get_connection,
)


CREATE_EXTENSION_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
"""


CREATE_DOCUMENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,

    source_doc_no TEXT NOT NULL,
    source_file TEXT NOT NULL,

    domain TEXT NOT NULL,
    topic_id TEXT NOT NULL,

    title TEXT NOT NULL,
    version_no TEXT NOT NULL,

    effective_at DATE NOT NULL,
    expired_at DATE,

    status TEXT NOT NULL,

    department TEXT NOT NULL,
    confidentiality TEXT NOT NULL,

    allowed_roles TEXT[] NOT NULL
        DEFAULT '{}',

    kb_id TEXT NOT NULL
);
"""


CREATE_DOCUMENT_DOMAIN_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS
idx_documents_domain
ON documents(domain);
"""


CREATE_DOCUMENT_TOPIC_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS
idx_documents_topic
ON documents(topic_id);
"""


CREATE_DOCUMENT_KB_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS
idx_documents_kb
ON documents(kb_id);
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
    with get_connection(
        register_pgvector=False
    ) as conn:
        with conn.cursor() as cur:

            # 1. 必须先确保 pgvector extension 存在
            cur.execute(
                CREATE_EXTENSION_SQL
            )

            # 2. Document metadata 表
            cur.execute(
                CREATE_DOCUMENTS_TABLE_SQL
            )

            cur.execute(
                CREATE_DOCUMENT_DOMAIN_INDEX_SQL
            )

            cur.execute(
                CREATE_DOCUMENT_TOPIC_INDEX_SQL
            )

            cur.execute(
                CREATE_DOCUMENT_KB_INDEX_SQL
            )

            # 3. Chunk + Embedding 表
            cur.execute(
                CREATE_TABLE_SQL
            )

            cur.execute(
                CREATE_DOCUMENT_INDEX_SQL
            )

        conn.commit()