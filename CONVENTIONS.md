# Project Conventions

These instructions apply to all AI-assisted contributions in this repository.
They are tool-agnostic and intended for any AI coding assistant.

## Project context

- Language/runtime: Python **3.14** (see `pyproject.toml`).
- Package: `src/python_try/`.
- Tests: `tests/` with **pytest**.
- Tooling:
  - Dependency management / runner: **uv**
  - CI/local orchestration: **tox** (often via `uv run tox ...`)
  - Formatting/lint: **ruff** (+ **pylint** in `tox -e lint`)
  - Type checking: **mypy** (strict settings in `pyproject.toml`)
  - Docs: **mkdocs**

Prefer using existing repo commands:
- `make test` (runs `tox -e py314`)
- `make check` (runs formatting/lint/type/test envs)
- `make docs` / `make docs-test`

## Defaults (how to work in this repo)

- Prefer small, reviewable diffs; avoid drive-by refactors.
- Call out assumptions and tradeoffs briefly; propose the smallest acceptable change before suggesting broader refactors.
- Fix root causes (don't paper over symptoms) and keep behavior/backward-compatibility unless asked otherwise.
- Follow existing patterns and naming in `src/python_try/`; avoid introducing new abstractions unless they pay for themselves.
- Validate changes using repo tooling: `uv run tox -e lint,type,py314` (or `make check`).
- When changing behavior, add/adjust pytest coverage for the relevant branches.

## Coding guidelines

- Keep changes minimal and focused on the user request.
- Match existing style (ruff formatting, line length 120).
- For major changes (especially breaking changes), use Conventional Commits so release tooling can infer version bumps (e.g., `feat!: ...` / `BREAKING CHANGE: ...`).
- Add type hints for new/changed public functions; keep mypy happy.
- Use Google-style docstrings where docstrings are present/expected.
- Avoid adding new dependencies unless explicitly requested.

## Unit test guidelines (pytest)

When writing unit tests:

- Use **pytest**.
- Prefer simple tests; avoid unnecessary mocks/classes/`SimpleNamespace`.
- Use `pytest.mark.parametrize` for input matrices.
  - Provide `argnames` as a **tuple of strings**, not a single string.
  - Prefer `pytest.param(..., id="...")` over per-case comments.
- Use comments only when they explain **why** (not what/how); write comments in English.
- Include type annotations in test function signatures when it improves clarity.
- Aim to cover relevant branches.

Note: If the project later defines a dedicated unit-test marker/decorator (e.g., `pytest.mark.unit_test`), follow that convention consistently.

## Workflow patterns

### 3-Step adversarial loop

For non-trivial changes, follow a structured critique cycle:

1. **Draft**: Generate the initial implementation, listing assumptions and risks. Do not finalize. Signal `READY_FOR_CRITIQUE`.
2. **Critique**: Audit for edge cases, performance concerns, type safety, and backward-compatibility. List prioritized findings. Signal `READY_FOR_REFINE`.
3. **Refine**: Apply the critique to produce the final implementation with tests.

Skip this loop for simple, low-risk changes (typos, config tweaks, single-line fixes).

### Context curation

- Attach relevant files explicitly when starting a task; do not rely on automatic discovery alone.
- When a hallucination or incorrect assumption is corrected, update this instruction file to prevent repeats.
- Pin architectural context (module boundaries, naming conventions) rather than re-explaining per task.

### Validation and confidence

| Task type | Minimum evidence for high confidence |
| --- | --- |
| **Code logic** | Tests pass (`make check` green) |
| **Documentation / polish** | Before-and-after diff with scope declared upfront |
| **Quick operation** | Before-and-after state proof |

For complex documentation or polish tasks, apply the full validation protocol:
1. **Pre-flight**: Declare scope, expected impact, success threshold.
2. **Execute**: Apply changes with documented rationale.
3. **Verify**: Show before→after metrics.
4. **Test**: Run regression suite where applicable.
