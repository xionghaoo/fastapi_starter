ARG BASE_IMAGE=docker.m.daocloud.io/library/python:3.11-slim
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

# Install project as a package (PEP517) so dependencies are resolved from pyproject.toml
COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN pip install --upgrade pip && pip install "uvicorn[standard]" && pip install .

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


