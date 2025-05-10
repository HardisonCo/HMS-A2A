#!/bin/bash
# HMS-A2A Migration Execution Script
# This script runs the migration steps in the correct order

set -e  # Exit on error

# Set working directory to HMS-A2A root
cd "$(dirname "$0")/.."
BASE_DIR="$(pwd)"
SCRIPTS_DIR="$BASE_DIR/scripts"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required for this script.${NC}"
    exit 1
fi

# Parse command line arguments
DRY_RUN=1
FORCE=0
SKIP_TESTS=0

for arg in "$@"; do
  case $arg in
    --force|-f)
      FORCE=1
      ;;
    --no-dry-run)
      DRY_RUN=0
      ;;
    --skip-tests)
      SKIP_TESTS=1
      ;;
    --help|-h)
      echo "Usage: $0 [options]"
      echo "  --force, -f       Skip confirmation prompts"
      echo "  --no-dry-run      Execute actual migration (default is dry run)"
      echo "  --skip-tests      Skip running tests after migration"
      echo "  --help, -h        Show this help message"
      exit 0
      ;;
  esac
done

# Header
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   HMS-A2A Migration Execution Script    ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

if [ $DRY_RUN -eq 1 ]; then
    echo -e "${YELLOW}DRY RUN MODE: No changes will be made.${NC}"
    echo "Run with --no-dry-run to execute the actual migration"
    echo ""
    DRY_RUN_ARG="--dry-run"
else
    echo -e "${YELLOW}LIVE MODE: Changes will be made to the filesystem.${NC}"
    echo ""
    DRY_RUN_ARG=""
fi

# Make all scripts executable
chmod +x "$SCRIPTS_DIR"/*.py

# Step 1: Run migration script to move files
echo -e "${GREEN}Step 1: File Migration${NC}"
if [ $DRY_RUN -eq 1 ]; then
    python3 "$SCRIPTS_DIR/migrate_structure.py" $DRY_RUN_ARG
else
    # Ask for confirmation before proceeding
    if [ $FORCE -eq 0 ]; then
        echo -e "${YELLOW}You are about to run the file migration in LIVE mode.${NC}"
        read -p "Are you sure you want to continue? [y/N] " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Migration cancelled."
            exit 1
        fi
    fi
    
    # Create a backup
    echo "Creating backup of current state..."
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Copy the directories to be modified
    for dir in "${ORIGINAL_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            cp -r "$dir" "$BACKUP_DIR/"
        fi
    done
    echo "Backup created in: $BACKUP_DIR"
    
    # Run the migration
    python3 "$SCRIPTS_DIR/migrate_structure.py" $DRY_RUN_ARG
fi

# Step 2: Update import statements
echo -e "\n${GREEN}Step 2: Update Documentation References${NC}"
python3 "$SCRIPTS_DIR/update_doc_references.py" $DRY_RUN_ARG

# Step 3: Run tests if not skipped
if [ $SKIP_TESTS -eq 0 ] && [ $DRY_RUN -eq 0 ]; then
    echo -e "\n${GREEN}Step 3: Running Tests${NC}"
    
    # Check if pytest is available
    if command -v pytest &> /dev/null; then
        echo "Running tests with pytest..."
        if pytest; then
            echo -e "${GREEN}All tests passed!${NC}"
        else
            echo -e "${RED}Tests failed!${NC}"
            echo "You may need to fix some issues before proceeding with cleanup."
            echo "You can look at the backup in $BACKUP_DIR if needed."
            exit 1
        fi
    else
        echo -e "${YELLOW}Warning: pytest not found, skipping tests.${NC}"
        echo "Please run tests manually before proceeding with cleanup."
    fi
else
    echo -e "\n${YELLOW}Skipping tests as requested or in dry-run mode.${NC}"
fi

# Step 4: Clean up unused files
echo -e "\n${GREEN}Step 4: Clean Up Unused Files${NC}"
python3 "$SCRIPTS_DIR/cleanup_unused.py" $DRY_RUN_ARG $([ $FORCE -eq 1 ] && echo "--force")

# Completion
echo ""
if [ $DRY_RUN -eq 1 ]; then
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}   Dry Run Completed Successfully!       ${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo ""
    echo "To execute the actual migration, run:"
    echo "  $0 --no-dry-run"
else
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}   Migration Completed Successfully!     ${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review the migrated files"
    echo "2. Verify that everything works correctly"
    echo "3. Commit the changes to version control"
fi 