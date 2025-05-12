#!/bin/bash
set -e

# Script to run integration tests for APHIS Bird Flu HMS-MFE components
# Can be run in both local development and CI environments

# Default values
RUN_MODE="local"  # 'local' or 'ci'
COMPONENT="all"   # 'all', 'dashboard', 'genetic', 'transmission', or 'federation'
HEADED_MODE=false

# Process arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --ci)
      RUN_MODE="ci"
      shift
      ;;
    --local)
      RUN_MODE="local"
      shift
      ;;
    --component)
      COMPONENT="$2"
      shift
      shift
      ;;
    --headed)
      HEADED_MODE=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --ci                 Run in CI mode (uses Docker containers)"
      echo "  --local              Run in local mode (default)"
      echo "  --component VALUE    Specify component to test: all, dashboard, genetic, transmission, federation"
      echo "  --headed             Run tests in headed mode (shows browser)"
      echo "  --help               Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Heading
echo "=============================================="
echo "APHIS Bird Flu HMS-MFE Integration Tests"
echo "=============================================="
echo "Mode: $RUN_MODE"
echo "Component: $COMPONENT"
echo "Headed mode: $HEADED_MODE"
echo "=============================================="

# Verify dependencies
if [[ "$RUN_MODE" == "ci" ]]; then
  # Check for Docker
  if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required but not installed."
    exit 1
  fi
  
  # Check for Docker Compose
  if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is required but not installed."
    exit 1
  fi
else
  # Check for Node.js
  if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not installed."
    exit 1
  fi
  
  # Check for npm
  if ! command -v npm &> /dev/null; then
    echo "Error: npm is required but not installed."
    exit 1
  fi
fi

# Function to run tests
run_tests() {
  echo "Starting test services..."
  
  if [[ "$RUN_MODE" == "ci" ]]; then
    # CI mode using Docker Compose
    docker-compose -f docker-compose.test.yml build
    
    # Determine test command based on component
    TEST_CMD="npm run test"
    case "$COMPONENT" in
      "dashboard")
        TEST_CMD="npm run test:dashboard"
        ;;
      "genetic")
        TEST_CMD="npm run test:genetic"
        ;;
      "transmission")
        TEST_CMD="npm run test:transmission"
        ;;
      "federation")
        TEST_CMD="npm run test:federation"
        ;;
    esac
    
    if [[ "$HEADED_MODE" == true ]]; then
      TEST_CMD="$TEST_CMD -- --headed"
    fi
    
    # Run tests in Docker
    docker-compose -f docker-compose.test.yml run tests sh -c "$TEST_CMD"
    
    # Cleanup
    docker-compose -f docker-compose.test.yml down
  else
    # Local mode
    cd tests
    
    # Ensure dependencies are installed
    npm ci
    
    # Install Playwright browsers if needed
    if ! [ -d ~/.cache/ms-playwright ]; then
      npx playwright install
    fi
    
    # Start local servers in background
    echo "Starting mock servers..."
    cd ../mock-data
    npm start &
    MOCK_PID=$!
    
    # Give servers time to start
    sleep 5
    
    # Return to tests directory
    cd ../tests
    
    # Determine test command based on component
    TEST_CMD="npm run test"
    case "$COMPONENT" in
      "dashboard")
        TEST_CMD="npm run test:dashboard"
        ;;
      "genetic")
        TEST_CMD="npm run test:genetic"
        ;;
      "transmission")
        TEST_CMD="npm run test:transmission"
        ;;
      "federation")
        TEST_CMD="npm run test:federation"
        ;;
    esac
    
    if [[ "$HEADED_MODE" == true ]]; then
      TEST_CMD="npm run test:headful"
    fi
    
    # Run the tests
    $TEST_CMD
    
    # Cleanup
    kill $MOCK_PID
  fi
}

# Main execution
if run_tests; then
  echo "✅ Tests completed successfully!"
  exit 0
else
  echo "❌ Tests failed!"
  exit 1
fi