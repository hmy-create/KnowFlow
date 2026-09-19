import re
from pathlib import Path

from docx import Document


REPO_ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    REPO_ROOT
    / "prompts"
    / "baseline"
    / "KnowFlow_Dify_POC_Prompt_Baseline.docx"
)

OUTPUT_DIR = (
    REPO_ROOT
    / "prompts"
    / "baseline"
    / "evidence_judge"
)


TARGET_MARKERS = {
    "hr": "EVIDENCE_JUDGE_HR:",
    "finance": "EVIDENCE_JUDGE_FINANCE:",
    "product": "EVIDENCE_JUDGE_PRODUCT:",
    "service": "EVIDENCE_JUDGE_SERVICE:",
}


def normalize(text: str) -> str:
    return " ".join(
        text.replace("\n", " ").split()
    )


def is_prompt_marker(text: str) -> bool:
    return bool(
        re.match(
            r"^[A-Za-z0-9_]+:$",
            text.strip(),
        )
    )


def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Frozen prompt file not found: {SOURCE}"
        )

    doc = Document(SOURCE)

    paragraphs = [
        normalize(p.text)
        for p in doc.paragraphs
        if normalize(p.text)
    ]

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    normalized_targets = {
        key: value.upper()
        for key, value
        in TARGET_MARKERS.items()
    }

    extracted = {}

    for name, target in normalized_targets.items():

        collecting = False
        lines = []

        for text in paragraphs:

            upper = text.upper()

            if upper == target:
                collecting = True
                continue

            if collecting and is_prompt_marker(text):
                break

            if collecting:
                lines.append(text)

        if not lines:
            raise RuntimeError(
                f"Prompt not found: {target}"
            )

        extracted[name] = "\n".join(lines)

    for name, content in extracted.items():

        path = (
            OUTPUT_DIR
            / f"{name}.txt"
        )

        path.write_text(
            content,
            encoding="utf-8",
        )

        print(
            f"{name}: {path}"
        )


if __name__ == "__main__":
    main()