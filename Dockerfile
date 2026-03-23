FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

COPY src/ src/
COPY data/gnosis.db data/gnosis.db

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "gnosis_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
