from pydantic import BaseModel, Field


class EvalUser(BaseModel):
    user_id: str
    department: str
    role: str

    authorized_kb_ids: list[str] = Field(
        default_factory=list
    )


class EvalCase(BaseModel):
    # ============================================================
    # Identity
    # ============================================================
    case_id: str

    set_name: str = "core_61"

    category: str = ""

    query: str

    user: EvalUser

    # ============================================================
    # Semantic Gold
    # ============================================================
    expected_domain: str | None = None

    expected_sensitivity: str | None = None

    expected_version_mode: str | None = None

    expected_permission_decision: str | None = None

    expected_decision: str | None = None

    # ============================================================
    # Retrieval Gold
    # ============================================================
    relevant_document_ids: list[str] = Field(
        default_factory=list
    )

    relevant_chunk_ids: list[str] = Field(
        default_factory=list
    )

    # ============================================================
    # Citation Gold
    # ============================================================
    expected_citation_document_ids: list[str] = Field(
        default_factory=list
    )

    expected_citation_chunk_ids: list[str] = Field(
        default_factory=list
    )

    require_clarifying_question: bool = False

    # ============================================================
    # Frozen Answer / Source Information
    # ============================================================
    expected_answer_keypoints: str = ""

    expected_source: str = ""

    route_expectation: str = ""

    notes: str = ""

    # ============================================================
    # Frozen Dify RUN_004 Actual Behaviour
    #
    # 这部分非常重要。
    # S9 FastAPI Parity 使用 frozen actual，
    # 而不是强制所有 Case 都符合理想 domain_expected。
    # ============================================================
    frozen_stage: str = ""

    frozen_domain_actual: str | None = None

    frozen_actual_decision: str | None = None

    frozen_actual_result_summary: str = ""

    frozen_actual_source: str = ""

    frozen_route_actual: str = ""

    frozen_pass: bool = True

    test_type: str = ""


class EvalCaseResult(BaseModel):
    run_id: str

    case_id: str

    category: str = ""

    query: str

    trace_id: str | None = None

    passed: bool = False

    checks: dict = Field(
        default_factory=dict
    )

    # ============================================================
    # Expected
    # ============================================================
    expected_domain: str | None = None

    expected_sensitivity: str | None = None

    expected_version_mode: str | None = None

    expected_permission_decision: str | None = None

    expected_decision: str | None = None

    frozen_domain_actual: str | None = None

    frozen_actual_decision: str | None = None

    # ============================================================
    # Actual
    # ============================================================
    actual_domain: str | None = None

    actual_sensitivity: str | None = None

    actual_version_mode: str | None = None

    actual_permission_decision: str | None = None

    actual_decision: str | None = None

    # ============================================================
    # Retrieval / Citation
    # ============================================================
    allowed_document_ids: list[str] = Field(
        default_factory=list
    )

    retrieved_document_ids: list[str] = Field(
        default_factory=list
    )

    retrieved_chunk_ids: list[str] = Field(
        default_factory=list
    )

    citation_document_ids: list[str] = Field(
        default_factory=list
    )

    citation_chunk_ids: list[str] = Field(
        default_factory=list
    )

    # ============================================================
    # Retrieval Metrics
    # ============================================================
    recall_at_5: float | None = None

    recall_at_10: float | None = None

    mrr_at_10: float | None = None

    ndcg_at_10: float | None = None

    # ============================================================
    # Safety / Citation
    # ============================================================
    unauthorized_retrieval: bool = False

    citation_version_integrity: bool | None = None

    # ============================================================
    # Observability
    # ============================================================
    latency_ms: int = 0

    input_tokens: int = 0

    output_tokens: int = 0

    error: str | None = None


class EvalRunSummary(BaseModel):
    run_id: str

    dataset_name: str

    total_cases: int

    passed_cases: int

    failed_cases: int

    pass_rate: float

    metrics: dict = Field(
        default_factory=dict
    )

    report_paths: dict = Field(
        default_factory=dict
    )