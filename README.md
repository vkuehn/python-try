# python-try

[![CI](https://github.com/vkuehn/python-try/actions/workflows/main.yml/badge.svg)](https://github.com/vkuehn/python-try/actions/workflows/)
[![Release](https://img.shields.io/badge/release-latest-blue)](https://github.com/vkuehn/python-try/releases/latest)
[![Build status](https://img.shields.io/github/actions/workflow/status/vkuehn/python-try/main.yml?branch=main)](https://github.com/vkuehn/python-try/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/vkuehn/python-try/branch/main/graph/badge.svg)](https://codecov.io/gh/vkuehn/python-try)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/vkuehn/python-try/blob/main/LICENSE)

This is a template repository for Python projects that use UV for their dependency management.
It is based on standard best practices for modern Python development.

- **GitHub repository**: <https://github.com/vkuehn/python-try/>
- **Documentation** <https://vkuehn.github.io/python-try/>

## Getting started with your project

To start a new project using this template:

1.  **Clone the repository** (or download and extract the ZIP):
    ```bash
    git clone [https://github.com/vkuehn/python-try.git](https://github.com/vkuehn/python-try.git) my-new-project
    cd my-new-project
    ```

2.  **Install dependencies**:
    ```bash
    make install
    ```

3.  **Initialize your new project**:
    This command will remove the template's git history, initialize a new git repository, and optionally link it to your new remote origin.
    ```bash
    make init-project
    ```

4.  **Rename and Configure**:
    - Rename the source folder `python_try` to your project name.
    - Update `pyproject.toml` with your project's name, version, and authors.
    - Update `mkdocs.yml` with your project name and repository URL.
    - Push your first commit: `git push -u origin main`

Make sure:
- that [GitHub pages](https://pages.github.com/) is enabled for your repo in `Settings > Pages`.
- that you give the GITHUB_TOKEN write permission.
  Go to `Settings > Actions > General > Workflow Permissions` and select **Read and write permissions**.

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

# Features

- **Makefile** with handy options during development (`make help`)
- **MkDocs** for source code documentation (see `mkdocs.yml`)
- **Pre-commit hooks** for code quality (see `.pre-commit-config.yaml`)
- **Ruff** for linting and formatting
- **Scripts** folder collecting helper functions
- **Pipelines**:
  - `on-release-main`:
    - Publishes documentation on GitHub Pages
    - Uses `python-semantic-release` to create new releases automatically

# ToDo

- remove all python_try left overs
- rename complete folder and subfolder
- recreate .venv folder
- Ensure pipelines are stable in all situations
- Refine release scripts

# Devcontainer

Run devcontainer locally:
```bash
podman run -it --rm -v "$(pwd):/workspaces/python-try:Z" -w /workspaces/python-try [mcr.microsoft.com/devcontainers/python:3.14-bookworm](https://mcr.microsoft.com/devcontainers/python:3.14-bookworm) bash
