import json
from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
from fastapi.encoders import (
    jsonable_encoder,
)

from app.db.connection import (
    get_connection,
)


router = APIRouter(
    prefix="/ops",
    tags=["Ops"],
)


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

BADCASE_PATH = (
    REPO_ROOT
    / "eval"
    / "badcase_runtime.jsonl"
)


@router.get("/traces")
def list_traces(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    """
    S10 Trace 页面使用。

    只读取已经持久化的 Trace，
    不修改任何 S3-S9 业务逻辑。
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT to_jsonb(t)
                FROM traces AS t
                ORDER BY ctid DESC
                LIMIT %s
                """,
                (limit,),
            )

            rows = cur.fetchall()

    items = [
        jsonable_encoder(
            row[0]
        )
        for row in rows
    ]

    return {
        "count": len(items),
        "items": items,
    }


@router.get(
    "/traces/{trace_id}"
)
def get_trace(
    trace_id: str,
):
    """
    按 trace_id 完整还原一次请求。
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT to_jsonb(t)
                FROM traces AS t
                WHERE trace_id = %s
                LIMIT 1
                """,
                (trace_id,),
            )

            row = cur.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Trace not found.",
        )

    return jsonable_encoder(
        row[0]
    )


@router.get("/badcases")
def list_badcases(
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
):
    """
    S10 Badcase 页面。

    当前直接复用 S9 runtime badcase pool。
    """

    if not BADCASE_PATH.exists():

        return {
            "count": 0,
            "items": [],
        }

    lines = (
        BADCASE_PATH
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
    )

    items = []

    for line in reversed(lines):

        if not line.strip():
            continue

        try:

            items.append(
                json.loads(line)
            )

        except json.JSONDecodeError:

            items.append(
                {
                    "raw": line,
                    "parse_error": True,
                }
            )

        if len(items) >= limit:
            break

    return {
        "count": len(items),
        "items": items,
    }
