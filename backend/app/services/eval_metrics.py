import math


def recall_at_k(
    ranked_ids: list[str],
    relevant_ids: list[str],
    k: int,
) -> float | None:

    if not relevant_ids:
        return None

    relevant = set(
        relevant_ids
    )

    retrieved = set(
        ranked_ids[:k]
    )

    return (
        len(
            relevant & retrieved
        )
        / len(relevant)
    )


def mrr_at_k(
    ranked_ids: list[str],
    relevant_ids: list[str],
    k: int,
) -> float | None:

    if not relevant_ids:
        return None

    relevant = set(
        relevant_ids
    )

    for rank, item_id in enumerate(
        ranked_ids[:k],
        start=1,
    ):

        if item_id in relevant:
            return (
                1.0 / rank
            )

    return 0.0


def ndcg_at_k(
    ranked_ids: list[str],
    relevant_ids: list[str],
    k: int,
) -> float | None:

    if not relevant_ids:
        return None

    relevant = set(
        relevant_ids
    )

    dcg = 0.0

    for rank, item_id in enumerate(
        ranked_ids[:k],
        start=1,
    ):

        relevance = (
            1.0
            if item_id in relevant
            else 0.0
        )

        dcg += (
            relevance
            / math.log2(
                rank + 1
            )
        )

    ideal_hits = min(
        len(relevant),
        k,
    )

    idcg = sum(
        1.0
        / math.log2(
            rank + 1
        )
        for rank
        in range(
            1,
            ideal_hits + 1,
        )
    )

    if idcg == 0:
        return 0.0

    return (
        dcg / idcg
    )


def mean_optional(
    values: list[
        float | None
    ],
) -> float | None:

    valid = [
        value
        for value in values
        if value is not None
    ]

    if not valid:
        return None

    return (
        sum(valid)
        / len(valid)
    )


def bool_rate(
    values: list[
        bool | None
    ],
) -> float | None:

    valid = [
        value
        for value in values
        if value is not None
    ]

    if not valid:
        return None

    return (
        sum(
            1
            for value in valid
            if value
        )
        / len(valid)
    )


def p95(
    values: list[int],
) -> int:

    if not values:
        return 0

    ordered = sorted(
        values
    )

    index = (
        math.ceil(
            0.95
            * len(ordered)
        )
        - 1
    )

    index = max(
        0,
        min(
            index,
            len(ordered) - 1,
        ),
    )

    return ordered[
        index
    ]