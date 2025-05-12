#!/bin/bash
# Launch AI Agency Codex CLI
# This script launches an AI-enhanced agency interface for Codex CLI

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
AGENCY_CONFIG_DIR="$HOME/.codex/agency-config"
AGENCY_DATA_DIR="$HOME/.codex/agency-data"
TEMPLATES_DIR="$SCRIPT_DIR/templates"
AGENCY_ISSUE_FINDER="$SCRIPT_DIR/agency_issue_finder"

# Ensure directories exist
mkdir -p "$AGENCY_CONFIG_DIR"
mkdir -p "$AGENCY_DATA_DIR"

# Check for required commands
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Error: Python 3 is required but not installed. Aborting.${NC}"; exit 1; }

# Function to display ASCII art for an agency
function show_agency_ascii() {
  local agency=$1
  local ascii_file="$TEMPLATES_DIR/${agency}_ascii.txt"
  
  if [[ -f "$ascii_file" ]]; then
    cat "$ascii_file"
  else
    echo -e "${YELLOW}No ASCII art found for $agency${NC}"
    echo -e "╔════════════════════════════════════════════════════════╗"
    echo -e "║                                                        ║"
    echo -e "║  $agency                                               ║"
    echo -e "║                                                        ║"
    echo -e "╚════════════════════════════════════════════════════════╝"
  fi
}

# Function to run the issue finder for an agency
function run_agency_issue_finder() {
  local agency=$1
  
  echo -e "${YELLOW}Running issue finder for ${BOLD}$agency${NC}"
  
  # Check if agency issue finder exists
  local finder_script="$AGENCY_ISSUE_FINDER/agencies/${agency}_finder.py"
  
  if [[ -f "$finder_script" ]]; then
    echo -e "${CYAN}Executing issue finder for $agency...${NC}"
    python3 "$finder_script" --output-format=json
  else
    echo -e "${YELLOW}No specialized issue finder found for $agency. Using default finder.${NC}"
    python3 "$AGENCY_ISSUE_FINDER/issue_finder.py" --agency="$agency" --output-format=json
  fi
}

# Function to run the research connector for an agency
function run_agency_research_connector() {
  local agency=$1
  
  echo -e "${YELLOW}Running research connector for ${BOLD}$agency${NC}"
  
  # Check if agency connector exists
  local connector_script="$SCRIPT_DIR/agencies/${agency}_connector.py"
  
  if [[ -f "$connector_script" ]]; then
    echo -e "${CYAN}Executing research connector for $agency...${NC}"
    python3 "$connector_script" --output=context
  else
    echo -e "${YELLOW}No specialized research connector found for $agency.${NC}"
    echo "{}"
  fi
}

# Function to launch Codex with agency context
function launch_agency_codex() {
  local agency=$1
  local agency_name=$(echo "$agency" | tr '[:lower:]' '[:upper:]')
  
  clear
  echo -e "${BOLD}Launching AI-Enhanced Agency Interface for: ${CYAN}$agency${NC}"
  echo
  
  # Show ASCII art for the agency
  show_agency_ascii "$agency"
  echo
  
  # Run the issue finder and research connector to get context
  echo -e "${YELLOW}Preparing AI context for $agency...${NC}"
  
  # Create a temporary context file
  CONTEXT_FILE=$(mktemp)
  
  # Run the issue finder and research connector
  echo -e "${CYAN}Finding current issues...${NC}"
  ISSUES_JSON=$(run_agency_issue_finder "$agency")
  
  echo -e "${CYAN}Gathering research context...${NC}"
  RESEARCH_JSON=$(run_agency_research_connector "$agency")
  
  # Combine context
  echo "{\"agency\": \"$agency\", \"issues\": $ISSUES_JSON, \"research\": $RESEARCH_JSON}" > "$CONTEXT_FILE"
  
  # Prepare Codex CLI arguments
  CODEX_ARGS="--agency=$agency --context-file=$CONTEXT_FILE"
  
  echo
  echo -e "${GREEN}${BOLD}Launching Codex CLI with $agency context...${NC}"
  echo
  
  # Create a sample prompt based on the agency
  case "$agency" in
    "cber.ai")
      PROMPT="I need to analyze the effectiveness of AI models in biologics application review. What are the current best practices for model validation in this domain?"
      ;;
    "nhtsa.ai")
      PROMPT="Help me develop an AI strategy for improving vehicle safety analysis and accident prevention."
      ;;
    "fhfa.ai")
      PROMPT="I need to analyze housing market trends using AI. What approaches should we consider for market forecasting?"
      ;;
    "doed.ai")
      PROMPT="Develop an AI framework for educational policy planning and program effectiveness assessment."
      ;;
    "hsin.ai")
      PROMPT="How can we enhance the Homeland Security Information Network with AI capabilities for better threat detection and analysis?"
      ;;
    *)
      PROMPT="What are the key AI capabilities and implementation priorities for this agency domain?"
      ;;
  esac
  
  echo -e "${CYAN}Suggested prompt:${NC}"
  echo -e "${YELLOW}\"$PROMPT\"${NC}"
  echo
  echo -e "${YELLOW}Press any key to launch Codex with this prompt, or Ctrl+C to cancel...${NC}"
  read -n 1 -s
  
  # Launch Codex CLI with context
  echo -e "${GREEN}Executing: codex $CODEX_ARGS \"$PROMPT\"${NC}"
  # Uncomment the next line when ready to actually execute Codex:
  # codex $CODEX_ARGS "$PROMPT"
  
  # For demo purposes, simulate running Codex
  echo -e "${BLUE}[Demo] Launching Codex with $agency context...${NC}"
  sleep 2
  echo -e "${BLUE}[Demo] Codex session would start here with domain-specific AI capabilities.${NC}"
  
  # Clean up
  rm -f "$CONTEXT_FILE"
}

