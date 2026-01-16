# syntax=docker/dockerfile:1

FROM python:3.14-bookworm

# Install uv
RUN pip install -U pip && pip install -U uv

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY uv.lock pyproject.toml /code/

# Project initialization:
RUN uv sync --frozen --no-cache --no-install-project

# Copy Python code to the Docker image
COPY python_try /code/python_try/

CMD ["uv", "run", "python", "-c", "from python_try.main import main; print(main('world'))"]
