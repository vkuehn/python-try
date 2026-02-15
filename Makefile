.PHONY: build
build: clean-build ## Build wheel file using uv and .venv
	@echo "🚀 Creating wheel file"
	@uv run tox -e build

.PHONY: check
check: ## Run code quality tools and project checks.
	@echo "🚀 Running checks via tox (uv.lock)"
	@uv run tox -e outdated,fix,lint,type,py314

.PHONY: clean-build
clean-build: ## clean build artifacts is needed by build
	@echo "🚀 Cleaning build artifacts"
	@rm -rf dist

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run tox -e docs-test

.PHONY: docs-serve
docs-serve: ## Build and serve the documentation
	@mkdocs serve

.PHONY: docs
docs: ## Build the documentation
	@uv run tox -e docs

.PHONY: docker-build
docker-build: ## Build Docker container from current project state
	@docker build -t python-try .

.PHONY: init-project
init-project: ## Nuke old git history and start a fresh project with new origin
	@uv run python scripts/init_new_project.py

.PHONY: install
install: ## Install the uv environment
	@echo "🚀 Creating virtual environment using uv and installing dependencies"
	@uv sync --frozen
	@echo "🚀 make sure a requirements file exists"
	@uv export --format requirements.txt --frozen --no-hashes --no-emit-project --output-file requirements.txt
	@uv run pre-commit install
	@echo "🚀 Setting up git hooks"
	@uv run pre-commit install
	@uv run ./scripts/setup_hook_commit_message.py


.PHONY: update
update: ## Run update of dependencies
	@echo "🚀 Upgrading dependencies in uv.lock"
	@uv lock --upgrade
	@echo "🚀 Updating project with uv"
	@uv sync --all-groups
	@echo "🚀 make sure a requirements is upgraded also"
	@uv export --format requirements.txt --frozen --no-hashes --no-emit-project --output-file requirements.txt

.PHONY: test
test: install ## Test the code with pytest (installs dependencies if needed)
	@echo "🚀 Testing via tox (uv.lock)"
	@uv run tox -e py314

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
