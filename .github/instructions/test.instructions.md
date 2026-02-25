# Python Development Instructions - python-try/src

## 🎯 Context
- **Project:** python-try template repository
- **Python Version:** >= 3.14
- **Code Quality:** Ruff, Mypy, Pylint, Pre-commit hooks
- **Testing:** Pytest with coverage of at least 80%

## 🔄 Mandatory Workflow: The 3-Step Loop

For all Python code changes in `src/python_try/`:

1. **DRAFT:** Propose implementation with type hints and docstrings.
2. **CRITIQUE:** Self-audit for:
   - Type safety (mypy compliance)
   - Google-style docstrings
   - Ruff linting rules compliance
   - Edge cases and error handling
   - Test coverage implications
3. **REFINE:** Output final code with corresponding pytest tests.

## 🏗️ Code Standards

### Type Hints
- All functions must have explicit type hints for parameters and return values.
- Use modern Python 3.14+ type syntax.
- Comply with mypy strict settings (no implicit Optional, no untyped definitions).

### Docstrings
- Use Google-style docstrings for all public functions and classes.
- Include Args, Returns, Raises sections where applicable.

### Code Quality
- Follow Ruff rules (line length: 120 chars).
- Avoid complexity (mccabe, simplify comprehensions).
- No security antipatterns (bandit S* rules).
- Prefer explicit over implicit (no lambda assignments).

### Testing
- Write pytest tests in `/tests/` for all new functionality.
- Maintain branch coverage (run `pytest --cov`).
- Use descriptive test names: `test_<function>_<scenario>_<expected_outcome>`.

## 📋 Code Generation Pattern

When creating new Python modules in `src/python_try/`:

```
Using Python 3.14, create a {module/function} that:
- Purpose: {clear objective}
- Inputs: {parameters with type hints}
- Outputs: {return type}
- Constraints: Google-style docstrings, mypy strict compliance
- Error handling: {expected exceptions}
- Tests: Include corresponding pytest test cases

Follow project conventions in @workspace.
```

## 🔍 Pre-commit Validation

Before finalizing code:
- Run `make check` to execute formatting, linting, type checking, and tests via tox/uv.
- Optionally run `make test` for a focused test run (tox `py314` environment).
- Optionally run `make docs-test` if documentation changes are included.

## 🎯 Quality Gates

All code must pass:
- ✅ Ruff linting (no errors)
- ✅ Mypy type checking (no errors)
- ✅ Pytest tests (100% pass rate)
- ✅ Coverage threshold maintained by at least 80% of code
