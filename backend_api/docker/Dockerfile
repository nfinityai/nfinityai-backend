FROM python:3.11-buster as builder

ARG POETRY_VERSION=1.8.2

RUN pip install poetry==${POETRY_VERSION}

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.11-slim-buster as runtime

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./migrations migrations
COPY alembic.ini alembic.ini
COPY ./src/backend_api backend_api

EXPOSE 8000

ENTRYPOINT ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"]