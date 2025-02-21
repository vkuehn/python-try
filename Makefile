.PHONY: build
build: clean-build ## Build wheel file using poetry
	@echo "🚀 Creating wheel file"
	@poetry build

.PHONY: check
check: ## Run code quality tools and project checks.
	@echo "🚀 Checking Poetry lock file consistency with 'pyproject.toml': Running poetry lock --check"
	@poetry check --lock
	@echo "🚀 Linting code: Running pre-commit"
	@poetry run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@poetry run mypy
	@echo "🚀 Checking for latest version for dependencies"
	@poetry show --latest --top-level
	@echo "🚀 Checking poetry venvs"
	@poetry env list
	@echo "🚀 poetry config"
	@poetry config --list
	@echo "🚀 poetry version"
	@poetry about

.PHONY: clean-build
clean-build: ## clean build artifacts
	@rm -rf dist

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@poetry run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@poetry run mkdocs serve

.PHONY: docker-build
docker-build: ## Build Docker container from current project state
	@docker build -t python-try .

.PHONY: install
install: ## Install the poetry environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry run pre-commit install
	@poetry shell

.PHONY: update
update: ## Run update of dependencies
	@echo "🚀 Updating project with Poetry"
	@rm poetry.lock
	@poetry self update
	@poetry update

.PHONY: update-check
update-check: ## Check if updates have conflicting dependencies
	@echo "🚀 Check if updates have conflicting dependencies"
	@poetry update --dry-run

.PHONY: update-requirements
update-requirements: ## Update requirements.txt from poetry.lock using tox and user tools
	@echo "Updating requirements.txt from poetry.lock..."
	@poetry export -f requirements.txt --output requirements.txt --without-hashes
	@tox -e requirements

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@poetry run pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
