def rewrite_query(query: str) -> str:
    """
    S6 第一版只做无损规范化。

    暂时不让 LLM 改写问题，
    防止修改 Frozen POC 的业务语义。
    """

    return " ".join(
        query.strip().split()
    )