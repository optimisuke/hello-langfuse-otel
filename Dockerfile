FROM ghcr.io/astral-sh/uv:python3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:${PATH}"

COPY app.py ./

CMD ["python", "app.py"]
