#!/bin/bash
# Start Tier 3 Agency Implementation
# This script starts the implementation of Tier 3 agencies

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

echo -e "${BOLD}Starting Tier 3 Agency Implementation${NC}"
echo -e "${YELLOW}Processing agencies from tier3_agencies.txt...${NC}"
echo

# Run batch processing
"$SCRIPT_DIR/batch_process_agencies.sh" --agencies "$SCRIPT_DIR/tier3_agencies.txt"

# Check status
echo
echo -e "${BOLD}Implementation Status After Processing:${NC}"
"$SCRIPT_DIR/agency_status_fixed.sh"

echo
echo -e "${GREEN}Tier 3 agency implementation complete.${NC}"
echo -e "${CYAN}Run './start_tier_4.sh' to continue with Tier 4 agencies.${NC}"