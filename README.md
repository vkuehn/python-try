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

## Project Structure

Uses standard **src-layout**:

```text
python-try/
├── src/python_try/     # Package source code
├── tests/              # Test files
└── pyproject.toml
```

## Getting started with your project

To start a new project using this template:

1. **Clone the repository** (or download and extract the ZIP):

    ```bash
    git clone [https://github.com/vkuehn/python-try.git](https://github.com/vkuehn/python-try.git) my-new-project
    cd my-new-project
    ```

2. **Install dependencies**:

    ```bash
    make install
    ```

3. **Initialize your new project**:
    This command will remove the template's git history, initialize a new git repository, and optionally link it to your new remote origin.

    ```bash
    make init-project
    ```

4. **Rename and Configure**:
    - Rename the package folder `src/python_try` to your project name.
    - Update `pyproject.toml` with your project's name, version, and authors.
    - Update `mkdocs.yml` with your project name and repository URL.
    - Push your first commit: `git push -u origin main`

Make sure:

- that [GitHub pages](https://pages.github.com/) is enabled for your repo in `Settings > Pages`.
- that you give the GITHUB_TOKEN write permission.
  Go to `Settings > Actions > General > Workflow Permissions` and select **Read and write permissions**.

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

## Features

- **Makefile** with handy options during development (`make help`)
- **MkDocs** for source code documentation (see `mkdocs.yml`)
- **Pre-commit hooks** for code quality (see `.pre-commit-config.yaml`)
- **Ruff** for linting and formatting
- **Docker** with optimized Dockerfile and docker-compose setup
- **Scripts** folder collecting helper functions
- **Pipelines**:
  - `on-release-main`:
    - Publishes documentation on GitHub Pages
    - Uses `python-semantic-release` to create new releases automatically

## Development Workflow

This template uses a single source of truth for quality checks: tox is the runner
for tests, linting, type checking and documentation builds. The Makefile targets are
thin wrappers around `uv run tox -e <env>`, so what you run locally is exactly what CI
runs. uv manages dependencies and creates the locked, isolated environments tox uses.

tox is kept intentionally minimal (just the quality gates). More advanced tox usage,
such as version matrices, plugins or extra environments, is left for you to add once
you have started your own project from this template.

Common commands (see `make help` for the full list and an explanation):

```bash
make check   # lint + type + tests (read-only, mirrors CI)
make fix     # ruff format + autofix (mutates source files)
make test    # run the test suite (pytest + coverage)
make docs    # build the documentation
```

The tox environments themselves:

- `py314` (default): pytest with doctests and coverage
- `lint`: ruff check (read-only)
- `type`: mypy
- `fix`: ruff format and autofix (mutating; kept separate from `check`)
- `docs` / `docs-test`: mkdocs build (strict for `docs-test`)

Build and release use uv directly (`uv build`), matching the semantic-release
`build_command`, so no tox environment is needed for packaging.

## ToDo

- remove all python_try left overs in code and documentation and config files
  index.md,CONTRIBUTING.md,init_new_project.py,tox.ini,test_main.py,_init__.py,mkdocs.yml
- rename complete folder and subfolder
- remove ./src/python_try.egg-info folder
- recreate .venv folder
- Ensure pipelines are stable in all situations
- Refine release scripts

**Docker Compose**:

```bash
docker-compose up dev
```
