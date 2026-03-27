FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY src/ src/
RUN uv sync --frozen --no-dev

COPY data/gnosis.db data/gnosis.db
COPY data/gnosis.usearch data/gnosis.usearch

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "gnosis_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
