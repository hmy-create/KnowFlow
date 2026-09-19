import json
import os
from pathlib import Path

from dotenv import load_dotenv
from zhipuai import ZhipuAI

from app.core.evidence_context import (
    build_evidence_context,
)
from app.models import (
    EvidenceDecision,
    RetrievalCandidate,
)


REPO_ROOT = Path(
    __file__
).resolve().parents[3]

PROMPT_DIR = (
    REPO_ROOT
    / "prompts"
    / "baseline"
    / "evidence_judge"
)

load_dotenv(
    REPO_ROOT / ".env"
)


DOMAIN_PROMPTS = {
    "HR": "hr.txt",
    "Finance": "finance.txt",
    "Product": "product.txt",
    "Service": "service.txt",
}


MIGRATION_OUTPUT_CONTRACT = """
在不改变以上冻结判定规则的前提下，
FastAPI 迁移要求你只输出 JSON。

必须严格输出以下字段：

{
  "decision": "answer|clarify|conflict|refuse",
  "reason": "判断原因",
  "clarifying_question": "",
  "evidence_ids": []
}

要求：

1. decision 只能是：
   answer / clarify / conflict / refuse

2. clarifying_question：
   只有 decision=clarify 时可以非空；
   其他情况必须为空字符串。

3. evidence_ids：
   只能填写输入证据中真实存在的
   EVIDENCE_ID。
   不得编造 ID。

4. 你只负责证据状态判断，
   不得直接回答用户的业务问题。

5. 不要输出 Markdown。
不要使用 ```json 代码块。
只输出合法 JSON。
"""


def load_evidence_prompt(
    domain: str,
) -> str:

    filename = (
        DOMAIN_PROMPTS.get(domain)
    )

    if filename is None:
        raise ValueError(
            f"No Evidence Judge prompt "
            f"for domain: {domain}"
        )

    path = PROMPT_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            path
        )

    return path.read_text(
        encoding="utf-8"
    )


def _extract_json(
    raw: str,
) -> dict:

    raw = raw.strip()

    first = raw.find("{")
    last = raw.rfind("}")

    if (
        first == -1
        or last == -1
        or last < first
    ):
        raise ValueError(
            "Evidence Judge did not "
            "return valid JSON."
        )

    return json.loads(
        raw[first:last + 1]
    )

def _normalize_evidence_id(
    evidence_id: str,
) -> str:

    value = str(
        evidence_id
    ).strip()

    prefix = "EVIDENCE_ID="

    if value.startswith(prefix):
        value = value[
            len(prefix):
        ].strip()

    return value

def judge_current_evidence(
    query: str,
    domain: str,
    evidence: list[
        RetrievalCandidate
    ],
    query_time_summary: str = "",
) -> EvidenceDecision:

    if not evidence:
        return EvidenceDecision(
            decision="refuse",
            reason=(
                "没有检索到足够相关的"
                "企业知识证据。"
            ),
            clarifying_question="",
            evidence_ids=[],
        )

    api_key = os.getenv(
        "ZHIPUAI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "ZHIPUAI_API_KEY is missing."
        )

    model = os.getenv(
        "ZHIPUAI_MODEL",
        "glm-4.7-flash",
    )

    client = ZhipuAI(
        api_key=api_key
    )

    frozen_prompt = (
        load_evidence_prompt(domain)
    )

    evidence_context = (
        build_evidence_context(
            evidence
        )
    )

    evidence_marker = "【企业知识库证据】"

    if evidence_marker in frozen_prompt:

        # 如果冻结 Prompt 本身预留了证据位置，
        # 就把真实 Evidence 注入该位置。
        prompt_with_context = (
            frozen_prompt.replace(
                evidence_marker,
                (
                    evidence_marker
                    + "\n"
                    + evidence_context
                ),
                1,
            )
        )

    else:

        # 某些冻结 Prompt 没有显式证据 marker。
        # 不修改其原有业务规则，
        # 只在末尾追加经过 S4/S5/S6
        # 筛选后的真实企业证据。
        prompt_with_context = (
            frozen_prompt
            + "\n\n"
            + "【企业知识库证据】"
            + "\n"
            + evidence_context
        )

    system_prompt = (
        prompt_with_context
        + "\n\n"
        + MIGRATION_OUTPUT_CONTRACT
    )

    user_message = f"""
    用户问题：
    {query}

    查询时间上下文：
    {query_time_summary or "未额外提供"}

    请严格依据系统消息中提供的企业知识库证据，
    只进行 Evidence State 判断。
    """

    response = (
        client.chat.completions.create(
            model=model,

            # FastAPI 迁移为了结构化回归稳定性
            # 使用确定性输出；
            # 不修改冻结业务决策规则。
            temperature=0.0,

            messages=[
                {
                    "role": "system",
                    "content":
                        system_prompt,
                },
                {
                    "role": "user",
                    "content":
                        user_message,
                },
            ],
        )
    )

    raw = (
        response
        .choices[0]
        .message
        .content
    )
    print("")
    print(
        f"[Evidence Judge Debug] "
        f"domain={domain}"
    )
    print(
        f"[Evidence Judge Debug] "
        f"query={query}"
    )

    for item in evidence:
        print(
            "[Evidence Judge Debug] "
            f"chunk={item.chunk_id} | "
            f"doc={item.document_id} | "
            f"section={item.section} | "
            f"rerank={item.rerank_score}"
        )

        print(
            "[Evidence Judge Debug] "
            f"text={item.text[:300]}"
        )

    print(
        f"[Evidence Judge Debug] "
        f"raw={raw}"
    )

    payload = _extract_json(raw)

    raw_evidence_ids = (
        payload.get(
            "evidence_ids",
            [],
        )
    )

    normalized_evidence_ids = [
        _normalize_evidence_id(
            evidence_id
        )
        for evidence_id
        in raw_evidence_ids
    ]


    decision = EvidenceDecision(
        decision=payload["decision"],
        reason=payload["reason"],
        clarifying_question=(
            payload.get(
                "clarifying_question",
                "",
            )
        ),
        evidence_ids=(
            normalized_evidence_ids
        ),
    )

    # -----------------------------
    # 输出约束校验
    # -----------------------------
    valid_ids = {
        item.chunk_id
        for item in evidence
    }

    unknown_ids = [
        evidence_id
        for evidence_id
        in decision.evidence_ids
        if evidence_id
        not in valid_ids
    ]

    if unknown_ids:

        decision.evidence_ids = [
            evidence_id
            for evidence_id
            in decision.evidence_ids
            if evidence_id
            in valid_ids
        ]

        decision.risk_flags.append(
            "invalid_evidence_id_removed"
        )

    if (
        decision.decision
        != "clarify"
    ):
        decision.clarifying_question = ""

    return decision