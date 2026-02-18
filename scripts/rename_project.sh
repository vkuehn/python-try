#!/bin/bash

# 🛑 Fail Fast:
set -e

# --- 1. Validation ---
NEW_NAME="$1"

if [ -z "$NEW_NAME" ]; then
    echo "❌ Error: No new name specified."
    echo "Usage: ./rename_project.sh <new-project-name>"
    exit 1
fi

# Find current directory name and parent directory
CURRENT_DIR_NAME=$(basename "$PWD")
PARENT_DIR=$(dirname "$PWD")

# Safety Check:
if [ "$CURRENT_DIR_NAME" == "$NEW_NAME" ]; then
    echo "⚠️  The project is already named '$NEW_NAME'. Nothing to do."
    exit 0
fi

echo "🚀 Starting migration from '$CURRENT_DIR_NAME' to '$NEW_NAME'..."


# --- 2. Cleanup (Housekeeping) ---
# We need to delete the .venv BEFORE renaming the folder,
# because absolute paths might be stored in venv scripts.
if [ -d ".venv" ]; then
    echo "🧹 Removing old .venv..."
    rm -rf .venv
fi

# Optional: Also delete caches to keep everything clean
rm -rf .ruff_cache .pytest_cache __pycache__


# --- 3. The "Dangerous Move" (Rename folder) ---
# Check if target already exists
if [ -d "../$NEW_NAME" ]; then
    echo "❌ Error: A folder named '$NEW_NAME' already exists in the parent directory!"
    exit 1
fi

echo "📦 Renaming directory..."

# Go one step back...
cd ..
# ... rename the folder ...
mv "$CURRENT_DIR_NAME" "$NEW_NAME"
# ... and enter the new folder.
cd "$NEW_NAME"


# --- 4. Re-initialization (Bootstrap) ---
echo "💎 Creating new environment (uv sync)..."
# Here uv is forced to rebuild the .venv.
# Since we're in the new path, all references are correct.
uv sync


# --- 5. Update project metadata and references ---
echo "🔧 Updating project configuration with new name..."
uv run python scripts/init_new_project.py --name "$NEW_NAME"

# -- 6. remove old .venv if it still exists (safety check) ---
if [ -d ".venv" ]; then
    echo "🧹 Removing old .venv (safety check)..."
    rm -rf .venv
fi

# --- 7. Create fresh environment and install git hooks ---
echo "🪝  Creating fresh environment and installing git hooks..."
uv sync --frozen
uv run pre-commit install

# Re-run custom hook setup script
if [ -f "scripts/setup_hook_commit_message.py" ]; then
    uv run python scripts/setup_hook_commit_message.py
fi

cd ..
cd "$NEW_NAME"
echo "✅ Done! Your project is now located at: $(pwd)"
