#!/bin/bash
# Agency Interface for Codex CLI
# A specialized launcher for agency-specific Codex CLI instances

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
AGENCY_CONFIG_DIR="$HOME/.codex/agency-config"
AGENCY_DATA_DIR="$HOME/.codex/agency-data"
ISSUE_FINDER_PATH="/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-DEV/agency-interface/agency_issue_finder"

# Ensure directories exist
mkdir -p "$AGENCY_CONFIG_DIR"
mkdir -p "$AGENCY_DATA_DIR"
mkdir -p "$ISSUE_FINDER_PATH"

# ASCII Art for Agencies
function show_hhs_ascii() {
  cat << "EOF"
 █████████████████████████████████████████████████████████
 █                                                       █
 █   ██   ██ ██   ██ ███████                            █
 █   ██   ██ ██   ██ ██                                 █
 █   ███████ ███████ ███████                            █
 █   ██   ██ ██   ██      ██                            █
 █   ██   ██ ██   ██ ███████                            █
 █                                                       █
 █       U.S. DEPARTMENT OF HEALTH & HUMAN SERVICES      █
 █                                                       █
 █████████████████████████████████████████████████████████
EOF
}

function show_usda_ascii() {
  cat << "EOF"
 █████████████████████████████████████████████████████████
 █                                                       █
 █   ██    ██ ███████ ██████   █████                     █
 █   ██    ██ ██      ██   ██ ██   ██                    █
 █   ██    ██ ███████ ██   ██ ███████                    █
 █   ██    ██      ██ ██   ██ ██   ██                    █
 █    ██████  ███████ ██████  ██   ██                    █
 █                                                       █
 █       U.S. DEPARTMENT OF AGRICULTURE                  █
 █                                                       █
 █████████████████████████████████████████████████████████
EOF
}

function show_aphis_ascii() {
  cat << "EOF"
 █████████████████████████████████████████████████████████
 █                                                       █
 █    █████  ██████  ██   ██ ██ ███████                  █
 █   ██   ██ ██   ██ ██   ██ ██ ██                       █
 █   ███████ ██████  ███████ ██ ███████                  █
 █   ██   ██ ██      ██   ██ ██      ██                  █
 █   ██   ██ ██      ██   ██ ██ ███████                  █
 █                                                       █
 █       ANIMAL AND PLANT HEALTH INSPECTION SERVICE      █
 █                                                       █
 █████████████████████████████████████████████████████████
EOF
}

# Agency Issue Finder Integration
function run_issue_finder() {
  local agency=$1
  local topic=$2
  
  echo -e "${YELLOW}Activating Agency Issue Finder for ${BOLD}$agency${NC} on topic: ${BOLD}$topic${NC}"
  echo -e "${YELLOW}Scanning for current issues and research materials...${NC}"
  
  # Simulated loading time
  for i in {1..20}; do
    echo -n "."
    sleep 0.1
  done
  echo ""
  
  case "$agency" in
    "APHIS")
      case "$topic" in
        "bird-flu"|"avian-influenza")
          echo -e "${GREEN}Found active critical issue: ${BOLD}Avian Influenza Outbreak${NC}"
          echo -e "${CYAN}Loading research data, case statistics, and surveillance priorities...${NC}"
          sleep 1
          echo -e "${CYAN}Preparing bird flu monitoring dashboard and data...${NC}"
          sleep 1
          CODEX_CONTEXT="avian-influenza-response"
          CODEX_ARGS="--agency-data=$AGENCY_DATA_DIR/aphis/bird-flu --agency-mode=active"
          ;;
        *)
          echo -e "${YELLOW}No specific issues found for topic: $topic${NC}"
          echo -e "${CYAN}Loading general APHIS resources and context...${NC}"
          CODEX_CONTEXT="aphis-general"
          CODEX_ARGS="--agency-data=$AGENCY_DATA_DIR/aphis/general --agency-mode=standard"
          ;;
      esac
      ;;
    
    "USDA")
      echo -e "${CYAN}Loading USDA resources and context...${NC}"
      CODEX_CONTEXT="usda-general"
      CODEX_ARGS="--agency-data=$AGENCY_DATA_DIR/usda/general --agency-mode=standard"
      ;;
      
    "HHS")
      echo -e "${CYAN}Loading HHS resources and context...${NC}"
      CODEX_CONTEXT="hhs-general"
      CODEX_ARGS="--agency-data=$AGENCY_DATA_DIR/hhs/general --agency-mode=standard"
      ;;
      
    *)
      echo -e "${RED}Unknown agency specified. Using default context.${NC}"
      CODEX_CONTEXT="default"
      CODEX_ARGS=""
      ;;
  esac
  
  return 0
}

