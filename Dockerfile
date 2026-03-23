FROM python:3.12-slim AS base

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/ src/
COPY data/gnosis.db data/gnosis.db

EXPOSE 8000
CMD ["uvicorn", "gnosis_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
