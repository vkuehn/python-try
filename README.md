# python-try

try_batch
[![CI](https://github.com/vkuehn/python-try/actions/workflows/main.yml/badge.svg)](https://github.com/vkuehn/python-try/actions/workflows/)
[![Release](https://img.shields.io/badge/release-latest-blue)](https://github.com/vkuehn/python-try/releases/latest)
[![Build status](https://img.shields.io/github/actions/workflow/status/vkuehn/python-try/main.yml?branch=main)](https://github.com/vkuehn/python-try/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/vkuehn/python-try/branch/main/graph/badge.svg)](https://codecov.io/gh/vkuehn/python-try)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/vkuehn/python-try/blob/main/LICENSE)

This is a template repository for Python projects that use UV for their dependency management.
It has been generated from the [cookiecutter-poetry](https://fpgmaas.github.io/cookiecutter-poetrycookiecutter-poetry) repo.
But than change to UV as main tool

- **GitHub repository**: <https://github.com/vkuehn/python-try/>
- **Documentation** <https://vkuehn.github.io/python-try/>

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:vkuehn/python-try.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
python3 -m venv .venv
source ./venv/bin/activate
pip install -U pip
pip install .
make install
```

Make sure.

- that [GitHub pages](https://vkuehn.github.io/python-try/) is enabled for your repo in
  github.com/your name/repo name/settings/pages.
- that you may need to give the GITHUB_TOKEN write permission.
  Go to your repository's Settings > Actions > General > Workflow Permissions and select Read and write permissions.
- before actively using make sure you get your first minor release version.
- rename everything python_try to your repo name

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

# Features

- makefile with handy options during development
- mkdocs generates source code documentation see mkdocs.yml
- pre commit hook see .pre-commit-config.yaml
- ruff
- scripts folder collecting some helper function
- Pipelines
  - on-release-main
  - - use mkdocs to publish documentation on [GitPages](https://vkuehn.github.io/python-try/)
    - use python-semantic-release to create a new release

# ToDo

Pipelines stable in all situations
release scripts

# Devcontainer
 run devcontainer locally
 podman run -it --rm -v "$(pwd):/workspaces/python-try:Z" -w /workspaces/python-try mcr.microsoft.com/devcontainers/python:3.13-trixie bash

## Releasing a new version

---
