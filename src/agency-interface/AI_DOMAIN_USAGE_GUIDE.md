# AI Domain Usage Guide

**Last Updated**: May 10, 2025

This guide provides instructions for using the AI domain interfaces integrated into the HMS-DEV system. These specialized interfaces allow access to domain-specific AI capabilities for 27 government agencies.

## Prerequisites

- HMS-DEV system installed
- Python 3.8 or higher
- Codex CLI installed

## Quick Start

To launch an AI domain interface, use the following command:

```bash
./launch_ai_agency.sh <agency-name>
```

For example, to launch the Center for Biologics Evaluation and Research AI domain:

```bash
./launch_ai_agency.sh cber.ai
```

Or to see the interactive menu of all available domains:

```bash
./launch_ai_agency.sh
```

## Available AI Domains

### Healthcare Domains
- **cber.ai** - Center for Biologics Evaluation and Research
- **cder.ai** - Center for Drug Evaluation and Research
- **hrsa.ai** - Health Resources and Services Administration
- **spuhc.ai** - Special Programs in Universal Health Care
- **niddk.ai** - National Institute of Diabetes and Digestive and Kidney Diseases
- **crohns.ai** - Crohn's Disease Program
- **nccih.ai** - National Center for Complementary and Integrative Health
- **oash.ai** - Office of the Assistant Secretary for Health
- **phm.ai** - Population Health Management

### Safety Domains
- **aphis.ai** - Animal and Plant Health Inspection Service
- **nhtsa.ai** - National Highway Traffic Safety Administration
- **cpsc.ai** - Consumer Product Safety Commission
- **bsee.ai** - Bureau of Safety and Environmental Enforcement
- **ntsb.ai** - National Transportation Safety Board

### Economic & Housing Domains
- **fhfa.ai** - Federal Housing Finance Agency
- **usitc.ai** - U.S. International Trade Commission
- **ustda.ai** - U.S. Trade and Development Agency
- **usich.ai** - U.S. Interagency Council on Homelessness

### Education & Nutrition Domains
- **doed.ai** - Department of Education
- **nslp.ai** - National School Lunch Program
- **cnpp.ai** - Center for Nutrition Policy and Promotion

### Security & Policy Domains
- **hsin.ai** - Homeland Security Information Network
- **csfc.ai** - Cybersecurity & Financial Crimes
- **ondcp.ai** - Office of National Drug Control Policy

### Special Domains
- **tlnt.ai** - Talent Management
- **naacp.ai** - National Association for the Advancement of Colored People

## Core Features

Each AI domain interface provides the following capabilities:

1. **Issue Finding** - Domain-specific issue identification
2. **Research Context** - Relevant knowledge and implementation details
3. **Domain-Specific AI Capabilities** - Specialized AI tools and models
4. **Custom CLI Environment** - Agency-specific Codex CLI context

## How It Works

The agency interface performs the following actions:

1. **Loads agency-specific ASCII art banner**
2. **Runs the domain-specific issue finder** - Identifies current issues and challenges
3. **Executes the research connector** - Gathers domain-specific context and knowledge
4. **Combines context** - Creates a rich, domain-specific environment for Codex
5. **Launches Codex CLI** - With pre-loaded context and capabilities

## Domain Integration

Each domain integrates with the HMS-DEV system in several ways:

1. **Knowledge Base Integration** - Connects to relevant HMS knowledge repositories
2. **Specialized Models** - Uses domain-specific AI models for analysis
3. **Cross-Domain Analysis** - Enables analysis across related domains
4. **Agency-Specific Workflows** - Tailored workflows for agency needs

## Example Usage Scenarios

### Healthcare Domains

```bash
./launch_ai_agency.sh cber.ai
```

Example prompt: "I need to analyze the effectiveness of AI models in biologics application review. What are the current best practices for model validation in this domain?"

### Safety Domains

```bash
./launch_ai_agency.sh nhtsa.ai
```

Example prompt: "Help me develop an AI strategy for improving vehicle safety analysis and accident prevention."

### Economic Domains

```bash
./launch_ai_agency.sh fhfa.ai
```

Example prompt: "I need to analyze housing market trends using AI. What approaches should we consider for market forecasting?"

### Education Domains

```bash
./launch_ai_agency.sh doed.ai
```

Example prompt: "Develop an AI framework for educational policy planning and program effectiveness assessment."

### Security Domains

```bash
./launch_ai_agency.sh hsin.ai
```

Example prompt: "How can we enhance the Homeland Security Information Network with AI capabilities for better threat detection and analysis?"

## Advanced Usage

For advanced usage and customization:

1. **Domain-Specific Configuration** - Customize the agency configuration in `config/ai_agencies/`
2. **Knowledge Base Extension** - Add domain-specific knowledge in `agency_knowledge_base/`
3. **Cross-Domain Analysis** - Use multiple domains together for comprehensive analysis
4. **Custom Issue Finding** - Create specialized issue finders for specific use cases

## Troubleshooting

If you encounter issues:

1. **Check Configuration** - Ensure agency configuration exists in `config/ai_agencies/`
2. **Verify Python Environment** - Ensure Python 3.8+ is installed
3. **Check Templates** - Ensure agency ASCII art template exists
4. **Logs** - Check logs in `~/.codex/logs/` directory