import jieba


def tokenize(text: str) -> list[str]:
    return [
        token.strip().lower()
        for token in jieba.lcut(text)
        if token.strip()
    ]