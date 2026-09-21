from app.services.eval_metrics import (
    mrr_at_k,
    ndcg_at_k,
    recall_at_k,
)


def test_recall_at_5():

    ranked = [
        "A",
        "B",
        "C",
        "D",
        "E",
    ]

    relevant = [
        "B",
        "E",
    ]

    assert (
        recall_at_k(
            ranked,
            relevant,
            5,
        )
        == 1.0
    )


def test_mrr_at_10():

    ranked = [
        "A",
        "B",
        "C",
    ]

    relevant = [
        "B",
    ]

    assert (
        mrr_at_k(
            ranked,
            relevant,
            10,
        )
        == 0.5
    )


def test_ndcg_perfect():

    ranked = [
        "A",
        "B",
    ]

    relevant = [
        "A",
        "B",
    ]

    assert (
        ndcg_at_k(
            ranked,
            relevant,
            10,
        )
        == 1.0
    )


def test_metrics_none_without_gold():

    assert (
        recall_at_k(
            ["A"],
            [],
            5,
        )
        is None
    )

    assert (
        mrr_at_k(
            ["A"],
            [],
            10,
        )
        is None
    )

    assert (
        ndcg_at_k(
            ["A"],
            [],
            10,
        )
        is None
    )