from rank_bm25 import BM25Okapi

from app.models import (
    Chunk,
    RetrievalCandidate,
)
from app.retrieval.tokenizer import tokenize


def bm25_retrieve(
    query: str,
    chunks: list[Chunk],
    top_n: int = 20,
) -> list[RetrievalCandidate]:

    if not chunks:
        return []

    tokenized_corpus = [
        tokenize(chunk.text)
        for chunk in chunks
    ]

    bm25 = BM25Okapi(
        tokenized_corpus
    )

    query_tokens = tokenize(query)

    scores = bm25.get_scores(
        query_tokens
    )

    ranked_indices = sorted(
        range(len(chunks)),
        key=lambda i: scores[i],
        reverse=True,
    )

    results: list[
        RetrievalCandidate
    ] = []

    for index in ranked_indices:

        score = float(scores[index])

        # 没有词法相关性则不作为 BM25 候选
        if score <= 0:
            continue

        chunk = chunks[index]

        results.append(
            RetrievalCandidate(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                page=chunk.page,
                section=chunk.section,
                chunk_index=chunk.chunk_index,
                retrieval_source="bm25",
                raw_score={
                    "bm25": score
                },
            )
        )

        if len(results) >= top_n:
            break

    return results