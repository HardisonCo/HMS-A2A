#!/bin/bash

# complete_tier_1.sh
# Script to complete the implementation of remaining Tier 1 agencies (HHS, USDA, DOD)

# Stop execution on error
set -e

# Define colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'
BLUE='\033[0;34m'

echo -e "${BOLD}Completing Tier 1 Agency Implementation${NC}"
echo "------------------------------------"

# Define base directory
BASE_DIR="$(pwd)"
CONFIG_DIR="${BASE_DIR}/config"
AGENCY_PROGRESS_FILE="${CONFIG_DIR}/agency_progress.json"

# Function to implement an agency
implement_agency() {
    local agency=$1
    local component=$2
    
    echo -e "${YELLOW}Implementing ${component} for ${agency}...${NC}"
    
    # Use the agency_generator.py script to generate the component
    if [[ "$component" == "issue_finder" ]]; then
        python3 agency_generator.py --agency "$agency" --component "issue_finder"
    elif [[ "$component" == "research_connector" ]]; then
        python3 agency_generator.py --agency "$agency" --component "research_connector"
    else
        echo -e "${RED}Invalid component: ${component}${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Successfully implemented ${component} for ${agency}${NC}"
}

# Array of agencies and their missing components
declare -A AGENCIES
AGENCIES["HHS"]="issue_finder"
AGENCIES["USDA"]="issue_finder research_connector"
AGENCIES["DOD"]="issue_finder research_connector"

# Implement missing components for each agency
for agency in "${!AGENCIES[@]}"; do
    components=${AGENCIES[$agency]}
    
    echo -e "\n${BOLD}Processing ${agency}${NC}"
    echo "------------------------------"
    
    for component in $components; do
        implement_agency "$agency" "$component"
    done
done

# Update the implementation progress
echo -e "\n${BOLD}Updating implementation progress...${NC}"
python3 update_progress.py

# Display the updated status
echo -e "\n${BOLD}Updated Implementation Status:${NC}"
./agency_status_fixed.sh

echo -e "\n${BOLD}${GREEN}Tier 1 implementation complete!${NC}"
echo "All Tier 1 agencies now have issue finders, research connectors, and ASCII art."