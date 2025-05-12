#!/bin/bash
# Start script for the Unified Notification System

# Function to check dependencies
check_dependencies() {
  echo "Checking dependencies..."
  
  # Check Python version
  python3 --version >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required but not found"
    exit 1
  fi
  
  # Check for required Python packages
  python3 -c "import aiohttp, jinja2, asyncio" >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
  fi
}

# Function to run demo mode
run_demo() {
  echo "Starting Unified Notification System in demo mode..."
  python3 demo.py
}

# Function to run the full system
run_system() {
  echo "Starting Unified Notification System..."
  
  if [ "$1" == "once" ]; then
    echo "Running once and exiting..."
    python3 main.py --once $CONFIG_ARG
  else
    python3 main.py $CONFIG_ARG
  fi
}

# Parse command line arguments
CONFIG_FILE=""
CONFIG_ARG=""
MODE="normal"

while [ "$1" != "" ]; do
  case $1 in
    --config | -c )
      shift
      CONFIG_FILE=$1
      CONFIG_ARG="--config $CONFIG_FILE"
      ;;
    --demo | -d )
      MODE="demo"
      ;;
    --once | -o )
      MODE="once"
      ;;
    --help | -h )
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --config, -c FILE    Use specific config file"
      echo "  --demo, -d           Run in demo mode"
      echo "  --once, -o           Run once and exit"
      echo "  --help, -h           Show this help"
      exit
      ;;
    * )
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
  esac
  shift
done

# Main script
check_dependencies

case $MODE in
  "demo")
    run_demo
    ;;
  "once")
    run_system "once"
    ;;
  "normal")
    run_system
    ;;
esac