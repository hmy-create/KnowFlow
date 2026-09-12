import os
from pathlib import Path

from dotenv import load_dotenv
from zhipuai import ZhipuAI


REPO_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(REPO_ROOT / ".env")


def load_router_prompt(filename: str) -> str:
    prompt_path = (
        REPO_ROOT
        / "prompts"
        / "baseline"
        / "routers"
        / filename
    )

    return prompt_path.read_text(encoding="utf-8")


def classify_label(
    query: str,
    prompt_filename: str,
    allowed_labels: list[str],
) -> str:

    api_key = os.getenv("ZHIPUAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "ZHIPUAI_API_KEY 未配置，请检查项目根目录 .env"
        )

    model = os.getenv(
        "ZHIPUAI_MODEL",
        "glm-4.7-flash",
    )

    client = ZhipuAI(api_key=api_key)

    system_prompt = load_router_prompt(prompt_filename)

    response = client.chat.completions.create(
        model=model,
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
    )

    raw = response.choices[0].message.content.strip()

    print(
    f"[Router Debug] "
    f"prompt={prompt_filename} | "
    f"query={query} | "
    f"raw={raw}"
)

    # 先尝试完全匹配
    for label in allowed_labels:
        if raw.lower() == label.lower():
            return label

    # 防止模型输出 “分类结果：HR”
    for label in allowed_labels:
        if label.lower() in raw.lower():
            return label

    raise ValueError(
        f"Router 输出无法解析：{raw}. "
        f"允许值：{allowed_labels}"
    )