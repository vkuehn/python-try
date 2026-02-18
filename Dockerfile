# syntax=docker/dockerfile:1

# Use Python 3.14 slim image for smaller size
FROM python:3.14-slim-bookworm AS base

# Prevents Python from writing pyc files and keeps Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install uv using official method
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

# Copy dependency files first for better layer caching
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Install dependencies as root (some packages may need system access)
RUN uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser py.typed ./

# Switch to non-root user
USER appuser

# Run the application
CMD ["uv", "run", "python", "-c", "from python_try.main import main; print(main('world'))"]