# Setup Agent Research Repository for Bird Flu
function setup_bird_flu_research() {
  echo -e "${CYAN}Setting up bird flu research repository...${NC}"
  
  # Create bird flu data directory if it doesn't exist
  mkdir -p "$AGENCY_DATA_DIR/aphis/bird-flu"
  
  # Create symlinks to the actual implementation files
  if [ -d "/Users/arionhardison/Desktop/Codify/aphis-bird-flu" ]; then
    ln -sf "/Users/arionhardison/Desktop/Codify/aphis-bird-flu" "$AGENCY_DATA_DIR/aphis/bird-flu/implementation"
    ln -sf "/Users/arionhardison/Desktop/Codify/APHIS-BIRD-FLU-IMPLEMENTATION-PLAN.md" "$AGENCY_DATA_DIR/aphis/bird-flu/plan.md"
    ln -sf "/Users/arionhardison/Desktop/Codify/APHIS-PROGRESS-TRACKING.md" "$AGENCY_DATA_DIR/aphis/bird-flu/progress.md"
  fi
  
  echo -e "${GREEN}Bird flu research repository setup complete.${NC}"
}

# Main Menu
function show_main_menu() {
  clear
  echo -e "${BOLD}┌───────────────────────────────────────────┐${NC}"
  echo -e "${BOLD}│   Agency Codex CLI Interface              │${NC}"
  echo -e "${BOLD}└───────────────────────────────────────────┘${NC}"
  echo
  echo -e "Select an agency to continue:"
  echo -e "  ${BLUE}1${NC}. Health & Human Services (HHS)"
  echo -e "  ${BLUE}2${NC}. Department of Agriculture (USDA)"
  echo -e "  ${BLUE}3${NC}. Animal & Plant Health Inspection Service (APHIS)"
  echo -e "  ${BLUE}q${NC}. Quit"
  echo
  echo -n "Enter selection [1-3 or q]: "
  read -r selection
  
  case "$selection" in
    1)
      agency_selected "HHS"
      ;;
    2)
      agency_selected "USDA"
      ;;
    3)
      agency_selected "APHIS"
      ;;
    q|Q)
      echo -e "${CYAN}Exiting Agency Codex CLI Interface.${NC}"
      exit 0
      ;;
    *)
      echo -e "${RED}Invalid selection. Please try again.${NC}"
      sleep 1
      show_main_menu
      ;;
  esac
}

