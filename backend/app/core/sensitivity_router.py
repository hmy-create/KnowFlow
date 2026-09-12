from app.core.llm_classifier import classify_label


FINANCE_SENSITIVITY_LABELS = [
    "Normal",
    "Restricted",
]


def classify_finance_sensitivity(query: str) -> str:
    return classify_label(
        query=query,
        prompt_filename="finance_sensitivity.txt",
        allowed_labels=FINANCE_SENSITIVITY_LABELS,
    )