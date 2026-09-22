FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TOKENIZERS_PARALLELISM=false
ENV PYTHONPATH=/app/backend
ENV HF_HOME=/root/.cache/huggingface

WORKDIR /app


# ============================================================
# System dependencies
# ============================================================

RUN apt-get update \
    && apt-get install -y \
        --no-install-recommends \
        build-essential \
        git \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*


# ============================================================
# Upgrade Python packaging tools
#
# 避免旧 pip 对 typing-extensions
# metadata normalization 处理异常。
# ============================================================

RUN python -m pip install \
    --no-cache-dir \
    --upgrade \
    pip \
    setuptools \
    wheel


# ============================================================
# PyTorch CPU
#
# PyTorch wheel 优先从 CPU index 获取，
# 其他依赖允许从 PyPI 获取。
#
# 不能只写 --index-url CPU，
# 否则 flit_core 等普通依赖无法解析。
# ============================================================

RUN python -m pip install \
    --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple \
    torch


# ============================================================
# KnowFlow Python dependencies
# ============================================================

COPY requirements-docker.txt \
     /app/requirements-docker.txt

RUN python -m pip install \
    --no-cache-dir \
    -r /app/requirements-docker.txt


# ============================================================
# Application
# ============================================================

COPY . /app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.s10_app:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]