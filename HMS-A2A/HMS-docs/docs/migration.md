# Migration from HMS-SME to HMS-A2A/specialized_agents

This document describes the migration of functionality from the HMS-SME project to the HMS-A2A/specialized_agents framework.

## Overview

The migration includes the following components:

1. **Deal Framework**: A system for structured collaboration between specialized agents
2. **Standards Validation**: Mechanisms to validate agent actions against domain-specific standards
3. **MCP Tools**: Domain-specific tools following the Model Context Protocol pattern

## Component Details

### Deal Framework

The Deal framework provides a structured approach to agent collaboration with the following components:

- **Deal**: The central collaboration entity containing problems, solutions, players, and transactions
- **Problem**: A well-defined challenge that requires a solution
- **Solution**: A proposed approach to solving a problem
- **Player**: An agent or human participating in the deal
- **Transaction**: An exchange of value between players

The framework uses a graph-based approach to represent relationships between these components, implemented using NetworkX.

Key files:
- `/specialized_agents/collaboration/deals.py`: Core implementation of Deal framework
- `/specialized_agents/collaboration/deal_tools.py`: MCP tools for working with deals

### Standards Validation

The standards validation framework ensures that agent actions comply with domain-specific standards:

- **StandardsValidator**: Validates actions against standards rules
- **StandardsRegistry**: Maintains a registry of available standards
- **Validation Rules**: Domain-specific rules for validating compliance

Key files:
- `/specialized_agents/standards_validation.py`: Standards validation framework
- `/specialized_agents/data/std.json`: Standards definitions database

### MCP Tools

MCP (Model Context Protocol) tools provide domain-specific functionality:

- **Healthcare Tools**: HIPAA-compliant tools for healthcare data
- **Agriculture Tools**: Tools for agricultural standards compliance
- **Deal Tools**: Tools for creating and managing deals

Key files:
- `/specialized_agents/healthcare/tools.py`: Healthcare MCP tools
- `/specialized_agents/agriculture/tools.py`: Agriculture MCP tools
- `/specialized_agents/mcp_registry.py`: Registry for MCP tools

## Usage

### Creating Deals

```python
from src.agents.specialized.collaboration import Deal, Player, Problem

# Create a deal
deal = Deal(name="Healthcare Analysis Project", 
            description="Analyze patient data for treatment optimization",
            domains=["healthcare", "data_science"])

# Add players
data_scientist = Player(name="Data Scientist", role="analyst", capabilities=["data_analysis", "model_building"])
healthcare_specialist = Player(name="Healthcare Specialist", role="domain_expert", capabilities=["medical_knowledge", "patient_care"])
deal.add_player(data_scientist)
deal.add_player(healthcare_specialist)

# Add a problem
problem = Problem(
    name="Treatment Efficacy Analysis",
    description="Determine which treatments are most effective for specific patient profiles",
    constraints=["Must comply with HIPAA", "Must use anonymized data only"],
    success_criteria=["Statistically significant results", "Actionable recommendations"]
)
deal.add_problem(problem)
deal.assign_problem_owner(problem.id, "Healthcare Specialist")
```

### Using MCP Tools

```python
from src.agents.specialized.healthcare.tools import HealthcareTools
from src.agents.specialized.collaboration.deal_tools import DealTools

# Validate PHI handling
result = HealthcareTools.validate_phi_handling(
    operation_type="store",
    data_elements=["patient_name", "address", "treatment_code"],
    purpose="Treatment efficacy analysis",
    access_control={
        "role_based_access": True,
        "authentication": True,
        "access_logs": True,
        "minimum_necessary_review": True
    },
    encryption_used=True
)

# Create a transaction in a deal
updated_deal = DealTools.create_transaction(
    deal_dict=deal.to_dict(),
    transaction_type="data_transfer",
    sender="Data Scientist",
    receiver="Healthcare Specialist",
    resources={"dataset": "anonymized_treatment_data.csv", "format": "CSV"},
    conditions=["Data must remain on secure server", "No re-identification attempts"]
)
```

### Standards Validation

```python
from src.agents.specialized.standards_validation import StandardsValidator

validator = StandardsValidator()

# Validate against HIPAA standard
validator.validate_field(
    field_name="patient_data_handling",
    value="Store patient names and addresses in encrypted database",
    standards=["HIPAA"]
)

# Check for violations
violations = validator.get_violations()
if violations:
    print(f"Found {len(violations)} compliance issues")
    for violation in violations:
        print(f"- {violation['message']} (Severity: {violation['severity']})")
else:
    print("No compliance issues found")
```

## Integration Points

The migrated components integrate with the existing HMS-A2A framework in the following ways:

1. **Specialized Agents**: Domain-specific agents can use the deals framework for collaboration
2. **Standards Compliance**: Agents maintain standards compliance during collaboration
3. **MCP Tools**: Domain-specific tools enhance agent capabilities
4. **Human-in-the-Loop**: Critical operations require human review

## Future Improvements

Potential future enhancements:

1. Additional domain-specific tools and standards
2. Enhanced visualization tools for deals and collaboration
3. Integration with external standards databases
4. Performance optimizations for graph operations
5. Advanced validation rules with machine learning