#!/bin/bash
# Agency Status Dashboard
# This script displays the status of agency implementation

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Default values
CONFIG_FILE="$SCRIPT_DIR/config/agency_data.json"
TRACKER_FILE="$SCRIPT_DIR/config/agency_progress.json"
VERBOSE=false

# Show usage
function show_usage() {
  echo -e "${BOLD}Agency Status Dashboard${NC}"
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  -c, --config FILE     Config file [default: config/agency_data.json]"
  echo "  -t, --tracker FILE    Tracker file [default: config/agency_progress.json]"
  echo "  -v, --verbose         Verbose output"
  echo "  -h, --help            Show this help message"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -c|--config)
      CONFIG_FILE="$2"
      shift 2
      ;;
    -t|--tracker)
      TRACKER_FILE="$2"
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

# Create progress tracker file if it doesn't exist
if [[ ! -f "$TRACKER_FILE" ]]; then
  echo "Creating new progress tracker file: $TRACKER_FILE"
  
  # Create empty tracker file
  cat > "$TRACKER_FILE" << EOF
{
  "agencies": {},
  "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
fi

# Display status dashboard
function display_dashboard() {
  if [[ ! -f "$TRACKER_FILE" ]]; then
    echo "Error: Tracker file not found: $TRACKER_FILE"
    exit 1
  fi
  
  echo -e "${BOLD}Agency Implementation Status${NC}"
  echo -e "---------------------------"
  
  # Count completed and total agencies
  local total_agencies=$(jq '.agencies | length' "$TRACKER_FILE")
  local completed_agencies=$(jq '.agencies | to_entries[] | select(.value.status == "completed") | length' "$TRACKER_FILE")
  local in_progress_agencies=$(jq '.agencies | to_entries[] | select(.value.status == "in_progress") | length' "$TRACKER_FILE")
  
  local tier1_agencies=("HHS" "USDA" "DOD" "TREAS" "DOJ" "DHS" "DOS" "DOE")
  local tier2_agencies=("DOC" "DOL" "HUD" "DOT" "ED" "VA" "DOI")

  # Count tier status
  local tier1_total=${#tier1_agencies[@]}
  local tier2_total=${#tier2_agencies[@]}
  local tier3_agencies=("EPA" "SBA" "SSA" "NASA" "NSF" "USAID" "FCC" "OPM")
  local tier3_total=${#tier3_agencies[@]}
  local tier4_agencies=("CFPB" "CFTC" "CPSC" "EEOC" "FTC" "GSA" "NARA" "NRC" "PBGC" "SEC")
  local tier4_total=${#tier4_agencies[@]}

  local tier1_completed=0
  local tier2_completed=0
  local tier3_completed=0
  local tier4_completed=0

  # Count completed agencies by tier
  for agency in "${tier1_agencies[@]}"; do
    if [[ $(jq -r ".agencies.\"$agency\".status" "$TRACKER_FILE" 2>/dev/null) == "completed" ]]; then
      tier1_completed=$((tier1_completed+1))
    fi
  done

  for agency in "${tier2_agencies[@]}"; do
    if [[ $(jq -r ".agencies.\"$agency\".status" "$TRACKER_FILE" 2>/dev/null) == "completed" ]]; then
      tier2_completed=$((tier2_completed+1))
    fi
  done

  for agency in "${tier3_agencies[@]}"; do
    if [[ $(jq -r ".agencies.\"$agency\".status" "$TRACKER_FILE" 2>/dev/null) == "completed" ]]; then
      tier3_completed=$((tier3_completed+1))
    fi
  done

  for agency in "${tier4_agencies[@]}"; do
    if [[ $(jq -r ".agencies.\"$agency\".status" "$TRACKER_FILE" 2>/dev/null) == "completed" ]]; then
      tier4_completed=$((tier4_completed+1))
    fi
  done
  
  # Calculate percentages (safely)
  local tier1_percent=0
  local tier2_percent=0
  local tier3_percent=0
  local tier4_percent=0
  
  if [[ $tier1_total -gt 0 ]]; then
    tier1_percent=$((tier1_completed * 100 / tier1_total))
  fi
  
  if [[ $tier2_total -gt 0 ]]; then
    tier2_percent=$((tier2_completed * 100 / tier2_total))
  fi
  
  if [[ $tier3_total -gt 0 ]]; then
    tier3_percent=$((tier3_completed * 100 / tier3_total))
  fi
  
  if [[ $tier4_total -gt 0 ]]; then
    tier4_percent=$((tier4_completed * 100 / tier4_total))
  fi
  
  # Create progress bars
  function create_progress_bar() {
    local percent=$1
    local filled=$((percent / 10))
    local empty=$((10 - filled))
    
    local bar="["
    for ((i=0; i<filled; i++)); do
      bar+="█"
    done
    for ((i=0; i<empty; i++)); do
      bar+="░"
    done
    bar+="]"
    
    echo "$bar"
  }
  
  # Display tier progress
  echo -e "Tier 1: $(create_progress_bar $tier1_percent) ${tier1_percent}% (${tier1_completed}/${tier1_total} agencies)"
  echo -e "Tier 2: $(create_progress_bar $tier2_percent) ${tier2_percent}% (${tier2_completed}/${tier2_total} agencies)"
  echo -e "Tier 3: $(create_progress_bar $tier3_percent) ${tier3_percent}% (${tier3_completed}/${tier3_total} agencies)"
  echo -e "Tier 4: $(create_progress_bar $tier4_percent) ${tier4_percent}% (${tier4_completed}/${tier4_total}+ agencies)"
  
  echo
  
  # Get recently completed agencies
  echo -e "${BOLD}Recently Completed:${NC}"
  jq -r '.agencies | to_entries[] | select(.value.status == "completed") | .key' "$TRACKER_FILE" | head -5 | while read -r agency; do
    echo -e "- ${GREEN}${agency}${NC}"
  done
  
  echo
  
  # Get in-progress agencies
  echo -e "${BOLD}In Progress:${NC}"
  jq -r '.agencies | to_entries[] | select(.value.status == "in_progress") | "\(.key) (\(.value.completion)% complete)"' "$TRACKER_FILE" | head -5 | while read -r line; do
    echo -e "- ${YELLOW}${line}${NC}"
  done
  
  echo
  
  # Display last updated timestamp
  local last_updated=$(jq -r '.last_updated' "$TRACKER_FILE")
  echo -e "Last updated: ${CYAN}${last_updated}${NC}"
  
  # Display verbose information if requested
  if $VERBOSE; then
    echo
    echo -e "${BOLD}Detailed Status:${NC}"
    
    jq -r '.agencies | to_entries[] | "\(.key) [\(.value.status)] - Issue Finder: \(.value.components.issue_finder), Research Connector: \(.value.components.research_connector), ASCII Art: \(.value.components.ascii_art)"' "$TRACKER_FILE" | sort | while read -r line; do
      local status_start=$(echo "$line" | grep -o '\[[^]]*\]')
      
      if [[ "$status_start" == "[completed]" ]]; then
        echo -e "${GREEN}${line}${NC}"
      elif [[ "$status_start" == "[in_progress]" ]]; then
        echo -e "${YELLOW}${line}${NC}"
      else
        echo -e "${RED}${line}${NC}"
      fi
    done
  fi
}

# Main execution
# Display dashboard
display_dashboard

exit 0