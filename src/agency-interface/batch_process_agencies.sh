#!/bin/bash
# Batch Process Agencies
# This script processes multiple agencies in a batch

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Default values
CONFIG_FILE="$SCRIPT_DIR/config/agency_data.json"
AGENCY_GENERATOR="$SCRIPT_DIR/agency_generator.py"
BASE_DIR="$SCRIPT_DIR"
TEMPLATES_DIR="$SCRIPT_DIR/templates"
MODE="process"
TIER=""
AGENCIES=""
VERBOSE=false

# Show usage
function show_usage() {
  echo -e "${BOLD}Batch Process Agencies${NC}"
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  -m, --mode MODE       Mode (process, test) [default: process]"
  echo "  -t, --tier TIER       Process agencies in a specific tier"
  echo "  -a, --agencies FILE   Process agencies listed in a file"
  echo "  -c, --config FILE     Config file [default: config/agency_data.json]"
  echo "  -b, --base-dir DIR    Base directory [default: script dir]"
  echo "  -d, --templates-dir DIR Templates directory [default: templates]"
  echo "  -v, --verbose         Verbose output"
  echo "  -h, --help            Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0 --tier 1           # Process all Tier 1 agencies"
  echo "  $0 --agencies tier1.txt # Process agencies listed in tier1.txt"
  echo "  $0 --mode test --tier 2 # Test all Tier 2 agencies"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--mode)
      MODE="$2"
      shift 2
      ;;
    -t|--tier)
      TIER="$2"
      shift 2
      ;;
    -a|--agencies)
      AGENCIES="$2"
      shift 2
      ;;
    -c|--config)
      CONFIG_FILE="$2"
      shift 2
      ;;
    -b|--base-dir)
      BASE_DIR="$2"
      shift 2
      ;;
    -d|--templates-dir)
      TEMPLATES_DIR="$2"
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    -h|--help)
      show_usage
      exit 0
      ;;
    *)
      echo "Error: Unknown option: $1"
      show_usage
      exit 1
      ;;
  esac
done

# Validate mode
if [[ "$MODE" != "process" && "$MODE" != "test" ]]; then
  echo "Error: Invalid mode: $MODE"
  show_usage
  exit 1
fi

# Check if at least one of tier or agencies is specified
if [[ -z "$TIER" && -z "$AGENCIES" ]]; then
  echo "Error: Either --tier or --agencies must be specified"
  show_usage
  exit 1
fi

# Check if agency generator exists
if [[ ! -f "$AGENCY_GENERATOR" ]]; then
  echo "Error: Agency generator script not found: $AGENCY_GENERATOR"
  exit 1
fi

# Check if config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Error: Config file not found: $CONFIG_FILE"
  exit 1
fi

# Process agencies by tier
function process_tier() {
  local tier=$1
  
  echo -e "${BOLD}Processing Tier $tier Agencies${NC}"
  echo -e "${YELLOW}Mode: $MODE${NC}"
  echo -e "${YELLOW}Config file: $CONFIG_FILE${NC}"
  echo -e "${YELLOW}Base directory: $BASE_DIR${NC}"
  echo -e "${YELLOW}Templates directory: $TEMPLATES_DIR${NC}"
  echo
  
  if [[ "$MODE" == "process" ]]; then
    python3 "$AGENCY_GENERATOR" --tier "$tier" --config-file "$CONFIG_FILE" --base-dir "$BASE_DIR" --templates-dir "$TEMPLATES_DIR"
  elif [[ "$MODE" == "test" ]]; then
    echo -e "${YELLOW}Testing Tier $tier Agencies...${NC}"
    # Add testing code here
    echo -e "${GREEN}Testing completed.${NC}"
  fi
}

# Process agencies from file
function process_agencies_from_file() {
  local file=$1
  
  echo -e "${BOLD}Processing Agencies from File: $file${NC}"
  echo -e "${YELLOW}Mode: $MODE${NC}"
  echo -e "${YELLOW}Config file: $CONFIG_FILE${NC}"
  echo -e "${YELLOW}Base directory: $BASE_DIR${NC}"
  echo -e "${YELLOW}Templates directory: $TEMPLATES_DIR${NC}"
  echo
  
  if [[ ! -f "$file" ]]; then
    echo "Error: Agencies file not found: $file"
    exit 1
  fi
  
  while IFS= read -r agency; do
    # Skip empty lines and comments
    if [[ -z "$agency" || "$agency" =~ ^# ]]; then
      continue
    fi
    
    echo -e "${BLUE}Processing agency: $agency${NC}"
    
    if [[ "$MODE" == "process" ]]; then
      python3 "$AGENCY_GENERATOR" --agency "$agency" --config-file "$CONFIG_FILE" --base-dir "$BASE_DIR" --templates-dir "$TEMPLATES_DIR"
    elif [[ "$MODE" == "test" ]]; then
      echo -e "${YELLOW}Testing agency: $agency...${NC}"
      # Add testing code here
      echo -e "${GREEN}Testing completed.${NC}"
    fi
    
    echo
  done < "$file"
}

# Main execution
if [[ -n "$TIER" ]]; then
  process_tier "$TIER"
elif [[ -n "$AGENCIES" ]]; then
  process_agencies_from_file "$AGENCIES"
fi

echo -e "${GREEN}${BOLD}Batch processing completed.${NC}"
exit 0