# Agency Topic Selection
function agency_selected() {
  local agency=$1
  clear
  
  case "$agency" in
    "HHS")
      show_hhs_ascii
      ;;
    "USDA")
      show_usda_ascii
      ;;
    "APHIS")
      show_aphis_ascii
      ;;
  esac
  
  echo
  echo -e "${BOLD}${agency}${NC} selected."
  echo
  
  if [ "$agency" == "APHIS" ]; then
    echo -e "Select a topic area:"
    echo -e "  ${BLUE}1${NC}. Avian Influenza (Bird Flu) Response"
    echo -e "  ${BLUE}2${NC}. General APHIS Operations"
    echo -e "  ${BLUE}b${NC}. Back to agency selection"
    echo
    echo -n "Enter selection [1-2 or b]: "
    read -r topic_selection
    
    case "$topic_selection" in
      1)
        launch_codex "$agency" "bird-flu"
        ;;
      2)
        launch_codex "$agency" "general"
        ;;
      b|B)
        show_main_menu
        ;;
      *)
        echo -e "${RED}Invalid selection. Please try again.${NC}"
        sleep 1
        agency_selected "$agency"
        ;;
    esac
  else
    echo -e "Select a topic area:"
    echo -e "  ${BLUE}1${NC}. General Operations"
    echo -e "  ${BLUE}b${NC}. Back to agency selection"
    echo
    echo -n "Enter selection [1 or b]: "
    read -r topic_selection
    
    case "$topic_selection" in
      1)
        launch_codex "$agency" "general"
        ;;
      b|B)
        show_main_menu
        ;;
      *)
        echo -e "${RED}Invalid selection. Please try again.${NC}"
        sleep 1
        agency_selected "$agency"
        ;;
    esac
  fi
}

# Launch the Codex CLI with appropriate context
function launch_codex() {
  local agency=$1
  local topic=$2
  
  clear
  case "$agency" in
    "HHS")
      show_hhs_ascii
      ;;
    "USDA")
      show_usda_ascii
      ;;
    "APHIS")
      show_aphis_ascii
      ;;
  esac
  
  echo
  echo -e "${BOLD}Launching ${agency} Codex CLI for topic: ${topic}${NC}"
  echo
  
  # Run the issue finder to load context and prepare arguments
  run_issue_finder "$agency" "$topic"
  
  # If the topic is bird-flu, ensure the research repository is set up
  if [ "$topic" == "bird-flu" ]; then
    setup_bird_flu_research
  fi
  
  # Launch the appropriate codex instance
  echo
  echo -e "${GREEN}${BOLD}Launching Codex CLI with ${agency} context...${NC}"
  echo
  
  if [ "$agency" == "APHIS" ] && [ "$topic" == "bird-flu" ]; then
    # When launching for APHIS bird flu, prepare a special prompt
    BIRD_FLU_PROMPT="I need to analyze the current status of the avian influenza tracking system implementation. Please review the implementation plan and progress tracking, then help me prioritize the next steps. Focus on adaptive sampling strategies and early outbreak detection capabilities."
    
    echo -e "${CYAN}${BIRD_FLU_PROMPT}${NC}"
    echo
    echo -e "${YELLOW}Press any key to launch Codex with this prompt...${NC}"
    read -n 1 -s
    
    # Launch codex with the bird flu context
    echo -e "${GREEN}Executing: codex ${CODEX_ARGS} \"${BIRD_FLU_PROMPT}\"${NC}"
    # Uncomment the following line to actually execute codex when ready
    # codex ${CODEX_ARGS} "${BIRD_FLU_PROMPT}"
    
    # For demo purposes, we'll just print that we would execute it
    echo -e "${YELLOW}[Demo Mode] Codex would be launched with APHIS bird flu context${NC}"
    sleep 2
  else
    # For other agencies or topics, launch with a general prompt
    echo -e "${YELLOW}Launching Codex with ${agency} context. Press any key to continue...${NC}"
    read -n 1 -s
    
    echo -e "${GREEN}Executing: codex ${CODEX_ARGS}${NC}"
    # Uncomment the following line to actually execute codex when ready
    # codex ${CODEX_ARGS}
    
    # For demo purposes, we'll just print that we would execute it
    echo -e "${YELLOW}[Demo Mode] Codex would be launched with ${agency} context${NC}"
    sleep 2
  fi
  
  # Return to the main menu after codex session
  echo
  echo -e "${CYAN}Codex session ended. Returning to agency selection.${NC}"
  sleep 2
  show_main_menu
}

# Check if running in demo mode
DEMO_MODE=false
if [ "$1" == "--demo" ]; then
  DEMO_MODE=true
  echo -e "${YELLOW}Running in demo mode. No actual Codex commands will be executed.${NC}"
  sleep 2
fi

# Start the interface
show_main_menu