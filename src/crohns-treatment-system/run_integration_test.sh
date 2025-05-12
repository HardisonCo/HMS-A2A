#!/bin/bash
# Run the integration test for the Crohn's Disease Treatment System

echo "Running Crohn's Disease Treatment System Integration Test"
echo "========================================================"
echo

# Create required directories if they don't exist
mkdir -p tests/integration
mkdir -p src/coordination/a2a-integration
mkdir -p src/research/agx-integration

# Set environment variables for testing
export AGX_API_KEY="test_key"
export AGX_BASE_URL="http://localhost:8000/api/v1"
export GENETIC_ENGINE_MOCK="true"  # Use mock implementation for testing

# Run the integration test
python3 tests/integration/test_research_to_treatment.py

# Store the exit code
EXIT_CODE=$?

# Display result based on exit code
if [ $EXIT_CODE -eq 0 ]; then
    echo
    echo "✅ Integration test PASSED"
else
    echo
    echo "❌ Integration test FAILED"
fi

exit $EXIT_CODE