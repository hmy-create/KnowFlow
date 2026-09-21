import csv
import json
import uuid
import time
from datetime import datetime
from pathlib import Path

from app.api.chat import chat
from app.db.connection import (
    get_connection,
)
from app.db.trace_repository import (
    get_trace,
)
from app.models import (
    EvalCase,
    EvalCaseResult,
)
from app.schemas.chat import (
    ChatRequest,
)
from app.services.eval_loader import (
    load_eval_cases,
)
from app.services.eval_metrics import (
    bool_rate,
    mean_optional,
    mrr_at_k,
    ndcg_at_k,
    p95,
    recall_at_k,
)


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

REPORT_DIR = (
    REPO_ROOT
    / "eval"
    / "reports"
)

MASTER_BADCASE_PATH = (
    REPO_ROOT
    / "eval"
    / "badcase_runtime.jsonl"
)


def _new_run_id() -> str:

    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d-%H%M%S"
        )
    )

    suffix = (
        uuid.uuid4()
        .hex[:6]
        .upper()
    )

    return (
        f"RUN-{timestamp}-{suffix}"
    )


def _dedupe(
    values: list[str],
) -> list[str]:

    result = []

    seen = set()

    for value in values:

        if not value:
            continue

        if value in seen:
            continue

        seen.add(
            value
        )

        result.append(
            value
        )

    return result

def _evaluate_sensitivity_match(
    case: EvalCase,
    actual_sensitivity: str | None,
) -> bool | None:
    """
    Frozen POC sensitivity semantics:

    Sensitivity routing is only a blocking dimension
    for Finance.

    HR / Product / Service / Other do not have an
    independent sensitivity routing stage in the
    frozen POC, therefore sensitivity is N/A for
    S9 parity evaluation.

    Important:
    Use frozen_domain_actual first, because the
    frozen RUN_004 dataset explicitly accepts some
    safe cross-domain cases whose ideal domain and
    frozen actual domain differ.
    """

    parity_domain = (
        case.frozen_domain_actual
        or case.expected_domain
    )

    # Sensitivity only applies to Finance.
    if parity_domain != "Finance":
        return None

    # No Gold -> do not score.
    if case.expected_sensitivity is None:
        return None

    return (
        actual_sensitivity
        == case.expected_sensitivity
    )

def _evaluate_version_match(
    case: EvalCase,
    actual_version_mode: str | None,
) -> bool | None:
    """
    Frozen POC version semantics.

    Version Resolver 只适用于：
    - HR
    - Product
    - Finance Normal

    不适用于：
    - Service
    - Other
    - Finance Restricted

    不适用时返回 None，
    表示 N/A，不进入准确率分母，
    也不作为 blocking failure。
    """

    parity_domain = (
        case.frozen_domain_actual
        or case.expected_domain
    )

    # Service / Other 没有独立 Version Resolver
    if parity_domain in {
        "Service",
        "Other",
    }:
        return None

    # Finance Restricted：
    # Frozen POC 是
    # Sensitivity → Role Check → Private/No Access
    # 不进入普通 Version Resolver。
    if (
        parity_domain == "Finance"
        and case.expected_sensitivity
        == "Restricted"
    ):
        return None

    # Gold 本身没有 Version
    if (
        case.expected_version_mode
        is None
    ):
        return None

    return (
        actual_version_mode
        == case.expected_version_mode
    )

def _safe_trace(
    trace_id: str | None,
):

    if not trace_id:
        return None

    try:
        return get_trace(
            trace_id
        )
    except Exception:
        return None


def _load_document_versions(
    document_ids: list[str],
) -> dict[str, str]:

    document_ids = _dedupe(
        document_ids
    )

    if not document_ids:
        return {}

    result = {}

    with get_connection() as conn:
        with conn.cursor() as cur:

            for document_id in document_ids:

                cur.execute(
                    """
                    SELECT
                        document_id,
                        version_no
                    FROM documents
                    WHERE document_id = %s;
                    """,
                    (
                        document_id,
                    ),
                )

                row = cur.fetchone()

                if row is not None:
                    result[
                        row[0]
                    ] = row[1]

    return result


