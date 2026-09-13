from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class QueryTimeContext(BaseModel):
    """
    用户问题对应的时间范围。

    Current / Historical:
        使用 selector + query_date / period

    Comparison:
        current 与 historical 分开保存，
        防止两个版本上下文混在一起。
    """

    version_mode: Literal[
        "Current",
        "Historical",
        "Comparison",
    ]

    selector: Literal[
        "request_time",
        "exact_date",
        "period",
        "all_historical",
        "comparison",
    ]

    query_date: date | None = None

    period_start: date | None = None
    period_end: date | None = None

    # Comparison 当前侧
    current_date: date | None = None

    # Comparison 历史侧
    history_selector: Literal[
        "none",
        "exact_date",
        "period",
        "all_historical",
    ] = "none"

    historical_date: date | None = None

    historical_period_start: date | None = None
    historical_period_end: date | None = None

    source: str = Field(
        default="",
        description="时间来源，例如 explicit_date / year / request_time"
    )


class VersionFilterResult(BaseModel):
    version_mode: str

    current_document_ids: list[str] = Field(
        default_factory=list
    )

    historical_document_ids: list[str] = Field(
        default_factory=list
    )

    blocked_document_ids: list[str] = Field(
        default_factory=list
    )