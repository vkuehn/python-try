#!/usr/bin/env bash
set -e  # Exit on any error

echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH and reload shell environment
export PATH="/root/.local/bin:$PATH"

# Verify installation
if [ -x "/root/.local/bin/uv" ]; then
    echo "UV executable found at /root/.local/bin/uv"
    /root/.local/bin/uv --version
else
    echo "Error: UV executable not found after installation"
    exit 1
fi

# Install Dependencies
echo "Syncing dependencies..."
uv sync --frozen
echo "Dependencies synced successfully!"
