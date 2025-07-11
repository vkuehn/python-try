#! /usr/bin/env bash

# Install Dependencies
uv pip install -r requirements.txt --upgrade --dev

# Install pre-commit hooks
uv venv exec pre-commit install --install-hooks
