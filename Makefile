.PHONY: build
build: clean-build ## Build wheel file using uv and .venv
	@echo "🚀 Creating wheel file"
	@uv run tox -e build

.PHONY: check
check: ## Run code quality tools and project checks.
	@echo "🚀 Cleaning previous tox and mypy artifacts"
	@rm -rf .tox
	@rm -rf .mypy_cache
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
	@read -p "🔗 Enter new project name: " NEW_NAME; \
	if [ -z "$$NEW_NAME" ]; then \
		echo "❌ Error: No project name provided"; \
		exit 1; \
	fi; \
	echo "🚀 Initializing new project with name: $$NEW_NAME"; \
	echo "make can't run the rename script directly!!"; \
	echo ". scripts/rename_project.sh \"$$NEW_NAME\""; \

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
update: ## Safe Update: Refresh lockfile within pyproject.toml constraints
	@echo "🚀 Upgrading dependencies in uv.lock..."
	@uv lock --upgrade
	@echo "🚀 Syncing project environment..."
	@uv sync --all-groups
	@echo "🚀 Exporting frozen requirements.txt..."
	@uv export --format requirements.txt --frozen --no-hashes --no-emit-project --output-file requirements.txt
	@echo "✅ Safe update complete."

.PHONY: upgrade
upgrade: ## Major Upgrade: Bump pyproject.toml constraints to absolute latest
	@echo "🚀 Bumping all pyproject.toml constraints to latest..."
	@# This extracts package names from [project] dependencies and forces uv to add their latest versions
	@python -c "import tomllib; deps = tomllib.load(open('pyproject.toml', 'rb')).get('project', {}).get('dependencies', []); pkgs = [d.split('=')[0].split('<')[0].split('>')[0].split('~')[0].strip() for d in deps]; print(' '.join([f'{p}@latest' for p in pkgs if p]))" | xargs -n 1 uv add
	@echo "🚀 Project file rewritten. Now running standard update..."
	@$(MAKE) update
	@echo "🚨 WARNING: Major versions may have been bumped. Please run your test suite!"

.PHONY: test
test: install ## Test the code with pytest (installs dependencies if needed)
	@echo "🚀 Testing via tox (uv.lock)"
	@uv run tox -e py314

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
