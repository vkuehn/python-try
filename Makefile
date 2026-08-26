.PHONY: build
build: clean-build ## Build wheel/sdist with uv (same command semantic-release uses)
	@echo "🚀 Building distribution with uv"
	@uv build --out-dir dist/

.PHONY: check
check: ## Run quality gates (lint + type + tests) - read-only, mirrors CI
	@echo "🚀 Running lint, type and tests via tox (uv.lock)"
	@uv run tox -e lint,type,py314

.PHONY: fix
fix: ## Auto-format and autofix with ruff - mutates source files
	@echo "🚀 Formatting and autofixing via tox (uv.lock)"
	@uv run tox -e fix

.PHONY: lint
lint: ## Lint the code (ruff, read-only)
	@uv run tox -e lint

.PHONY: type
type: ## Type-check the code (mypy)
	@uv run tox -e type

.PHONY: test
test: ## Run the test suite (pytest + coverage)
	@echo "🚀 Testing via tox (uv.lock)"
	@uv run tox -e py314

.PHONY: clean-build
clean-build: ## Remove build artifacts (needed by build)
	@echo "🚀 Cleaning build artifacts"
	@rm -rf dist

.PHONY: docs
docs: ## Build the documentation
	@uv run tox -e docs

.PHONY: docs-test
docs-test: ## Build the documentation in strict mode (warnings become errors)
	@uv run tox -e docs-test

.PHONY: docs-serve
docs-serve: ## Build and serve the documentation locally
	@uv run tox -e docs -- serve

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
install: ## Install the uv environment and set up git hooks
	@echo "🚀 Creating virtual environment using uv and installing dependencies"
	@uv sync --frozen
	@echo "🚀 make sure a requirements file exists"
	@uv export --format requirements.txt --frozen --no-hashes --no-emit-project --output-file requirements.txt
	@echo "🚀 Setting up git hooks"
	@uv run pre-commit install
	@uv run ./scripts/setup_hook_commit_message.py

.PHONY: update
update: ## Safe update: refresh lockfile within pyproject.toml constraints
	@echo "🚀 Upgrading dependencies in uv.lock..."
	@uv lock --upgrade
	@echo "🚀 Syncing project environment..."
	@uv sync --all-groups
	@echo "🚀 Exporting frozen requirements.txt..."
	@uv export --format requirements.txt --frozen --no-hashes --no-emit-project --output-file requirements.txt
	@echo "✅ Safe update complete."

.PHONY: upgrade
upgrade: ## Major upgrade: bump pyproject.toml constraints to absolute latest
	@echo "🚀 Bumping all pyproject.toml constraints to latest..."
	@# Extract package names from [project] dependencies and bump each to latest.
	@pkgs="$$(uv run python -c "import re, tomllib; deps = tomllib.load(open('pyproject.toml', 'rb')).get('project', {}).get('dependencies', []); names = [re.split(r'[<>=!~\\[]', d, maxsplit=1)[0].strip() for d in deps if d.strip()]; print(' '.join(f'{n}@latest' for n in names if n))")"; \
	if [ -n "$$pkgs" ]; then \
		echo "🚀 Upgrading project dependencies: $$pkgs"; \
		printf "%s\\n" "$$pkgs" | xargs -n 1 uv add; \
	else \
		echo "ℹ️ No [project] dependencies found; skipping constraint rewrite."; \
	fi
	@echo "🚀 Project file rewritten. Now running standard update..."
	@$(MAKE) update
	@echo "🚨 WARNING: Major versions may have been bumped. Please run your test suite!"

.PHONY: help
help:
	@echo "python-try - a slim UV + tox Python template"
	@echo ""
	@echo "Approach: tox is the single runner for all quality gates (tests, lint,"
	@echo "type, docs). The targets below are thin wrappers around 'uv run tox -e ...',"
	@echo "so local and CI runs are identical. tox is kept intentionally minimal;"
	@echo "add matrices, plugins or extra envs once you start your own project."
	@echo ""
	@echo "Note: 'fix' mutates source files; 'check' is read-only and mirrors CI."
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