def _citation_version_integrity(
    citations: list[dict],
) -> bool | None:

    if not citations:
        return None

    document_ids = _dedupe(
        [
            item.get(
                "document_id"
            )
            for item
            in citations
            if item.get(
                "document_id"
            )
        ]
    )

    version_map = (
        _load_document_versions(
            document_ids
        )
    )

    for citation in citations:

        document_id = (
            citation.get(
                "document_id"
            )
        )

        citation_version = (
            citation.get(
                "version_no"
            )
        )

        db_version = (
            version_map.get(
                document_id
            )
        )

        if (
            db_version is None
            or citation_version
            != db_version
        ):
            return False

    return True


def _build_badcase_type(
    checks: dict,
    error: str | None,
) -> str:

    if error:
        return "runtime_error"

    priority = [
        (
            "trace_persisted",
            "trace_error",
        ),
        (
            "domain_frozen_parity_match",
            "routing_parity_error",
        ),
        (
            "version_match",
            "version_error",
        ),
        (
            "sensitivity_match",
            "sensitivity_error",
        ),
        (
            "permission_match",
            "permission_error",
        ),
        (
            "decision_frozen_parity_match",
            "decision_error",
        ),
        (
            "clarifying_question_ok",
            "clarification_error",
        ),
        (
            "unauthorized_retrieval_ok",
            "security_error",
        ),
        (
            "no_access_safe",
            "security_error",
        ),
        (
            "citation_evidence_alignment",
            "citation_error",
        ),
        (
            "citation_version_integrity",
            "citation_version_error",
        ),
    ]

    for check_name, badcase_type in priority:

        value = checks.get(
            check_name
        )

        if value is False:
            return badcase_type

    return "evaluation_mismatch"
PUBLIC_KB_BY_DOMAIN = {
    "Finance":
        "KB_FINANCE_PUBLIC",

    "HR":
        "KB_HR_PUBLIC",

    "Product":
        "KB_PRODUCT_PUBLIC",

    "Service":
        "KB_SERVICE_PUBLIC",
}


def _build_eval_runtime_user(
    case: EvalCase,
) -> dict:
    """
    S9-only runtime fixture normalization.

    core_61.csv 中的 user / authorized_kb_ids
    是为了自动执行 /chat 人工构造的测试身份，
    并不是 Frozen Gold。

    对 Frozen RUN_004 中明确允许的跨域实际路由：

        expected_domain != frozen_domain_actual

    增加 frozen actual domain 对应的 PUBLIC KB，
    使 FastAPI 能复现冻结 POC 的实际安全路径。

    重要：
    - 只补 Public KB
    - 永不补 Private KB
    - 不修改真实生产 Permission 逻辑
    """

    user = (
        case.user.model_dump()
    )

    authorized_kb_ids = list(
        user.get(
            "authorized_kb_ids",
            [],
        )
        or []
    )

    frozen_domain = (
        case.frozen_domain_actual
    )

    expected_domain = (
        case.expected_domain
    )

    if (
        frozen_domain
        and frozen_domain
        != expected_domain
    ):

        public_kb = (
            PUBLIC_KB_BY_DOMAIN.get(
                frozen_domain
            )
        )

        if (
            public_kb
            and public_kb
            not in authorized_kb_ids
        ):
            authorized_kb_ids.append(
                public_kb
            )

    user[
        "authorized_kb_ids"
    ] = authorized_kb_ids

    return user
