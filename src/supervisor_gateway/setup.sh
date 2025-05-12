#!/bin/bash

# Supervisor Gateway Setup Script
#
# This script sets up the development environment for the Supervisor Gateway.

set -e

echo "Setting up Supervisor Gateway development environment..."

# Ensure the script is being run from the correct directory
if [ ! -f "package.json" ]; then
  echo "Error: This script must be run from the supervisor_gateway directory."
  exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Create knowledge base directory if it doesn't exist
echo "Setting up knowledge base directory..."
KB_DIR="../../../agent_knowledge_base"
mkdir -p $KB_DIR

# Check if knowledge bases exist, if not create default ones
if [ ! -f "$KB_DIR/economic_kb.json" ]; then
  echo "Creating default economic knowledge base..."
  # Use default economic_kb.json from templates
  if [ -f "./templates/economic_kb.json" ]; then
    cp ./templates/economic_kb.json $KB_DIR/
  else
    echo "Warning: Default economic knowledge base template not found."
    echo "  Please create it manually at $KB_DIR/economic_kb.json"
  fi
fi

# Build the project
echo "Building the project..."
npm run build

# Run typechecking
echo "Running type checking..."
npm run typecheck

# Run linting
echo "Running linting..."
npm run lint

# Create a simple example script
echo "Creating example script..."
cat > ./run_example.sh << 'EOL'
#!/bin/bash
# Example script to run the Supervisor Gateway

# Build the project
npm run build

# Run the application
node dist/index.js
EOL

chmod +x ./run_example.sh

echo "Setup complete! You can now run the application with:"
echo "  ./run_example.sh"
echo ""
echo "Or for development with auto-reload:"
echo "  npm run dev"
echo ""
echo "Happy coding!"