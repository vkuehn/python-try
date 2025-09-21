#! /usr/bin/env bash

set -euo pipefail

# Ensure we're in the right directory
cd "$(dirname "$0")/.."

install_uv() {
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH and reload shell environment
    export PATH="/root/.local/bin:$PATH"

    # Try direct execution from the installed location
    if [ -x "/root/.local/bin/uv" ]; then
        echo "UV executable found at /root/.local/bin/uv"
        /root/.local/bin/uv --version
        return 0
    else
        echo "Error: UV executable not found after installation"
        return 1
    fi
}

# Install Dependencies
uv sync
