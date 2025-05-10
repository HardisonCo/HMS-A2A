#!/bin/bash
# HMS-A2A CoRT Demo Start Script
# This script provides a convenient way to start HMS-A2A services with CoRT enabled

# Make the script executable 
chmod +x start.sh

# Validate that the start script exists
if [ ! -f "start.sh" ]; then
  echo "❌ Error: start.sh script not found!"
  exit 1
fi

# Run tests to ensure CoRT is working properly
echo "🧪 Running CoRT specification tests..."
python3 -m tests.test_cort_specs

# Check if tests were successful
if [ $? -ne 0 ]; then
  echo "❌ Core specification tests failed! Please fix issues before continuing."
  exit 1
fi

echo "✅ CoRT specification tests passed successfully!"

# Skip integration tests if lacking dependencies
if python3 -c "import langchain_google_genai" 2>/dev/null; then
  echo "🧪 Running integration tests..."
  python3 -m tests.test_cort_integration
  python3 -m tests.test_cort_deal_negotiation
  python3 -m tests.test_cort_full_cycle
else
  echo "⚠️ Skipping integration tests (dependencies not installed)"
  echo "To run full tests, install: pip install langchain-google-genai google-generativeai pydantic"
fi

echo "🚀 Starting services with CoRT enabled..."

# Start all services with CoRT enabled
./start.sh --cort