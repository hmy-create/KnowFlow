from datetime import date

from pydantic import BaseModel, Field

from app.models.citation import Citation


class Trace(BaseModel):
    """
    KnowFlow S8 Trace Model

    用于完整记录一次 /chat 请求从：
    Router
    → Permission
    → Version
    → Retrieval
    → Rerank
    → Evidence Decision
    → Citation

    的完整执行链路。

    目标：
    给定一个 trace_id，
    可以还原一次请求发生了什么。
    """

    # ============================================================
    # Trace Identity
    # ============================================================
    trace_id: str = Field(
        ...,
        description="一次请求的唯一 Trace ID",
    )

    # ============================================================
    # Request
    # ============================================================
    query: str = Field(
        ...,
        description="用户原始 Query",
    )

    user_id: str = Field(
        ...,
        description="本次请求对应的用户 ID",
    )

    # ============================================================
    # S3 Router
    # ============================================================
    domain: str = Field(
        ...,
        description="Router 最终识别的业务域",
    )

    sensitivity: str | None = Field(
        default=None,
        description=(
            "知识敏感级别，"
            "例如 Normal / Restricted"
        ),
    )

    version_mode: str | None = Field(
        default=None,
        description=(
            "版本模式，"
            "例如 Current / Historical / Comparison"
        ),
    )

    # ============================================================
    # S5 Query Time Context
    # ============================================================
    query_date: date | None = Field(
        default=None,
        description=(
            "从 Query 中解析出的具体查询日期"
        ),
    )

    # ============================================================
    # S4 Permission Filter
    # ============================================================
    permission_filter: dict = Field(
        default_factory=dict,
        description=(
            "权限过滤过程与结果"
        ),
    )

    # ============================================================
    # S5 Version Filter
    # ============================================================
    version_filter: dict = Field(
        default_factory=dict,
        description=(
            "版本过滤过程与结果"
        ),
    )

    # ============================================================
    # S6 Retrieval
    #
    # 这里不能只存 chunk_id。
    # 后续 S9 需要知道：
    # retrieval_source
    # raw_score
    # fused_score
    # rerank_score
    # ============================================================
    retrieved_chunks: list[dict] = Field(
        default_factory=list,
        description=(
            "S6 最终参与 Evidence 判断的"
            "检索候选 Chunk 及其检索信息"
        ),
    )

    rerank_scores: list[dict] = Field(
        default_factory=list,
        description=(
            "Chunk 与对应 Rerank Score"
        ),
    )

    # ============================================================
    # S7 Evidence State Machine
    # ============================================================
    decision: str = Field(
        ...,
        description=(
            "Evidence State："
            "answer / clarify / conflict / "
            "refuse / no_access"
        ),
    )

    decision_reason: str = Field(
        default="",
        description=(
            "Evidence State Machine 的判断原因"
        ),
    )

    clarifying_question: str = Field(
        default="",
        description=(
            "decision=clarify 时生成的澄清问题；"
            "其他状态必须为空字符串"
        ),
    )

    evidence_ids: list[str] = Field(
        default_factory=list,
        description=(
            "S7 最终采用的真实 Chunk ID"
        ),
    )

    # ============================================================
    # S8 Citation
    # ============================================================
    citations: list[Citation] = Field(
        default_factory=list,
        description=(
            "由真实 Chunk 映射得到的 Citation Chain"
        ),
    )

    # ============================================================
    # Observability
    # ============================================================
    latency_ms: int = Field(
        default=0,
        ge=0,
        description=(
            "本次请求总耗时，单位毫秒"
        ),
    )

    input_tokens: int = Field(
        default=0,
        ge=0,
        description=(
            "本次请求实际调用 LLM 时的输入 Token 数；"
            "未调用 LLM 时为 0"
        ),
    )

    output_tokens: int = Field(
        default=0,
        ge=0,
        description=(
            "本次请求实际调用 LLM 时的输出 Token 数；"
            "未调用 LLM 时为 0"
        ),
    )

    # ============================================================
    # Prompt / Baseline Version
    # ============================================================
    prompt_version: str = Field(
        default="baseline-v1",
        description=(
            "当前使用的冻结 Prompt / Baseline 版本"
        ),
    )


# ================================================================
# Compatibility Alias
#
# S8 后续 Repository 使用 TraceRecord 命名时，
# 不需要再定义第二套数据结构。
#
# Trace 与 TraceRecord 完全是同一个 Model。
# ================================================================
TraceRecord = Trace