import pytest

from backend.app.core.domain_router import match_frozen_domain


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (
            "2025年一线城市住宿标准是多少？",
            "Finance",
        ),
        (
            "预算调整审批链是什么？",
            "Finance",
        ),
        (
            "电子发票可以报销吗？",
            "Finance",
        ),
        (
            "现在员工试用期多久？",
            "HR",
        ),
        (
            "现在产品 A 退款规则是什么？",
            "Product",
        ),
        (
            "P1投诉多久首次响应？",
            "Service",
        ),
    ],
)
def test_frozen_domain_strong_match(
    query,
    expected,
):
    assert match_frozen_domain(query) == expected

def test_multi_domain_query_falls_back():
    result = match_frozen_domain(
        "产品 A 退款的发票怎么处理？"
    )

    assert result is None