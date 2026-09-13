from datetime import date
from collections.abc import Iterable

from app.models import (
    Document,
    QueryTimeContext,
    VersionFilterResult,
)


def is_applicable(
    doc: Document,
    query_date: date,
) -> bool:
    """
    V102 核心规则。

    expired_at 当天仍然有效。
    """

    return (
        doc.effective_at <= query_date
        and (
            doc.expired_at is None
            or query_date <= doc.expired_at
        )
    )

def is_current_status(
    doc: Document,
) -> bool:
    """
    当前查询只允许当前 active 文档。
    """

    return doc.status == "active"


def is_historical_status(
    doc: Document,
) -> bool:
    """
    历史查询允许：
    - 当前仍 active，但历史日期也在有效区间内
    - 当前已经 expired 的历史文档

    pending / draft / failed 等均不得使用。
    """

    return doc.status in {
        "active",
        "expired",
    }

def overlaps_period(
    doc: Document,
    period_start: date,
    period_end: date,
) -> bool:
    """
    判断文档有效期是否与查询时间段有重叠。
    """

    doc_end = (
        doc.expired_at
        if doc.expired_at is not None
        else date.max
    )

    return (
        doc.effective_at <= period_end
        and doc_end >= period_start
    )

def filter_current_documents(
    documents: Iterable[Document],
    query_date: date,
) -> list[Document]:

    return [
        doc
        for doc in documents
        if (
            is_current_status(doc)
            and is_applicable(
                doc,
                query_date,
            )
        )
    ]

def filter_historical_documents(
    documents: Iterable[Document],
    context: QueryTimeContext,
) -> list[Document]:

    documents = list(documents)

    if context.selector == "exact_date":

        return [
            doc
            for doc in documents
            if (
                is_historical_status(doc)
                and context.query_date
                is not None
                and is_applicable(
                    doc,
                    context.query_date,
                )
            )
        ]

    if context.selector == "period":

        return [
            doc
            for doc in documents
            if (
                is_historical_status(doc)
                and context.period_start
                is not None
                and context.period_end
                is not None
                and overlaps_period(
                    doc,
                    context.period_start,
                    context.period_end,
                )
            )
        ]

    if context.selector == "all_historical":

        return [
            doc
            for doc in documents
            if doc.status == "expired"
        ]

    return []

def filter_comparison_history(
    documents: Iterable[Document],
    context: QueryTimeContext,
) -> list[Document]:

    documents = list(documents)

    if context.history_selector == "exact_date":

        return [
            doc
            for doc in documents
            if (
                is_historical_status(doc)
                and context.historical_date
                is not None
                and is_applicable(
                    doc,
                    context.historical_date,
                )
            )
        ]

    if context.history_selector == "period":

        return [
            doc
            for doc in documents
            if (
                is_historical_status(doc)
                and context.historical_period_start
                is not None
                and context.historical_period_end
                is not None
                and overlaps_period(
                    doc,
                    context.historical_period_start,
                    context.historical_period_end,
                )
            )
        ]

    if (
        context.history_selector
        == "all_historical"
    ):
        return [
            doc
            for doc in documents
            if doc.status == "expired"
        ]

    return []

def filter_documents_by_version(
    documents: Iterable[Document],
    context: QueryTimeContext,
) -> VersionFilterResult:

    documents = list(documents)

    current_docs: list[Document] = []
    historical_docs: list[Document] = []

    if context.version_mode == "Current":

        if context.selector in {
            "request_time",
            "exact_date",
        }:
            current_docs = (
                filter_current_documents(
                    documents,
                    context.query_date,
                )
                if context.query_date
                is not None
                else []
            )

        elif context.selector == "period":

            current_docs = [
                doc
                for doc in documents
                if (
                    is_current_status(doc)
                    and context.period_start
                    is not None
                    and context.period_end
                    is not None
                    and overlaps_period(
                        doc,
                        context.period_start,
                        context.period_end,
                    )
                )
            ]

    elif context.version_mode == "Historical":

        historical_docs = (
            filter_historical_documents(
                documents,
                context,
            )
        )

    elif context.version_mode == "Comparison":

        if context.current_date is not None:
            current_docs = (
                filter_current_documents(
                    documents,
                    context.current_date,
                )
            )

        historical_docs = (
            filter_comparison_history(
                documents,
                context,
            )
        )

    kept_ids = {
        doc.document_id
        for doc in (
            current_docs
            + historical_docs
        )
    }

    blocked_ids = [
        doc.document_id
        for doc in documents
        if doc.document_id
        not in kept_ids
    ]

    return VersionFilterResult(
        version_mode=context.version_mode,
        current_document_ids=[
            doc.document_id
            for doc in current_docs
        ],
        historical_document_ids=[
            doc.document_id
            for doc in historical_docs
        ],
        blocked_document_ids=blocked_ids,
    )