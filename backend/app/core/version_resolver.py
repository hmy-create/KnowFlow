from app.core.llm_classifier import classify_label


def resolve_hr_version(query: str) -> str:
    return classify_label(
        query=query,
        prompt_filename="hr_version.txt",
        allowed_labels=[
            "Current",
            "Historical",
        ],
    )


def resolve_finance_version(query: str) -> str:
    return classify_label(
        query=query,
        prompt_filename="finance_version.txt",
        allowed_labels=[
            "Current",
            "Historical",
        ],
    )


def resolve_product_version(query: str) -> str:
    return classify_label(
        query=query,
        prompt_filename="product_version.txt",
        allowed_labels=[
            "Current",
            "Historical",
            "Comparison",
        ],
    )