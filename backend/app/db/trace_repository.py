from psycopg.types.json import Jsonb

from app.db.connection import (
    get_connection,
)
from app.models import TraceRecord


def save_trace(
    trace: TraceRecord,
) -> None:

    sql = """
    INSERT INTO traces (
        trace_id,
        query,
        user_id,
        domain,
        sensitivity,
        version_mode,
        query_date,
        permission_filter,
        version_filter,
        retrieved_chunks,
        rerank_scores,
        decision,
        decision_reason,
        clarifying_question,
        evidence_ids,
        citations,
        latency_ms,
        input_tokens,
        output_tokens,
        prompt_version
    )
    VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s
    );
    """

    citations = [
        item.model_dump()
        for item in trace.citations
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                sql,
                (
                    trace.trace_id,
                    trace.query,
                    trace.user_id,
                    trace.domain,
                    trace.sensitivity,
                    trace.version_mode,
                    trace.query_date,
                    Jsonb(
                        trace.permission_filter
                    ),
                    Jsonb(
                        trace.version_filter
                    ),
                    Jsonb(
                        trace.retrieved_chunks
                    ),
                    Jsonb(
                        trace.rerank_scores
                    ),
                    trace.decision,
                    trace.decision_reason,
                    trace.clarifying_question,
                    trace.evidence_ids,
                    Jsonb(citations),
                    trace.latency_ms,
                    trace.input_tokens,
                    trace.output_tokens,
                    trace.prompt_version,
                ),
            )

        conn.commit()


def get_trace(
    trace_id: str,
) -> dict | None:

    sql = """
    SELECT
        trace_id,
        created_at,
        query,
        user_id,
        domain,
        sensitivity,
        version_mode,
        query_date,
        permission_filter,
        version_filter,
        retrieved_chunks,
        rerank_scores,
        decision,
        decision_reason,
        clarifying_question,
        evidence_ids,
        citations,
        latency_ms,
        input_tokens,
        output_tokens,
        prompt_version
    FROM traces
    WHERE trace_id = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                sql,
                (trace_id,),
            )

            row = cur.fetchone()

    if row is None:
        return None

    return {
        "trace_id": row[0],
        "created_at": row[1],
        "query": row[2],
        "user_id": row[3],
        "domain": row[4],
        "sensitivity": row[5],
        "version_mode": row[6],
        "query_date": row[7],
        "permission_filter": row[8],
        "version_filter": row[9],
        "retrieved_chunks": row[10],
        "rerank_scores": row[11],
        "decision": row[12],
        "decision_reason": row[13],
        "clarifying_question": row[14],
        "evidence_ids": row[15],
        "citations": row[16],
        "latency_ms": row[17],
        "input_tokens": row[18],
        "output_tokens": row[19],
        "prompt_version": row[20],
    }