FROM python:3.13-alpine AS base

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .


FROM base AS migrate

RUN wget -q https://github.com/pressly/goose/releases/download/v3.26.0/goose_linux_x86_64 -O /usr/local/bin/goose && chmod +x /usr/local/bin/goose

ENTRYPOINT ["goose", "-dir", "migrations", "sqlite3", "/data/heartbeat.db", "up"]


FROM base AS app

ENTRYPOINT ["uv", "run", "python", "main.py"]