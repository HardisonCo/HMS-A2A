#!/bin/bash
# Test Agency Interface
# This script allows users to test the agency interface with different agencies

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

# Display agency menu
function display_menu() {
  echo -e "${BOLD}Agency Interface Test Tool${NC}"
  echo -e "${CYAN}Select an agency to test:${NC}"
  echo
  echo -e "${BOLD}Tier 1 Agencies:${NC}"
  echo "  1) HHS - Department of Health and Human Services"
  echo "  2) USDA - Department of Agriculture"
  echo "  3) DOD - Department of Defense"
  echo "  4) TREAS - Department of the Treasury"
  echo "  5) DOJ - Department of Justice"
  echo
  echo -e "${BOLD}Tier 2 Agencies:${NC}"
  echo "  6) DOC - Department of Commerce"
  echo "  7) DOL - Department of Labor"
  echo "  8) HUD - Department of Housing and Urban Development"
  echo
  echo -e "${BOLD}Tier 3 Agencies:${NC}"
  echo "  9) EPA - Environmental Protection Agency"
  echo " 10) NASA - National Aeronautics and Space Administration"
  echo " 11) SSA - Social Security Administration"
  echo
  echo -e "${BOLD}Tier 4 Agencies:${NC}"
  echo " 12) CFPB - Consumer Financial Protection Bureau"
  echo " 13) FTC - Federal Trade Commission"
  echo " 14) SEC - Securities and Exchange Commission"
  echo
  echo " 15) Show Status Dashboard"
  echo " 16) Exit"
  echo
  echo -e "${YELLOW}Enter your choice [1-16]:${NC}"
}

function test_agency() {
  local agency=$1
  
  echo -e "${BOLD}Testing ${agency} Interface${NC}"
  echo -e "${YELLOW}Demonstrating components for ${agency}...${NC}"
  echo
  
  # Show ASCII art
  if [ -f "$SCRIPT_DIR/templates/${agency,,}_ascii.txt" ]; then
    echo -e "${BOLD}ASCII Art:${NC}"
    cat "$SCRIPT_DIR/templates/${agency,,}_ascii.txt"
    echo
  else
    echo -e "${RED}ASCII art not found for ${agency}${NC}"
  fi
  
  # Show issue finder availability
  echo -e "${BOLD}Issue Finder:${NC}"
  if [ -f "$SCRIPT_DIR/agency_issue_finder/agencies/${agency,,}_finder.py" ]; then
    echo -e "${GREEN}Issue finder available: agency_issue_finder/agencies/${agency,,}_finder.py${NC}"
    
    # Display sample issues (simulate)
    echo
    echo "Sample issues for ${agency}:"
    echo -e "  - ${agency}-GEN-001: Systems Integration Analysis"
    echo -e "  - ${agency}-POL-001: Policy Implementation"
    echo -e "  - ${agency}-SEC-001: Security Compliance Framework"
  else
    echo -e "${RED}Issue finder not available for ${agency}${NC}"
  fi
  
  # Show research connector availability
  echo
  echo -e "${BOLD}Research Connector:${NC}"
  if [ -f "$SCRIPT_DIR/agencies/${agency,,}_connector.py" ]; then
    echo -e "${GREEN}Research connector available: agencies/${agency,,}_connector.py${NC}"
    
    # Display sample recommendations (simulate)
    echo
    echo "Sample recommendations for ${agency}:"
    echo -e "  - Enhance integration capabilities with HMS components"
    echo -e "  - Implement comprehensive testing framework"
    echo -e "  - Establish secure communication channels"
  else
    echo -e "${RED}Research connector not available for ${agency}${NC}"
  fi
  
  echo
  echo -e "${BOLD}Press Enter to continue...${NC}"
  read
}

# Main execution loop
while true; do
  clear
  display_menu
  read choice
  
  case $choice in
    1) test_agency "HHS" ;;
    2) test_agency "USDA" ;;
    3) test_agency "DOD" ;;
    4) test_agency "TREAS" ;;
    5) test_agency "DOJ" ;;
    6) test_agency "DOC" ;;
    7) test_agency "DOL" ;;
    8) test_agency "HUD" ;;
    9) test_agency "EPA" ;;
    10) test_agency "NASA" ;;
    11) test_agency "SSA" ;;
    12) test_agency "CFPB" ;;
    13) test_agency "FTC" ;;
    14) test_agency "SEC" ;;
    15) 
      clear
      "$SCRIPT_DIR/agency_status_fixed.sh"
      echo
      echo -e "${BOLD}Press Enter to continue...${NC}"
      read
      ;;
    16) 
      echo "Exiting..."
      exit 0
      ;;
    *)
      echo -e "${RED}Invalid choice. Please try again.${NC}"
      sleep 2
      ;;
  esac
done