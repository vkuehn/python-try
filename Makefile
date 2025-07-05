.PHONY: build
build: clean-build ## Build wheel file using uv and .venv
	@echo "🚀 Creating wheel file"
	@uv build --out-dir dist/

.PHONY: check
check: ## Run code quality tools and project checks.
	@echo "🚀 Checking uv lock file consistency with 'pyproject.toml': Running uv pip check"
	@uv pip check
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy
	@echo "🚀 Checking for latest version for dependencies"
	@uv pip list --outdated
	@echo "🚀 Checking uv environments"
	@uv venv list
	@echo "🚀 uv version"
	@uv --version

.PHONY: clean-build
clean-build: ## clean build artifacts is needed by build
	@echo "🚀 Cleaning build artifacts"
	@rm -rf dist

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs-serve
docs-serve: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: docs
docs: ## Build the documentation
	@uv run mkdocs build

.PHONY: docker-build
docker-build: ## Build Docker container from current project state
	@docker build -t python-try .

.PHONY: install
install: ## Install the uv environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv and installing dependencies"
	@uv sync
	@uv run pre-commit install

.PHONY: update
update: ## Run update of dependencies
	@echo "🚀 Updating project with uv"
	@uv sync --upgrade

.PHONY: test
test: install ## Test the code with pytest (installs dependencies if needed)
	@echo "🚀 Testing code: Running pytest"
	@uv run pytest --cov --cov-config=pyproject.toml --cov-report=html

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