# Function to show the main menu
function show_main_menu() {
  clear
  echo -e "${BOLD}┌───────────────────────────────────────────┐${NC}"
  echo -e "${BOLD}│   AI-Enhanced Agency Interface            │${NC}"
  echo -e "${BOLD}└───────────────────────────────────────────┘${NC}"
  echo
  echo -e "Select an AI agency domain to continue:"
  echo
  echo -e "${BLUE}Healthcare Domains:${NC}"
  echo -e "  ${BLUE}1${NC}. cber.ai - Center for Biologics Evaluation and Research"
  echo -e "  ${BLUE}2${NC}. cder.ai - Center for Drug Evaluation and Research"
  echo -e "  ${BLUE}3${NC}. hrsa.ai - Health Resources and Services Administration"
  echo
  echo -e "${BLUE}Safety Domains:${NC}"
  echo -e "  ${BLUE}4${NC}. aphis.ai - Animal and Plant Health Inspection Service"
  echo -e "  ${BLUE}5${NC}. nhtsa.ai - National Highway Traffic Safety Administration"
  echo -e "  ${BLUE}6${NC}. cpsc.ai - Consumer Product Safety Commission"
  echo
  echo -e "${BLUE}Economic Domains:${NC}"
  echo -e "  ${BLUE}7${NC}. fhfa.ai - Federal Housing Finance Agency"
  echo -e "  ${BLUE}8${NC}. usitc.ai - U.S. International Trade Commission"
  echo
  echo -e "${BLUE}Education Domains:${NC}"
  echo -e "  ${BLUE}9${NC}. doed.ai - Department of Education"
  echo -e "  ${BLUE}10${NC}. nslp.ai - National School Lunch Program"
  echo
  echo -e "${BLUE}Security Domains:${NC}"
  echo -e "  ${BLUE}11${NC}. hsin.ai - Homeland Security Information Network"
  echo -e "  ${BLUE}12${NC}. csfc.ai - Cybersecurity & Financial Crimes"
  echo
  echo -e "${BLUE}Other Options:${NC}"
  echo -e "  ${BLUE}c${NC}. Custom agency (specify name)"
  echo -e "  ${BLUE}q${NC}. Quit"
  echo
  echo -n "Enter selection [1-12, c, or q]: "
  read -r selection
  
  case "$selection" in
    1) launch_agency_codex "cber.ai" ;;
    2) launch_agency_codex "cder.ai" ;;
    3) launch_agency_codex "hrsa.ai" ;;
    4) launch_agency_codex "aphis.ai" ;;
    5) launch_agency_codex "nhtsa.ai" ;;
    6) launch_agency_codex "cpsc.ai" ;;
    7) launch_agency_codex "fhfa.ai" ;;
    8) launch_agency_codex "usitc.ai" ;;
    9) launch_agency_codex "doed.ai" ;;
    10) launch_agency_codex "nslp.ai" ;;
    11) launch_agency_codex "hsin.ai" ;;
    12) launch_agency_codex "csfc.ai" ;;
    c|C)
      echo -n "Enter agency name (e.g., phm.ai): "
      read -r custom_agency
      launch_agency_codex "$custom_agency"
      ;;
    q|Q)
      echo -e "${CYAN}Exiting AI Agency Interface.${NC}"
      exit 0
      ;;
    *)
      echo -e "${RED}Invalid selection. Please try again.${NC}"
      sleep 1
      show_main_menu
      ;;
  esac
  
  # Return to main menu after the agency session
  echo
  echo -e "${CYAN}Returning to agency selection...${NC}"
  sleep 2
  show_main_menu
}

# Handle direct agency specification
if [[ $# -gt 0 ]]; then
  agency=$1
  launch_agency_codex "$agency"
else
  # Show the main menu
  show_main_menu
fi