ARG DEPS_IMAGE=__APP_NAME__:deps
FROM ${DEPS_IMAGE}

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# Copy only application code and runtime assets; dependencies are already installed in deps image
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY README.md ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


