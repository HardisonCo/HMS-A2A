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

# Check agency implementation status
function check_agency_status() {
  local agency=$1
  local agency_lower=$(echo "$agency" | tr '[:upper:]' '[:lower:]')
  
  # Check if issue finder exists
  local issue_finder="$SCRIPT_DIR/agency_issue_finder/agencies/${agency_lower}_finder.py"
  local has_issue_finder=false
  if [[ -f "$issue_finder" ]]; then
    has_issue_finder=true
  fi
  
  # Check if research connector exists
  local research_connector="$SCRIPT_DIR/agencies/${agency_lower}_connector.py"
  local has_research_connector=false
  if [[ -f "$research_connector" ]]; then
    has_research_connector=true
  fi
  
  # Check if ASCII art exists
  local ascii_art="$SCRIPT_DIR/templates/${agency_lower}_ascii.txt"
  local has_ascii_art=false
  if [[ -f "$ascii_art" ]]; then
    has_ascii_art=true
  fi
  
  # Determine overall status
  local status="not_started"
  if $has_issue_finder && $has_research_connector && $has_ascii_art; then
    status="completed"
  elif $has_issue_finder || $has_research_connector || $has_ascii_art; then
    status="in_progress"
  fi
  
  # Calculate completion percentage
  local completion=0
  if $has_issue_finder; then
    completion=$((completion + 34))
  fi
  if $has_research_connector; then
    completion=$((completion + 33))
  fi
  if $has_ascii_art; then
    completion=$((completion + 33))
  fi
  
  # Return status as JSON
  echo "{\"status\":\"$status\",\"completion\":$completion,\"components\":{\"issue_finder\":$has_issue_finder,\"research_connector\":$has_research_connector,\"ascii_art\":$has_ascii_art}}"
}

# Update progress tracker
function update_progress_tracker() {
  if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    exit 1
  fi
  
  if [[ ! -f "$TRACKER_FILE" ]]; then
    echo "Error: Tracker file not found: $TRACKER_FILE"
    exit 1
  fi
  
  echo "Updating progress tracker..."
  
  # Get all agencies from config file
  local agencies=$(grep -o '"acronym": "[^"]*"' "$CONFIG_FILE" | cut -d'"' -f4)
  
  # Create temporary file for updated tracker
  local temp_file=$(mktemp)
  
  # Start writing JSON
  echo "{" > "$temp_file"
  echo "  \"agencies\": {" >> "$temp_file"
  
  # Process each agency
  local first=true
  for agency in $agencies; do
    if $first; then
      first=false
    else
      echo "," >> "$temp_file"
    fi
    
    # Check agency status
    local status_json=$(check_agency_status "$agency")
    
    # Write agency status to tracker
    echo -n "    \"$agency\": $status_json" >> "$temp_file"
  done
  
  # Finish writing JSON
  echo "" >> "$temp_file"
  echo "  }," >> "$temp_file"
  echo "  \"last_updated\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" >> "$temp_file"
  echo "}" >> "$temp_file"
  
  # Replace tracker file with updated version
  mv "$temp_file" "$TRACKER_FILE"
  
  echo "Progress tracker updated: $TRACKER_FILE"
}

# Display status dashboard
function display_dashboard() {
  if [[ ! -f "$TRACKER_FILE" ]]; then
    echo "Error: Tracker file not found: $TRACKER_FILE"
    exit 1
  fi
  
  echo -e "${BOLD}Agency Implementation Status${NC}"
  echo -e "---------------------------"
  
  # Get statistics by tier
  local tier1_total=$(grep -o '"tier": 1' "$CONFIG_FILE" | wc -l)
  local tier2_total=$(grep -o '"tier": 2' "$CONFIG_FILE" | wc -l)
  local tier3_total=$(grep -o '"tier": 3' "$CONFIG_FILE" | wc -l)
  local tier4_total=$(grep -o '"tier": 4' "$CONFIG_FILE" | wc -l)
  
  local tier1_completed=$(jq -r '.agencies | to_entries[] | select(.value.status == "completed") | .key' "$TRACKER_FILE" | grep -f <(grep -A 1 '"tier": 1' "$CONFIG_FILE" | grep -o '"acronym": "[^"]*"' | cut -d'"' -f4) | wc -l)
  local tier2_completed=$(jq -r '.agencies | to_entries[] | select(.value.status == "completed") | .key' "$TRACKER_FILE" | grep -f <(grep -A 1 '"tier": 2' "$CONFIG_FILE" | grep -o '"acronym": "[^"]*"' | cut -d'"' -f4) | wc -l)
  local tier3_completed=$(jq -r '.agencies | to_entries[] | select(.value.status == "completed") | .key' "$TRACKER_FILE" | grep -f <(grep -A 1 '"tier": 3' "$CONFIG_FILE" | grep -o '"acronym": "[^"]*"' | cut -d'"' -f4) | wc -l)
  local tier4_completed=$(jq -r '.agencies | to_entries[] | select(.value.status == "completed") | .key' "$TRACKER_FILE" | grep -f <(grep -A 1 '"tier": 4' "$CONFIG_FILE" | grep -o '"acronym": "[^"]*"' | cut -d'"' -f4) | wc -l)
  
  # Calculate percentages
  local tier1_percent=$((tier1_completed * 100 / tier1_total))
  local tier2_percent=$((tier2_completed * 100 / tier2_total))
  local tier3_percent=$((tier3_completed * 100 / tier3_total))
  local tier4_percent=$((tier4_completed * 100 / tier4_total))
  
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
# Update progress tracker
update_progress_tracker

# Display dashboard
display_dashboard

exit 0