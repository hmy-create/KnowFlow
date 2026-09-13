import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector


REPO_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(REPO_ROOT / ".env")


def get_connection():
    conn = psycopg.connect(
        host=os.getenv(
            "POSTGRES_HOST",
            "127.0.0.1",
        ),
        port=int(
            os.getenv(
                "POSTGRES_PORT",
                "5432",
            )
        ),
        dbname=os.getenv(
            "POSTGRES_DB",
            "knowflow",
        ),
        user=os.getenv(
            "POSTGRES_USER",
            "knowflow",
        ),
        password=os.getenv(
            "POSTGRES_PASSWORD",
            "",
        ),
    )

    register_vector(conn)

    return conn