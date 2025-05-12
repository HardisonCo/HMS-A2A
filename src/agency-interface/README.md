# Agency Interface for Codex CLI

This system provides a specialized interface for launching Codex CLI with agency-specific contexts, ASCII art, and issue tracking capabilities. It's designed to streamline access to federal agency data and implementation plans across healthcare and related domains.

## Overview

The agency interface system includes:

1. **Agency Launcher**: CLI tool for starting Codex with agency context
2. **ASCII Art Generator**: Creates agency-specific banners
3. **Issue Finder**: Identifies agency-related issues and relevant context
4. **Research Connector**: Provides access to implementation plans and agency data
5. **Configuration System**: Manages agency settings and data sources

## Directory Structure

```
agency-interface/
├── agency-cli.sh                  # Main launcher script
├── launch_agency_codex.sh         # Entry point script
├── common/                        # Shared utilities
│   ├── ascii_art_generator.py     # ASCII art generator
│   └── config_utils.py            # Configuration utilities
├── agency_issue_finder/           # Issue finder modules
│   ├── issue_finder.py            # Base issue finder module
│   ├── base_connector.py          # Base research connector
│   ├── hhs_finder.py              # HHS-specific issue finder
│   └── agencies/                  # Agency-specific issue finders
├── templates/                     # ASCII art templates
│   ├── hhs_ascii.txt              # HHS ASCII art
│   ├── usda_ascii.txt             # USDA ASCII art
│   ├── aphis_ascii.txt            # APHIS ASCII art
│   └── dod_ascii.txt              # DOD ASCII art
├── config/                        # Configuration files
│   └── agency_data.json           # Agency data model
└── agencies/                      # Agency-specific connectors
    └── hhs_connector.py           # HHS research connector
```

## Supported Agencies

The system supports agencies organized into four tiers:

### Tier 1 Agencies (Cabinet Departments):
- Department of Health and Human Services (HHS) ✓
- Department of Agriculture (USDA) ✓
- Animal and Plant Health Inspection Service (APHIS) ⚠️
- Department of Defense (DOD) ✓
- Department of Treasury (TREAS) ✓
- Department of Justice (DOJ) ✓
- Department of Homeland Security (DHS) ✓
- Department of State (DOS) ✓
- Department of Energy (DOE) ✓

### Tier 2 Agencies (Additional Cabinet Departments):
- Department of Commerce (DOC) ✓
- Department of Labor (DOL) ✓
- Department of Housing and Urban Development (HUD) ✓
- Department of Transportation (DOT) ✓
- Department of Education (ED) ✓
- Department of Veterans Affairs (VA) ✓
- Department of the Interior (DOI) ✓

### Tier 3 Agencies (Major Independent Agencies):
- Environmental Protection Agency (EPA) ✓
- Small Business Administration (SBA) ✓
- Social Security Administration (SSA) ✓
- National Aeronautics and Space Administration (NASA) ✓
- National Science Foundation (NSF) ✓
- U.S. Agency for International Development (USAID) ✓
- Federal Communications Commission (FCC) ✓
- Office of Personnel Management (OPM) ✓

### Tier 4 Agencies (Selected Independent Agencies):
- Consumer Financial Protection Bureau (CFPB) ✓
- Commodity Futures Trading Commission (CFTC) ✓
- Consumer Product Safety Commission (CPSC) ✓
- Equal Employment Opportunity Commission (EEOC) ✓
- Federal Trade Commission (FTC) ✓
- General Services Administration (GSA) ✓
- National Archives and Records Administration (NARA) ✓
- Nuclear Regulatory Commission (NRC) ✓
- Pension Benefit Guaranty Corporation (PBGC) ✓
- Securities and Exchange Commission (SEC) ✓

✓ = Fully implemented with issue finder, research connector, and ASCII art

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/organization/codify.git
   cd codify/SYSTEM-COMPONENTS/HMS-DEV/agency-interface
   ```

2. Ensure scripts are executable:
   ```bash
   chmod +x agency-cli.sh launch_agency_codex.sh
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt  # (if requirements file exists)
   ```

## Usage

### Basic Usage

Launch the agency interface:

```bash
./launch_agency_codex.sh
```

This will present a menu of available agencies. Select an agency and follow the prompts to start Codex CLI with the appropriate context.

### Direct Agency Selection

To launch directly with a specific agency:

```bash
./launch_agency_codex.sh --agency=HHS
```

### Topic Selection

To focus on a specific topic within an agency:

```bash
./launch_agency_codex.sh --agency=USDA --topic=bird-flu
```

### Demo Mode

Run in demo mode without executing actual Codex commands:

```bash
./launch_agency_codex.sh --demo
```

## Implementation Scripts

The following scripts are available for implementing and managing agencies:

- **start_tier_1.sh**: Script to implement Tier 1 agencies
- **start_tier_2.sh**: Script to implement Tier 2 agencies
- **start_tier_3.sh**: Script to implement Tier 3 agencies
- **start_tier_4.sh**: Script to implement Tier 4 agencies
- **batch_process_agencies.sh**: Script for batch processing multiple agencies
- **agency_generator.py**: Python script to generate agency components
- **agency_status_fixed.sh**: Script to display implementation status dashboard
- **update_progress.py**: Script to update implementation progress tracker

## Domain Support

The agency interface supports multiple domains including:

- Healthcare (HHS)
- Agriculture (USDA)
- Defense (DOD)
- Finance (TREAS)
- Justice (DOJ)
- Security (DHS)
- Diplomacy (DOS)
- Energy (DOE)
- Commerce (DOC)
- Labor (DOL)
- Housing (HUD)
- Transportation (DOT)
- Education (ED)
- Veterans (VA)
- Interior (DOI)
- Environment (EPA)
- Business (SBA)
- Social (SSA)
- Space (NASA)
- Science (NSF)
- Development (USAID)
- Communications (FCC)
- Personnel (OPM)
- Various Tier 4 domains (Consumer, Securities, etc.)

## Extending the System

### Adding a New Agency

1. Add the agency to `config/agency_data.json`
2. Add appropriate domain templates to `agency_generator.py` if needed
3. Run `python3 agency_generator.py --agency NEW_AGENCY`
4. Update the progress tracker with `python3 update_progress.py`

## Documentation

For more detailed information, see:

- [COMPLETE-AGENCY-ROLLOUT-PLAN.md](../docs/COMPLETE-AGENCY-ROLLOUT-PLAN.md)
- [CODEX-CLI-CUSTOMIZATION-PLAN.md](../CODEX-CLI-CUSTOMIZATION-PLAN.md)

## Contact

For questions or feedback, please contact the HMS-DEV team.