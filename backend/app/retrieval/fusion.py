from app.models import RetrievalCandidate


def reciprocal_rank_fusion(
    bm25_results: list[RetrievalCandidate],
    vector_results: list[RetrievalCandidate],
    k: int = 60,
) -> list[RetrievalCandidate]:

    merged: dict[
        str,
        RetrievalCandidate
    ] = {}

    def add_results(
        results: list[
            RetrievalCandidate
        ],
        source: str,
    ):
        for rank, candidate in enumerate(
            results,
            start=1,
        ):
            rrf_score = 1.0 / (
                k + rank
            )

            if (
                candidate.chunk_id
                not in merged
            ):
                item = (
                    candidate.model_copy(
                        deep=True
                    )
                )

                item.fused_score = (
                    rrf_score
                )

                merged[
                    candidate.chunk_id
                ] = item

            else:
                item = merged[
                    candidate.chunk_id
                ]

                item.fused_score += (
                    rrf_score
                )

                item.raw_score.update(
                    candidate.raw_score
                )

                item.retrieval_source = (
                    "hybrid"
                )

    add_results(
        bm25_results,
        "bm25",
    )

    add_results(
        vector_results,
        "vector",
    )

    return sorted(
        merged.values(),
        key=lambda x: x.fused_score,
        reverse=True,
    )