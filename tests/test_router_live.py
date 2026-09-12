import os

import pytest

from backend.app.core.router_service import route_query


RUN_LIVE = (
    os.getenv("RUN_LIVE_ROUTER_TESTS") == "1"
)


@pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live router test disabled",
)
@pytest.mark.parametrize(
    (
        "query",
        "domain",
        "sensitivity",
        "version_mode",
    ),
    [
        (
            "电子发票可以报销吗？",
            "Finance",
            "Normal",
            "Current",
        ),
        (
            "2025年一线城市住宿标准是多少？",
            "Finance",
            "Normal",
            "Historical",
        ),
        (
            "预算调整审批链是什么？",
            "Finance",
            "Restricted",
            None,
        ),
        (
            "现在员工试用期多久？",
            "HR",
            None,
            "Current",
        ),
        (
            "2025年员工试用期规定是什么？",
            "HR",
            None,
            "Historical",
        ),
        (
            "现在产品 A 退款规则是什么？",
            "Product",
            None,
            "Current",
        ),
        (
            "2025年产品 A 退款规则是什么？",
            "Product",
            None,
            "Historical",
        ),
        (
            "产品 A 现在和旧版退款规则有什么区别？",
            "Product",
            None,
            "Comparison",
        ),
    ],
)
def test_router_parity(
    query,
    domain,
    sensitivity,
    version_mode,
):
    result = route_query(query)

    assert result["domain"] == domain
    assert result["sensitivity"] == sensitivity
    assert result["version_mode"] == version_mode