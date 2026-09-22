from importlib.metadata import (
    PackageNotFoundError,
    version,
)
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

OUTPUT = (
    ROOT
    / "requirements-docker.txt"
)


PACKAGES = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "python-dotenv",
    "zhipuai",

    "psycopg",
    "psycopg-binary",
    "psycopg2-binary",

    "rank-bm25",
    "jieba",
    "numpy",

    "FlagEmbedding",
    "transformers",
    "sentence-transformers",
    "huggingface-hub",

    "python-docx",
    "openpyxl",
    "pandas",

    "requests",
]


lines = []

for package in PACKAGES:

    try:

        v = version(package)

    except PackageNotFoundError:
        continue

    lines.append(
        f"{package}=={v}"
    )


OUTPUT.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)


print(
    f"generated: {OUTPUT}"
)

print("")

print(
    OUTPUT.read_text(
        encoding="utf-8"
    )
)