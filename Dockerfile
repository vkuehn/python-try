# syntax=docker/dockerfile:1

FROM python:3.12.2-bookworm

# Install uv
RUN pip install -u uv

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY uv.lock pyproject.toml /code/

# Project initialization:
RUN uv sync --no-cache

# Copy Python code to the Docker image
COPY python_try /code/python_try/

CMD [ "python", "python_try/foo.py"]
