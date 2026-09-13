import re
from datetime import date

from app.models import QueryTimeContext


def extract_explicit_date(
    query: str,
) -> date | None:
    """
    支持：
    2026-05-01
    2026/05/01
    2026年5月1日
    """

    patterns = [
        r"(\d{4})-(\d{1,2})-(\d{1,2})",
        r"(\d{4})/(\d{1,2})/(\d{1,2})",
        r"(\d{4})年(\d{1,2})月(\d{1,2})日",
    ]

    for pattern in patterns:
        match = re.search(pattern, query)

        if match:
            year, month, day = map(
                int,
                match.groups(),
            )

            return date(
                year,
                month,
                day,
            )

    return None


def extract_year(
    query: str,
) -> int | None:
    """
    只提取 YYYY年。
    具体 YYYY年MM月DD日 会先被 exact date 捕获。
    """

    match = re.search(
        r"(?<!\d)(20\d{2})年",
        query,
    )

    if match:
        return int(match.group(1))

    return None


def year_period(
    year: int,
) -> tuple[date, date]:

    return (
        date(year, 1, 1),
        date(year, 12, 31),
    )


def resolve_query_time(
    query: str,
    version_mode: str,
    request_date: date | None = None,
) -> QueryTimeContext:
    """
    将用户时间表达转换为结构化时间条件。

    优先级：
    1. 明确具体日期
    2. 明确年份
    3. 去年
    4. Current 使用请求日期
    5. Historical 无日期 → all_historical
    6. Comparison → 当前与历史分开
    """

    request_date = request_date or date.today()

    explicit_date = extract_explicit_date(
        query
    )

    explicit_year = extract_year(
        query
    )

    # -------------------------
    # Comparison
    # -------------------------
    if version_mode == "Comparison":

        if explicit_date:
            return QueryTimeContext(
                version_mode="Comparison",
                selector="comparison",
                current_date=request_date,
                history_selector="exact_date",
                historical_date=explicit_date,
                source="comparison_explicit_date",
            )

        if explicit_year:
            start, end = year_period(
                explicit_year
            )

            return QueryTimeContext(
                version_mode="Comparison",
                selector="comparison",
                current_date=request_date,
                history_selector="period",
                historical_period_start=start,
                historical_period_end=end,
                source="comparison_year",
            )

        if "去年" in query:
            year = request_date.year - 1
            start, end = year_period(year)

            return QueryTimeContext(
                version_mode="Comparison",
                selector="comparison",
                current_date=request_date,
                history_selector="period",
                historical_period_start=start,
                historical_period_end=end,
                source="comparison_last_year",
            )

        return QueryTimeContext(
            version_mode="Comparison",
            selector="comparison",
            current_date=request_date,
            history_selector="all_historical",
            source="comparison_all_historical",
        )

    # -------------------------
    # 明确日期优先
    # -------------------------
    if explicit_date:
        return QueryTimeContext(
            version_mode=version_mode,
            selector="exact_date",
            query_date=explicit_date,
            source="explicit_date",
        )

    # -------------------------
    # 明确年份
    # -------------------------
    if explicit_year:
        start, end = year_period(
            explicit_year
        )

        return QueryTimeContext(
            version_mode=version_mode,
            selector="period",
            period_start=start,
            period_end=end,
            source="explicit_year",
        )

    # -------------------------
    # 去年
    # -------------------------
    if "去年" in query:
        year = request_date.year - 1

        start, end = year_period(year)

        return QueryTimeContext(
            version_mode=version_mode,
            selector="period",
            period_start=start,
            period_end=end,
            source="last_year",
        )

    # -------------------------
    # Current
    # -------------------------
    if version_mode == "Current":
        return QueryTimeContext(
            version_mode="Current",
            selector="request_time",
            query_date=request_date,
            source="request_time",
        )

    # -------------------------
    # Historical，无明确时间
    # -------------------------
    if version_mode == "Historical":
        return QueryTimeContext(
            version_mode="Historical",
            selector="all_historical",
            source="all_historical",
        )

    raise ValueError(
        f"Unsupported version mode: "
        f"{version_mode}"
    )