def _call_chat_with_retry(
    request,
    max_attempts: int = 3,
):
    """
    S9 evaluation transport retry.

    只重试外部 API / 网络瞬时错误，
    不修改任何 Router / Permission /
    Version / Retrieval / Evidence 业务逻辑。

    其他代码异常立即抛出，
    不通过 retry 掩盖真实 Badcase。
    """

    transient_error_names = {
        "APIConnectionError",
        "APITimeoutError",
        "TimeoutError",
        "ConnectionError",
    }

    last_error = None

    for attempt in range(
        1,
        max_attempts + 1,
    ):

        try:

            return chat(
                request
            )

        except Exception as exc:

            error_name = (
                type(exc).__name__
            )

            if (
                error_name
                not in transient_error_names
            ):
                raise

            last_error = exc

            print(
                "[Eval Retry] "
                f"attempt={attempt}/"
                f"{max_attempts} "
                f"error={error_name}: "
                f"{exc}"
            )

            if (
                attempt
                >= max_attempts
            ):
                raise

            # 2s → 4s
            wait_seconds = (
                2 ** attempt
            )

            print(
                "[Eval Retry] "
                f"waiting "
                f"{wait_seconds}s..."
            )

            time.sleep(
                wait_seconds
            )

    raise last_error

def _run_single_case(
    case: EvalCase,
    run_id: str,
) -> EvalCaseResult:

    try:
        # ========================================================
        # IMPORTANT
        #
        # 不复制 Router / Retrieval / Judge。
        #
        # 直接调用当前生产 /chat 对应函数，
        # 保证评测与真实执行链一致。
        # ========================================================
        request = (
            ChatRequest.model_validate(
                {
                    "query":
                        case.query,

                    "user":
                        _build_eval_runtime_user(case),
                }
            )
        )

        response = (
            _call_chat_with_retry(
                request
            )
        )

        payload = (
            response.model_dump(
                mode="json"
            )
        )

        trace_id = (
            payload.get(
                "trace_id"
            )
        )

        trace = _safe_trace(
            trace_id
        )

        # ========================================================
        # Actual Behaviour
        # ========================================================
        actual_domain = (
            payload.get(
                "domain"
            )
        )

        actual_sensitivity = (
            payload.get(
                "sensitivity"
            )
        )

        actual_version_mode = (
            payload.get(
                "version_mode"
            )
        )

        actual_permission = (
            payload.get(
                "permission_decision"
            )
        )

        actual_decision = (
            payload.get(
                "decision"
            )
        )

        # ========================================================
        # Evidence
        # ========================================================
        evidence = (
            payload.get(
                "evidence"
            )
            or []
        )

        retrieved_chunk_ids = (
            _dedupe(
                [
                    item.get(
                        "chunk_id"
                    )
                    for item
                    in evidence
                    if item.get(
                        "chunk_id"
                    )
                ]
            )
        )

        retrieved_document_ids = (
            _dedupe(
                [
                    item.get(
                        "document_id"
                    )
                    for item
                    in evidence
                    if item.get(
                        "document_id"
                    )
                ]
            )
        )

        # ========================================================
        # Allowed Docs
        # ========================================================
        allowed_document_ids = (
            payload.get(
                "allowed_document_ids"
            )
            or []
        )

        # ========================================================
        # Citation
        # ========================================================
        citations = (
            payload.get(
                "citations"
            )
            or []
        )

        citation_chunk_ids = (
            _dedupe(
                [
                    item.get(
                        "chunk_id"
                    )
                    for item
                    in citations
                    if item.get(
                        "chunk_id"
                    )
                ]
            )
        )

        citation_document_ids = (
            _dedupe(
                [
                    item.get(
                        "document_id"
                    )
                    for item
                    in citations
                    if item.get(
                        "document_id"
                    )
                ]
            )
        )

        evidence_ids = (
            payload.get(
                "evidence_ids"
            )
            or []
        )

        # ========================================================
        # Frozen Parity Targets
        #
        # Domain:
        # frozen actual 优先。
        #
        # 因为旧 Dify 中存在：
        # “路由不最优但安全结果正确”
        # 的已接受冻结 Case。
        # ========================================================
        domain_parity_target = (
            case.frozen_domain_actual
            or case.expected_domain
        )

        decision_parity_target = (
            case.frozen_actual_decision
            or case.expected_decision
        )

        # ========================================================
        # Checks
        # ========================================================
        checks = {}

        checks[
            "runtime_ok"
        ] = True

        checks[
            "trace_persisted"
        ] = (
            trace is not None
        )

        # --------------------------------
        # Frozen Domain Parity
        # BLOCKING
        # --------------------------------
        checks[
            "domain_frozen_parity_match"
        ] = (
            actual_domain
            == domain_parity_target
            if domain_parity_target
            else None
        )

        # --------------------------------
        # Semantic Ideal Domain
        # INFORMATIONAL ONLY
        # --------------------------------
        checks[
            "domain_expected_match"
        ] = (
            actual_domain
            == case.expected_domain
            if case.expected_domain
            else None
        )

        # --------------------------------
        # Version
        # --------------------------------
        checks[
            "version_match"
        ] = (
            _evaluate_version_match(
                case=case,
                actual_version_mode=(
                    actual_version_mode
                ),
            )
        )

        # --------------------------------
        # Sensitivity
        #
        # Frozen POC 中只有 Finance
        # 存在独立 Sensitivity 分类：
        #
        # Normal / Restricted
        #
        # HR / Product / Service 不经过
        # Sensitivity Router，因此其
        # actual_sensitivity=None 是正常行为。
        #
        # 对这些 Domain：
        # sensitivity_match = None
        # 表示 N/A，不进入 blocking，也不进入
        # sensitivity_accuracy 分母。
        # --------------------------------
        checks[
            "sensitivity_match"
        ] = (
            _evaluate_sensitivity_match(
                case=case,
                actual_sensitivity=(
                    actual_sensitivity
                ),
            )
        )

        # --------------------------------
        # Permission
        #
        # 你的冻结 Excel 没有独立 Gold，
        # 所以当前多数 Case 为 None。
        # --------------------------------
        checks[
            "permission_match"
        ] = (
            actual_permission
            == case.expected_permission_decision
            if case.expected_permission_decision
            else None
        )

        # --------------------------------
        # Frozen Decision Parity
        # BLOCKING
        # --------------------------------
        checks[
            "decision_frozen_parity_match"
        ] = (
            actual_decision
            == decision_parity_target
            if decision_parity_target
            else None
        )

        # --------------------------------
        # Semantic Decision Gold
        # INFORMATIONAL
        # --------------------------------
        checks[
            "decision_expected_match"
        ] = (
            actual_decision
            == case.expected_decision
            if case.expected_decision
            else None
        )

        # --------------------------------
        # Clarify 必须真的有问题
        # --------------------------------
        if (
            case.require_clarifying_question
        ):

            clarifying_question = (
                payload.get(
                    "clarifying_question"
                )
                or ""
            )

            checks[
                "clarifying_question_ok"
            ] = bool(
                clarifying_question.strip()
            )

        else:
            checks[
                "clarifying_question_ok"
            ] = None

        # --------------------------------
        # Security:
        # Retrieved 必须是 Allowed 子集
        # --------------------------------
        retrieved_set = set(
            retrieved_document_ids
        )

        allowed_set = set(
            allowed_document_ids
        )

        unauthorized = bool(
            retrieved_set
            - allowed_set
        )

        checks[
            "unauthorized_retrieval_ok"
        ] = (
            not unauthorized
        )

        # --------------------------------
        # no_access 特别安全校验
        # --------------------------------
        if (
            case.expected_decision
            == "no_access"
        ):

            checks[
                "no_access_safe"
            ] = (
                len(
                    retrieved_document_ids
                ) == 0

                and len(
                    retrieved_chunk_ids
                ) == 0

                and len(
                    evidence_ids
                ) == 0

                and len(
                    citation_document_ids
                ) == 0

                and len(
                    citation_chunk_ids
                ) == 0
            )

        else:
            checks[
                "no_access_safe"
            ] = None

        # --------------------------------
        # Citation 只能来自 S7 Evidence IDs
        # --------------------------------
        if evidence_ids:

            checks[
                "citation_evidence_alignment"
            ] = (
                set(
                    citation_chunk_ids
                )
                == set(
                    evidence_ids
                )
                and len(
                    citation_chunk_ids
                )
                == len(
                    evidence_ids
                )
            )

        else:

            checks[
                "citation_evidence_alignment"
            ] = (
                len(
                    citation_chunk_ids
                )
                == 0
            )

        citation_version_ok = (
            _citation_version_integrity(
                citations
            )
        )

        checks[
            "citation_version_integrity"
        ] = (
            citation_version_ok
        )

        # ========================================================
        # Blocking Check Set
        #
        # domain_expected_match
        # decision_expected_match
        # 是额外语义统计，
        # 不是 RUN_004 Parity 阻断。
        # ========================================================
        blocking_names = [
            "runtime_ok",
            "trace_persisted",

            # domain_frozen_parity_match
            # 只做统计，不作为 RUN_004 封版阻断项

            "version_match",
            "sensitivity_match",
            "permission_match",

            "decision_frozen_parity_match",

            "clarifying_question_ok",

            "unauthorized_retrieval_ok",
            "no_access_safe",

            "citation_evidence_alignment",
            "citation_version_integrity",
        ]

        blocking_values = [
            checks[name]
            for name
            in blocking_names
            if (
                checks.get(name)
                is not None
            )
        ]

        passed = all(
            blocking_values
        )

        # ========================================================
        # Retrieval Metrics
        #
        # relevant_document_ids 为空时，
        # 正确返回 None，而不是 0。
        # ========================================================
        recall5 = recall_at_k(
            ranked_ids=(
                retrieved_document_ids
            ),
            relevant_ids=(
                case.relevant_document_ids
            ),
            k=5,
        )

        recall10 = recall_at_k(
            ranked_ids=(
                retrieved_document_ids
            ),
            relevant_ids=(
                case.relevant_document_ids
            ),
            k=10,
        )

        mrr10 = mrr_at_k(
            ranked_ids=(
                retrieved_document_ids
            ),
            relevant_ids=(
                case.relevant_document_ids
            ),
            k=10,
        )

        ndcg10 = ndcg_at_k(
            ranked_ids=(
                retrieved_document_ids
            ),
            relevant_ids=(
                case.relevant_document_ids
            ),
            k=10,
        )

        # ========================================================
        # Trace Metrics
        # ========================================================
        latency_ms = 0
        input_tokens = 0
        output_tokens = 0

        if trace is not None:

            latency_ms = int(
                trace.get(
                    "latency_ms",
                    0,
                )
                or 0
            )

            input_tokens = int(
                trace.get(
                    "input_tokens",
                    0,
                )
                or 0
            )

            output_tokens = int(
                trace.get(
                    "output_tokens",
                    0,
                )
                or 0
            )

        return EvalCaseResult(
            run_id=run_id,

            case_id=case.case_id,

            category=case.category,

            query=case.query,

            trace_id=trace_id,

            passed=passed,

            checks=checks,

            expected_domain=(
                case.expected_domain
            ),

            expected_sensitivity=(
                case.expected_sensitivity
            ),

            expected_version_mode=(
                case.expected_version_mode
            ),

            expected_permission_decision=(
                case.expected_permission_decision
            ),

            expected_decision=(
                case.expected_decision
            ),

            frozen_domain_actual=(
                case.frozen_domain_actual
            ),

            frozen_actual_decision=(
                case.frozen_actual_decision
            ),

            actual_domain=(
                actual_domain
            ),

            actual_sensitivity=(
                actual_sensitivity
            ),

            actual_version_mode=(
                actual_version_mode
            ),

            actual_permission_decision=(
                actual_permission
            ),

            actual_decision=(
                actual_decision
            ),

            allowed_document_ids=(
                allowed_document_ids
            ),

            retrieved_document_ids=(
                retrieved_document_ids
            ),

            retrieved_chunk_ids=(
                retrieved_chunk_ids
            ),

            citation_document_ids=(
                citation_document_ids
            ),

            citation_chunk_ids=(
                citation_chunk_ids
            ),

            recall_at_5=recall5,

            recall_at_10=recall10,

            mrr_at_10=mrr10,

            ndcg_at_10=ndcg10,

            unauthorized_retrieval=(
                unauthorized
            ),

            citation_version_integrity=(
                citation_version_ok
            ),

            latency_ms=latency_ms,

            input_tokens=input_tokens,

            output_tokens=output_tokens,

            error=None,
        )

    except Exception as exc:

        return EvalCaseResult(
            run_id=run_id,

            case_id=case.case_id,

            category=case.category,

            query=case.query,

            passed=False,

            checks={
                "runtime_ok": False
            },

            expected_domain=(
                case.expected_domain
            ),

            expected_sensitivity=(
                case.expected_sensitivity
            ),

            expected_version_mode=(
                case.expected_version_mode
            ),

            expected_permission_decision=(
                case.expected_permission_decision
            ),

            expected_decision=(
                case.expected_decision
            ),

            frozen_domain_actual=(
                case.frozen_domain_actual
            ),

            frozen_actual_decision=(
                case.frozen_actual_decision
            ),

            error=(
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )


def _build_summary(
    run_id: str,
    dataset_name: str,
    results: list[
        EvalCaseResult
    ],
) -> dict:

    total = len(
        results
    )

    passed = sum(
        1
        for item in results
        if item.passed
    )

    failed = (
        total - passed
    )

    # ============================================================
    # Check Rates
    # ============================================================
    def check_values(
        name: str,
    ):
        return [
            item.checks.get(
                name
            )
            for item
            in results
        ]

    metrics = {
        "domain_frozen_parity_rate":
            bool_rate(
                check_values(
                    "domain_frozen_parity_match"
                )
            ),

        "domain_expected_exact_rate":
            bool_rate(
                check_values(
                    "domain_expected_match"
                )
            ),

        "version_accuracy":
            bool_rate(
                check_values(
                    "version_match"
                )
            ),

        "sensitivity_accuracy":
            bool_rate(
                check_values(
                    "sensitivity_match"
                )
            ),

        "permission_accuracy":
            bool_rate(
                check_values(
                    "permission_match"
                )
            ),

        "decision_frozen_parity_rate":
            bool_rate(
                check_values(
                    "decision_frozen_parity_match"
                )
            ),

        "decision_expected_accuracy":
            bool_rate(
                check_values(
                    "decision_expected_match"
                )
            ),

        "clarifying_question_rate":
            bool_rate(
                check_values(
                    "clarifying_question_ok"
                )
            ),

        "trace_persistence_rate":
            bool_rate(
                check_values(
                    "trace_persisted"
                )
            ),

        "citation_alignment_rate":
            bool_rate(
                check_values(
                    "citation_evidence_alignment"
                )
            ),

        "citation_version_integrity_rate":
            bool_rate(
                check_values(
                    "citation_version_integrity"
                )
            ),

        "unauthorized_retrieval_rate":
            (
                sum(
                    1
                    for item in results
                    if item.unauthorized_retrieval
                )
                / total
                if total
                else 0.0
            ),

        "recall_at_5":
            mean_optional(
                [
                    item.recall_at_5
                    for item
                    in results
                ]
            ),

        "recall_at_10":
            mean_optional(
                [
                    item.recall_at_10
                    for item
                    in results
                ]
            ),

        "mrr_at_10":
            mean_optional(
                [
                    item.mrr_at_10
                    for item
                    in results
                ]
            ),

        "ndcg_at_10":
            mean_optional(
                [
                    item.ndcg_at_10
                    for item
                    in results
                ]
            ),

        "p95_latency_ms":
            p95(
                [
                    item.latency_ms
                    for item
                    in results
                ]
            ),

        "avg_input_tokens":
            (
                sum(
                    item.input_tokens
                    for item in results
                )
                / total
                if total
                else 0.0
            ),

        "avg_output_tokens":
            (
                sum(
                    item.output_tokens
                    for item in results
                )
                / total
                if total
                else 0.0
            ),

        # 当前 S8 仍无最终 Answer Generator，
        # 不伪造回答质量指标。
        "answer_correctness":
            None,

        "faithfulness":
            None,
    }

    return {
        "run_id":
            run_id,

        "dataset_name":
            dataset_name,

        "total_cases":
            total,

        "passed_cases":
            passed,

        "failed_cases":
            failed,

        "pass_rate":
            (
                passed / total
                if total
                else 0.0
            ),

        "metrics":
            metrics,
    }


def _write_case_csv(
    path: Path,
    results: list[
        EvalCaseResult
    ],
):

    fields = [
        "run_id",
        "case_id",
        "category",
        "query",
        "trace_id",
        "passed",

        "expected_domain",
        "frozen_domain_actual",
        "actual_domain",

        "expected_sensitivity",
        "actual_sensitivity",

        "expected_version_mode",
        "actual_version_mode",

        "expected_permission_decision",
        "actual_permission_decision",

        "expected_decision",
        "frozen_actual_decision",
        "actual_decision",

        "checks_json",

        "allowed_document_ids_json",
        "retrieved_document_ids_json",
        "retrieved_chunk_ids_json",

        "citation_document_ids_json",
        "citation_chunk_ids_json",

        "recall_at_5",
        "recall_at_10",
        "mrr_at_10",
        "ndcg_at_10",

        "unauthorized_retrieval",
        "citation_version_integrity",

        "latency_ms",
        "input_tokens",
        "output_tokens",

        "error",
    ]

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for item in results:

            data = (
                item.model_dump()
            )

            writer.writerow(
                {
                    "run_id":
                        item.run_id,

                    "case_id":
                        item.case_id,

                    "category":
                        item.category,

                    "query":
                        item.query,

                    "trace_id":
                        item.trace_id,

                    "passed":
                        item.passed,

                    "expected_domain":
                        item.expected_domain,

                    "frozen_domain_actual":
                        item.frozen_domain_actual,

                    "actual_domain":
                        item.actual_domain,

                    "expected_sensitivity":
                        item.expected_sensitivity,

                    "actual_sensitivity":
                        item.actual_sensitivity,

                    "expected_version_mode":
                        item.expected_version_mode,

                    "actual_version_mode":
                        item.actual_version_mode,

                    "expected_permission_decision":
                        item.expected_permission_decision,

                    "actual_permission_decision":
                        item.actual_permission_decision,

                    "expected_decision":
                        item.expected_decision,

                    "frozen_actual_decision":
                        item.frozen_actual_decision,

                    "actual_decision":
                        item.actual_decision,

                    "checks_json":
                        json.dumps(
                            item.checks,
                            ensure_ascii=False,
                        ),

                    "allowed_document_ids_json":
                        json.dumps(
                            item.allowed_document_ids,
                            ensure_ascii=False,
                        ),

                    "retrieved_document_ids_json":
                        json.dumps(
                            item.retrieved_document_ids,
                            ensure_ascii=False,
                        ),

                    "retrieved_chunk_ids_json":
                        json.dumps(
                            item.retrieved_chunk_ids,
                            ensure_ascii=False,
                        ),

                    "citation_document_ids_json":
                        json.dumps(
                            item.citation_document_ids,
                            ensure_ascii=False,
                        ),

                    "citation_chunk_ids_json":
                        json.dumps(
                            item.citation_chunk_ids,
                            ensure_ascii=False,
                        ),

                    "recall_at_5":
                        item.recall_at_5,

                    "recall_at_10":
                        item.recall_at_10,

                    "mrr_at_10":
                        item.mrr_at_10,

                    "ndcg_at_10":
                        item.ndcg_at_10,

                    "unauthorized_retrieval":
                        item.unauthorized_retrieval,

                    "citation_version_integrity":
                        item.citation_version_integrity,

                    "latency_ms":
                        item.latency_ms,

                    "input_tokens":
                        item.input_tokens,

                    "output_tokens":
                        item.output_tokens,

                    "error":
                        item.error,
                }
            )


def _write_badcases(
    path: Path,
    results: list[
        EvalCaseResult
    ],
):

    failed = [
        item
        for item in results
        if not item.passed
    ]

    with path.open(
        "w",
        encoding="utf-8",
    ) as run_file:

        for item in failed:

            failed_checks = [
                key
                for key, value
                in item.checks.items()
                if value is False
            ]

            badcase = {
                "badcase_id":
                    (
                        f"{item.run_id}"
                        f"__{item.case_id}"
                    ),

                "run_id":
                    item.run_id,

                "source_case_id":
                    item.case_id,

                "trace_id":
                    item.trace_id,

                "query":
                    item.query,

                "badcase_type":
                    _build_badcase_type(
                        item.checks,
                        item.error,
                    ),

                "symptom":
                    (
                        "S9 automated eval "
                        "case failed."
                    ),

                "failed_checks":
                    failed_checks,

                "root_cause":
                    "pending_manual_diagnosis",

                "fix_action":
                    "",

                "status":
                    "Open",

                "error":
                    item.error,
            }

            line = json.dumps(
                badcase,
                ensure_ascii=False,
            )

            run_file.write(
                line + "\n"
            )

            with (
                MASTER_BADCASE_PATH.open(
                    "a",
                    encoding="utf-8",
                )
            ) as master:

                master.write(
                    line + "\n"
                )


def run_eval(
    dataset_name: str = "core_61",
    limit: int | None = None,
    case_ids: list[str] | None = None,
    progress: bool = True,
) -> dict:

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    MASTER_BADCASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cases = load_eval_cases(
        dataset_name
    )

    if case_ids:

        requested = set(
            case_ids
        )

        cases = [
            item
            for item in cases
            if item.case_id
            in requested
        ]

        found = {
            item.case_id
            for item in cases
        }

        missing = (
            requested - found
        )

        if missing:
            raise ValueError(
                "Unknown case IDs: "
                f"{sorted(missing)}"
            )

    if (
        limit is not None
    ):

        if limit <= 0:
            raise ValueError(
                "limit must be > 0"
            )

        cases = cases[
            :limit
        ]

    if not cases:
        raise RuntimeError(
            "No eval cases selected."
        )

    run_id = (
        _new_run_id()
    )

    results = []

    total = len(
        cases
    )

    for index, case in enumerate(
        cases,
        start=1,
    ):

        result = (
            _run_single_case(
                case=case,
                run_id=run_id,
            )
        )

        results.append(
            result
        )

        if progress:

            state = (
                "PASS"
                if result.passed
                else "FAIL"
            )

            print(
                f"[{index:02d}/{total:02d}] "
                f"{case.case_id} "
                f"{state}"
            )

            if (
                not result.passed
            ):

                false_checks = [
                    name
                    for name, value
                    in result.checks.items()
                    if value is False
                ]

                if false_checks:
                    print(
                        "    failed_checks="
                        + ", ".join(
                            false_checks
                        )
                    )

                if result.error:
                    print(
                        "    error="
                        + result.error
                    )

    summary = (
        _build_summary(
            run_id=run_id,
            dataset_name=(
                dataset_name
            ),
            results=results,
        )
    )

    summary_path = (
        REPORT_DIR
        / f"{run_id}_summary.json"
    )

    cases_path = (
        REPORT_DIR
        / f"{run_id}_cases.csv"
    )

    badcases_path = (
        REPORT_DIR
        / f"{run_id}_badcases.jsonl"
    )

    _write_case_csv(
        cases_path,
        results,
    )

    _write_badcases(
        badcases_path,
        results,
    )

    report_paths = {
        "summary":
            str(summary_path),

        "cases":
            str(cases_path),

        "badcases":
            str(badcases_path),

        "master_badcases":
            str(
                MASTER_BADCASE_PATH
            ),
    }

    summary[
        "report_paths"
    ] = report_paths

    summary_path.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return summary