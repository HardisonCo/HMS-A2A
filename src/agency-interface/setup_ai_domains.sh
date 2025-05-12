#!/bin/bash
# Setup AI Domains
#
# This script sets up the necessary components for AI domains integration
# with the HMS-DEV system.

# Create necessary directories
mkdir -p ~/.codex/agency-config/ai_domains
mkdir -p ~/.codex/agency-data/ai_domains

# Process Phase 1 (high priority) agencies
echo "Processing Phase 1 AI agencies..."
python3 ai_agency_generator.py --file phase1_ai_agencies.txt

# Create test domains data
mkdir -p ./config/ai_domains/data

# Create integration completion tracker
echo '{
  "ai_domains": {
    "last_updated": "'$(date -Iseconds)'",
    "phase1_complete": false,
    "phase2_complete": false,
    "overall_progress": 0,
    "domains_processed": []
  }
}' > ./config/ai_domains/integration_status.json

echo "Phase 1 AI domain setup complete."
echo "To process Phase 2 agencies, run: python3 ai_agency_generator.py --file phase2_ai_agencies.txt"
