#!/bin/bash
# Standards Migration Script for HMS-A2A
# This script automates the migration of standards from HMS-SME to HMS-A2A format

set -e

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
SOURCE_DIR="$BASE_DIR/data/standards/source"
HMS_NFO_PATH="/Users/arionhardison/Desktop/CodifyHQ/HMS-DTA/HMS-NFO"

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Migrate standards from HMS-SME format to HMS-A2A format"
    echo ""
    echo "Options:"
    echo "  -s, --source     Source standards file or directory (default: auto-detect)"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Auto-detect source standards"
    echo "  $0 --source /path/to/std.json  # Specify source standards file"
    echo "  $0 --source /path/to/standards/ # Specify source standards directory"
    echo ""
}

# Parse arguments
SOURCE_PATH=""

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -s|--source)
            SOURCE_PATH="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $key"
            show_help
            exit 1
            ;;
    esac
done

# Auto-detect source if not specified
if [ -z "$SOURCE_PATH" ]; then
    echo "Auto-detecting source standards..."
    
    # Try to find HMS-NFO standards
    if [ -d "$HMS_NFO_PATH" ]; then
        if [ -d "$HMS_NFO_PATH/_/SYSTEM-LEVEL/standards" ]; then
            SOURCE_PATH="$HMS_NFO_PATH/_/SYSTEM-LEVEL/standards"
            echo "Found HMS-NFO standards at $SOURCE_PATH"
        elif [ -f "$HMS_NFO_PATH/_/SYSTEM-LEVEL/std.json" ]; then
            SOURCE_PATH="$HMS_NFO_PATH/_/SYSTEM-LEVEL/std.json"
            echo "Found HMS-NFO std.json at $SOURCE_PATH"
        else
            echo "HMS-NFO directory found but no standards located."
            echo "Please specify source standards path with --source option."
            exit 1
        fi
    else
        echo "HMS-NFO directory not found at $HMS_NFO_PATH"
        echo "Please specify source standards path with --source option."
        exit 1
    fi
fi

# Verify source exists
if [ ! -e "$SOURCE_PATH" ]; then
    echo "Error: Source path does not exist: $SOURCE_PATH"
    exit 1
fi

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found in PATH"
    exit 1
fi

echo "Starting standards migration process..."
echo "Source: $SOURCE_PATH"
echo "Destination: $BASE_DIR/data/standards"

# Run migration script
python3 "$BASE_DIR/specialized_agents/standards/standards_migration.py" --source "$SOURCE_PATH"

# Check exit status
if [ $? -eq 0 ]; then
    echo "Standards migration completed successfully!"
    echo "Standards database is available at:"
    echo "  $BASE_DIR/data/standards/standards.json"
    
    # Update stats
    echo "Updating standards statistics..."
    if [ -f "$BASE_DIR/data/standards/standards.json" ]; then
        STANDARD_COUNT=$(python3 -c "import json; print(len(json.load(open('$BASE_DIR/data/standards/standards.json'))))")
        echo "Total standards migrated: $STANDARD_COUNT"
    fi
    
    exit 0
else
    echo "Standards migration failed!"
    echo "Please check the logs for details."
    exit 1
fi