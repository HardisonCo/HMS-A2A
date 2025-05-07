# Agency Integration with MAC Architecture

This README documents the integration of the USTDA and USITC agency agents with the Multi-Agent Collaboration (MAC) architecture in HMS-A2A, including the Win-Win calculation framework.

## Overview

The integration enables government agencies to participate in the Moneyball trade system using a three-layer architecture:
1. **Governance Layer**: Policy definition and regulatory framework
2. **Management Layer**: Program implementation and execution
3. **Interface Layer**: User and system interaction points

## Components

### Agency Agents
- **USTDA Agent**: US Trade & Development Agency agent for trade policy development and implementation
- **USITC Agent**: US International Trade Commission agent for economic analysis and impact assessment

### Win-Win Calculation Framework
- Mathematical framework for ensuring all stakeholders receive positive value
- Provides entity-specific value translation functions for different stakeholder types
- Supports optimization of value distribution to achieve win-win outcomes

### MAC Integration
- `agency_integration.py`: Core integration module for extending MAC with agency functionality
- Support for import certificates, economic impact assessment, and win-win calculations

## File Structure

```
HMS-A2A/
├── mac/
│   ├── agency_integration.py   # Core MAC integration
│   └── ...                     # Other MAC components
├── ustda_agent.py              # USTDA agent implementation
├── usitc_agent.py              # USITC agent implementation
├── win_win_calculation_framework.py  # Mathematical framework
├── trade_base.py               # Base classes for trade system
├── trade_agent.py              # Dynamic trade agent implementation
├── test_agency_integration.py  # Full integration tests
├── test_win_win_framework.py   # Win-Win framework tests
└── simple_agency_integration_test.py  # Basic component tests
```

## Current Status

The integration work has been partly completed:

✅ Successfully implemented the USTDA agent with Import Certificate functionality
✅ Successfully implemented the USITC agent with Economic Analysis capabilities
✅ Successfully implemented the Win-Win calculation framework 
✅ Agency agents are properly importable and functional
✅ Fixed import path issues in integration code

🔄 MAC integration requires additional setup:
  - The MAC architecture depends on external modules like `a2a` that need to be installed
  - The Win-Win calculation framework requires `numpy` and `pandas` packages

## Testing

Simple tests confirm the components are properly implemented and can be imported:

```bash
python3 simple_agency_integration_test.py
```

For full integration testing with the MAC architecture, additional dependencies need to be installed:

1. The `a2a` module for MAC architecture
2. `numpy` and `pandas` for the Win-Win calculation framework
3. Other MAC dependencies as specified in the project

## Next Steps

1. Install required dependencies for MAC and Win-Win framework
2. Run the full `test_agency_integration.py` test suite
3. Integrate the agency components with deal creation and negotiation workflow
4. Extend economic impact assessments with real-world data
5. Develop visualization tools for Win-Win analysis results

## Implementation Notes

- Agency agents implement the three-layer architecture (Governance, Management, Interface)
- The Win-Win framework translates value across different entity types based on mathematical models
- The MAC integration extends the market network with agency-specific functionality
- Import certificates implement Warren Buffett's balanced trade approach
- Economic models provide data-driven analysis for policy recommendations

## Mathematical Models

The Win-Win calculation framework uses several mathematical models:

1. Entity-specific value translation
2. Time-adjusted value calculation
3. Risk-adjusted value calculation
4. Log STD deviation value
5. Translation matrices between domains
6. Value distribution optimization
7. Gini coefficient for value inequality

See `win_win_calculation_framework.py` for detailed implementation.