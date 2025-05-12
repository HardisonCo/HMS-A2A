# AI Domain Integration

This directory contains tools and configurations for integrating AI domain-specific agencies with the HMS-DEV system and Codex CLI.

## Overview

The AI domain integration adds support for 27 government agencies that use AI for specific domains such as healthcare, safety, agriculture, and more. Each agency receives specialized components:

- Issue finders for identifying AI-related issues
- Research connectors for accessing AI domain knowledge
- Agency-specific CLI branding
- Domain-specific configuration

## Getting Started

### Prerequisites

- Python 3.8+
- HMS-DEV agency-interface
- Codex CLI

### Setup

To set up the AI domain integration:

1. Run the process script to generate agency files:

```bash
# Create agency files and setup script
python process_ai_agencies.py --setup

# Run the setup script to install Phase 1 agencies
bash setup_ai_domains.sh
```

2. Verify the installation:

```bash
# Test a Phase 1 agency
python ai_agency_generator.py --agency "CBER" --name "Center for Biologics Evaluation and Research"
```

## Components

### AI Agency Generator

The `ai_agency_generator.py` script creates components for AI-focused agencies:

```bash
# Generate components for a specific agency
python ai_agency_generator.py --agency ACRONYM --name "Agency Name" [--domain domain_type]

# Process a file containing agency specifications
python ai_agency_generator.py --file agency_list.txt
```

### Process Script

The `process_ai_agencies.py` script manages the full implementation:

```bash
# Generate agency files and setup script
python process_ai_agencies.py --setup

# Generate agency files, setup script, and run the setup
python process_ai_agencies.py --setup --run
```

### Implementation Plan

The `AI_DOMAIN_IMPLEMENTATION_PLAN.md` file contains the detailed implementation plan for the AI domain integration, including:

- Implementation phases
- Technical details
- Timeline and milestones
- Dependencies and risks
- Validation approach

## Domain Types

The AI domain integration supports these domain types:

- **healthcare**: AI for medical diagnosis, treatment, and health management
- **agriculture**: AI for crop protection, animal health, and inspection
- **safety**: AI for product safety, risk assessment, and recall prediction
- **environment**: AI for environmental monitoring and safety
- **finance**: AI for financial risk assessment and fraud detection
- **nutrition**: AI for nutrition analysis and policy modeling
- **food**: AI for food safety and quality control
- **transportation**: AI for crash prevention and vehicle safety
- **drugs**: AI for drug reviews and pharmacovigilance
- **biologics**: AI for biologics evaluation and manufacturing oversight
- **complementary_health**: AI for complementary health research

## Directory Structure

```
agency-interface/
  ├── ai_agency_generator.py          # AI agency generator
  ├── process_ai_agencies.py          # Process script
  ├── AI_DOMAIN_IMPLEMENTATION_PLAN.md # Implementation plan
  ├── AI_DOMAINS_README.md            # This README
  ├── phase1_ai_agencies.txt          # Phase 1 agency list
  ├── phase2_ai_agencies.txt          # Phase 2 agency list
  ├── setup_ai_domains.sh             # Setup script
  ├── agency_issue_finder/
  │   └── agencies/                   # Agency issue finders
  ├── agencies/                       # Agency connectors
  ├── config/
  │   ├── agency_data.json            # Agency configuration
  │   └── ai_domains/                 # AI domain configuration
  └── templates/                      # Agency ASCII art templates
```

## Implementation Phases

The AI domain integration follows these implementation phases:

1. **Phase 1**: Core Healthcare and Safety Agencies (May-June 2025)
2. **Phase 2**: Economic and Additional Health Agencies (July-August 2025)
3. **Phase 3**: Social Services and Additional Safety Agencies (September-October 2025)
4. **Phase 4**: Security and Remaining Agencies (November-December 2025)

## Codex CLI Integration

The AI domain integration extends the Codex CLI with these commands:

```bash
# View AI domain information
codex hms ai info [agency]

# List AI models for domain
codex hms ai models [agency]

# Check AI model validation status
codex hms ai validate [agency] [model]

# Generate AI implementation report
codex hms ai report [agency]
```

## Additional Resources

- [AI Domain Implementation Plan](./AI_DOMAIN_IMPLEMENTATION_PLAN.md)
- [HMS-DEV CLAUDE.md](../CLAUDE.md)
- [Codex CLI Documentation](../../codex-cli/README.md)

## Troubleshooting

If you encounter issues:

1. Check the agency configuration in `config/agency_data.json`
2. Verify the domain-specific files in `config/ai_domains`
3. Check permissions on the generated Python files
4. Review the implementation logs in `logs/ai_domain_implementation.log`

## Contributing

To add a new AI domain type:

1. Add the domain type to `AI_DOMAIN_TEMPLATES` in `ai_agency_generator.py`
2. Create domain-specific templates for issue finders and research connectors
3. Update the domain mapping in `DOMAIN_TYPE_MAP`
4. Update the README and implementation plan