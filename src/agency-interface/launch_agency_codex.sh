#!/bin/bash
# Launch Agency Codex CLI
# This script launches the agency interface for Codex CLI

# Check for required commands
command -v python3 >/dev/null 2>&1 || { echo "Error: Python 3 is required but not installed. Aborting."; exit 1; }

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Navigate to script directory
cd "$SCRIPT_DIR"

# Run the main agency CLI
./agency-cli.sh "$@"