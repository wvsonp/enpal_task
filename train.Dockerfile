# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.13-slim-bookworm AS builder

# Copy uv binary directly from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system packages required for the scientific Python stack
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set uv environment variables for optimal performance
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy dependency management files
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy project metadata and source code
COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data

# Default command: run training entrypoint
ENTRYPOINT ["python", "-m", "src.train_entry"]
