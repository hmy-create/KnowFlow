from functools import lru_cache

import torch
from FlagEmbedding import FlagReranker

from app.models import (
    RetrievalCandidate,
)


@lru_cache(maxsize=1)
def get_reranker():
    return FlagReranker(
        "BAAI/bge-reranker-v2-m3",
        use_fp16=torch.cuda.is_available(),
    )


def rerank_candidates(
    query: str,
    candidates: list[
        RetrievalCandidate
    ],
    top_k: int = 10,
) -> list[RetrievalCandidate]:

    if not candidates:
        return []

    model = get_reranker()

    pairs = [
        [
            query,
            candidate.text,
        ]
        for candidate in candidates
    ]

    scores = model.compute_score(
        pairs,
        normalize=True,
    )

    if isinstance(
        scores,
        (int, float),
    ):
        scores = [scores]

    reranked = []

    for candidate, score in zip(
        candidates,
        scores,
    ):
        item = candidate.model_copy(
            deep=True
        )

        item.rerank_score = float(
            score
        )

        reranked.append(item)

    reranked.sort(
        key=lambda x: (
            x.rerank_score
            if x.rerank_score
            is not None
            else -1.0
        ),
        reverse=True,
    )

    return reranked[:top_k]