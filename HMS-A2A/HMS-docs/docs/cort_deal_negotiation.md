# Chain of Recursive Thoughts for Deal Negotiation

This document explains how to use Chain of Recursive Thoughts (CoRT) for deal negotiations and trade scenarios between specialized agents in the HMS-A2A framework.

## Overview

Chain of Recursive Thoughts enhances deal negotiation and collaborative decision-making by enabling agents to:

1. Generate multiple alternatives for each decision point
2. Evaluate each alternative against specific criteria
3. Compare options from multiple perspectives
4. Select the best solution through recursive self-critique
5. Provide transparent reasoning traces for all decisions

This approach helps specialized agents make better decisions in complex deal negotiations by considering more options and engaging in structured multi-round thinking.

## Latest Improvements

The CoRT Deal Negotiation implementation has been enhanced with:

- **Domain-Specific Instructions**: Support for custom prompt instructions tailored to specific negotiation contexts
- **Improved Pattern Recognition**: Better extraction of approval status and recommendation details
- **Enhanced Error Handling**: Robust recovery from evaluation failures
- **Comprehensive Testing**: Detailed specification tests for deal negotiation scenarios
- **Unified Start Command**: Simple command to launch CoRT-enhanced deal scenarios

## Key Components

### 1. CoRT Deal Evaluator

The `CoRTDealEvaluator` module provides specialized tools for deal evaluations, solution comparisons, and transaction negotiations:

- **Deal Evaluation**: Thoroughly assesses a deal against multiple criteria with recursive thinking
- **Solution Comparison**: Compares and ranks multiple solutions to a problem through recursive analysis
- **Transaction Negotiation**: Recursively improves transaction terms to find win-win arrangements

### 2. CoRT Agent Adapter

The `CoRTAgentAdapter` makes it easy to enhance any specialized agent with deal negotiation capabilities:

- Adds CoRT-enhanced functions for deal evaluation, solution comparison, and negotiation
- Wraps existing agent functions with recursive thinking capabilities
- Provides domain-specific reasoning based on agent expertise

### 3. Deal Framework Integration

The CoRT functionality is fully integrated with the Deals framework:

- Works with Problems, Solutions, Players, and Transactions
- Maintains standards compliance throughout
- Enhances collaborative decision-making while preserving accountability

## Installation and Setup

To use the Chain of Recursive Thoughts for deal negotiation, follow these steps:

1. Make sure you have the required dependencies:
   ```bash
   pip install langchain-google-genai google-generativeai networkx
   ```

2. Set up your API key for Gemini (or other LLM provider):
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```

3. Import the necessary modules:
   ```python
   from src.common.utils.recursive_thought import get_recursive_thought_processor
   from src.agents.specialized.collaboration.cort_deal_negotiator import CoRTDealEvaluator
   from src.agents.specialized.collaboration.cort_agent_adapter import enhance_agent_with_cort
   ```

## Usage Examples

### 1. Basic Deal Evaluation with CoRT

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.specialized.collaboration.cort_deal_negotiator import CoRTDealEvaluator
from src.agents.specialized.collaboration.deals import Deal

# Create a model and LLM generator function
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
def llm_generator(prompt):
    return model.invoke(prompt).content

# Create the CoRT Deal Evaluator
evaluator = CoRTDealEvaluator(
    llm_generator=llm_generator,
    max_rounds=3,
    generate_alternatives=3,
    dynamic_rounds=True  # Automatically determines the optimal number of thinking rounds
)

# Create or load your deal object
deal = Deal(
    name="Healthcare Data Exchange Partnership",
    description="A collaboration between healthcare providers and tech companies",
    participants=["hospital", "tech_company", "compliance_advisor"]
)

# Define evaluation criteria
criteria = [
    {"name": "Regulatory Compliance", "description": "Does the deal meet all regulatory requirements?"},
    {"name": "Data Security", "description": "How well does the deal address data security concerns?"},
    {"name": "Business Viability", "description": "Is the deal commercially viable for all parties?"}
]

# Evaluate the deal with recursive thinking
result = evaluator.evaluate_deal(
    deal=deal,
    evaluator_role="Healthcare Compliance Officer",
    evaluation_criteria=criteria,
    prompt_instructions="Focus on HIPAA compliance and patient data protection requirements"  # Domain-specific guidance
)

# Access the results
print(f"Deal evaluation completed after {result['rounds_completed']} rounds of thinking")
print(f"Approval status: {result['approval_status']}")  # New feature: explicit approval status
print("\nFinal evaluation:")
print(result["evaluation"])

# Access the thinking trace if needed
thinking_trace = result["thinking_trace"]
for round_data in thinking_trace:
    print(f"Round {round_data.get('round', 0)}: {len(round_data.get('alternatives', []))} alternatives considered")
```

### Using the Unified Start Command for Deal Negotiations

```bash
# Start the system with CoRT enabled for better deal negotiations
./start.sh --cort

# Run the deal demo
./examples/cort_deal_demo.py
```

### 2. Comparing Multiple Solutions with CoRT

```python
from src.agents.specialized.collaboration.deals import Problem, Solution

# Create a problem and multiple solutions
problem = Problem(
    name="Secure Healthcare Data Exchange",
    description="Design a secure system for exchanging sensitive healthcare data",
    success_criteria=["Meets HIPAA requirements", "Supports real-time data exchange"],
    constraints=["Cannot store patient identifiable information in unencrypted format"]
)

cloud_solution = Solution(
    name="Cloud-Based Platform",
    description="A fully managed cloud platform using FHIR standards and encryption",
    approach="Build a cloud-native platform with comprehensive access controls"
)

hybrid_solution = Solution(
    name="Hybrid On-Premise/Cloud System",
    description="A hybrid system that keeps sensitive data on-premise with cloud interfaces",
    approach="Develop on-premise data hubs connected to a cloud orchestration layer"
)

# Define comparison criteria
criteria = [
    {"name": "Security", "description": "How effectively does the solution protect sensitive data?"},
    {"name": "Integration", "description": "How well does the solution integrate with existing systems?"},
    {"name": "Cost-Efficiency", "description": "Is the solution cost-effective in both short and long-term?"}
]

# Compare solutions with recursive thinking
result = evaluator.compare_solutions(
    problem=problem,
    solutions=[cloud_solution, hybrid_solution],
    evaluator_role="Healthcare Technology Architect",
    comparison_criteria=criteria
)

# Access the results
print(f"Solution comparison completed after {result['rounds_completed']} rounds of thinking")
print("\nSolution ranking:")
for i, solution_id in enumerate(result["solution_ranking"]):
    for solution in [cloud_solution, hybrid_solution]:
        if solution.id == solution_id:
            print(f"#{i+1}: {solution.name}")
            break

print("\nFull comparison:")
print(result["comparison"])
```

### 3. Negotiating Transaction Terms with CoRT

```python
from src.agents.specialized.collaboration.deals import Player, Transaction

# Create players and a transaction
hospital = Player(
    agent_id="hospital",
    name="General Hospital",
    role="healthcare_provider"
)

tech_company = Player(
    agent_id="techcorp",
    name="TechCorp Solutions",
    role="tech_company"
)

license_transaction = Transaction(
    name="Technology Licensing Agreement",
    transaction_type="licensing",
    amount=250000.00,
    from_player=hospital.id,
    to_player=tech_company.id,
    currency="USD",
    description="Annual licensing fee for the data exchange platform",
    terms=["Annual renewal", "Includes up to 500TB of data transfer monthly"]
)

# Define negotiation context
context = {
    "market_conditions": "Competitive market with several alternative technology providers",
    "hospital_budget_constraints": "Annual IT budget capped at $2M with 15% for new initiatives",
    "tech_company_costs": "Development and maintenance costs estimated at $150K annually",
    "relationship_goal": "Establish long-term partnership with potential for expanded services"
}

# Negotiate the transaction with recursive thinking
result = evaluator.negotiate_transaction(
    transaction=license_transaction,
    from_player=hospital,
    to_player=tech_company,
    negotiator_role="Healthcare Business Advisor",
    negotiation_context=context
)

# Access the results
print(f"Transaction negotiation completed after {result['rounds_completed']} rounds of thinking")
print("\nRecommended adjustments:")
for recommendation in result["recommendations"]:
    print(f"- {recommendation}")

print("\nFull negotiation analysis:")
print(result["negotiation"])
```

### 4. Enhancing an Existing Agent with CoRT

```python
from src.agents.specialized.financial.tools import FinancialAdvisorTools
from src.agents.specialized.collaboration.cort_agent_adapter import enhance_agent_with_cort

# Create your specialized agent
financial_agent = FinancialAdvisorTools()

# Enhance the agent with CoRT capabilities
enhanced_functions = enhance_agent_with_cort(
    agent=financial_agent,
    domain="finance",
    role="Financial Advisor",
    expertise=["investment", "risk assessment", "financial planning"],
    max_rounds=3,
    generate_alternatives=3
)

# Add enhanced functions to the agent
for name, function in enhanced_functions.items():
    setattr(financial_agent, name, function)

# Now use the CoRT-enhanced functions
deal = Deal(name="Investment Partnership")
evaluation = await financial_agent.evaluate_deal_with_cort(deal)

# CoRT enhanced version of existing methods
result = await financial_agent.cort_negotiate_contract(
    client="Example Corp",
    terms=["Term 1", "Term 2"]
)
```

### 5. Using CoRT Deal Tool in Collaborative Scenarios

The `CoRTDealTool` can be registered as an MCP tool, making it available to any agent in the system:

```python
from src.agents.specialized.collaboration.cort_deal_negotiator import register_cort_deal_tools

# Register the CoRT deal tools with the LLM generator
registered_tools = register_cort_deal_tools(llm_generator)
print(f"Registered CoRT deal tools: {registered_tools}")

# Use the tool through MCP
from src.agents.specialized.collaboration.tool_registry import MCPToolRegistry

registry = MCPToolRegistry()
cort_tool = registry.get_tool("cort_deal_evaluation")

# Execute the tool
result = await cort_tool.execute({
    "operation": "compare_solutions",
    "problem": problem.to_dict(),
    "solutions": [solution1.to_dict(), solution2.to_dict()],
    "evaluator_role": "Deal Analyst"
})
```

## Testing

The Chain of Recursive Thoughts implementation for deal negotiation includes comprehensive tests:

### Basic Tests

```bash
# Run all CoRT deal tests
python -m unittest tests/test_cort_deal_negotiation.py

# Run specific test case
python -m unittest tests.test_cort_deal_negotiation.TestCoRTDealEvaluator
```

### Full Cycle Tests

```bash
# Test complete negotiation workflow
python -m unittest tests.test_cort_full_cycle.TestCoRTDealEvaluation
```

### Specification Tests

```bash
# Verify implementation meets design specifications
python -m unittest tests.test_cort_specs
```

### All Tests with Unified Script

```bash
# Run all tests and launch with CoRT enabled
./start_cort_demo.sh
```

### Key Specifications Tested

1. **Deal Analysis**: Thorough assessment of deal terms and implications
2. **Approval Status Detection**: Clear identification of approval recommendations
3. **Fallback Mechanisms**: Graceful handling of evaluation failures
4. **Prompt Instructions**: Domain-specific guidance for specialized evaluations
5. **Standards Compliance**: Validation against industry standards
6. **Cross-Domain Analysis**: Multi-perspective evaluation from different domains

## Advanced Configuration

### LLM Model Configuration

You can configure the LLM model used by the CoRT processor:

```python
from langchain_google_genai import ChatGoogleGenerativeAI

# Create a model with specific configuration
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # Use a more powerful model for complex negotiations
    temperature=0.2,  # Lower temperature for more consistent results
    top_p=0.95,
    top_k=40,
    max_output_tokens=2048
)

def llm_generator(prompt):
    return model.invoke(prompt).content

# Create the CoRT processor with this generator
evaluator = CoRTDealEvaluator(llm_generator=llm_generator)
```

### Customizing Recursive Thinking

You can customize how the recursive thinking process works:

```python
# Create a CoRT processor with specific thinking parameters
evaluator = CoRTDealEvaluator(
    llm_generator=llm_generator,
    max_rounds=5,                # More rounds for complex decisions
    generate_alternatives=4,     # Generate more alternatives per round
    dynamic_rounds=True          # Automatically determine optimal rounds
)
```

### Adding Domain-Specific Evaluation Criteria

You can create domain-specific criteria sets:

```python
# Healthcare domain criteria
healthcare_criteria = [
    {"name": "Patient Privacy", "description": "Does the deal protect patient privacy in accordance with HIPAA?"},
    {"name": "Clinical Workflow", "description": "Does the solution integrate with clinical workflows?"},
    {"name": "Data Integrity", "description": "Are there safeguards for ensuring data integrity?"},
    {"name": "Regulatory Compliance", "description": "Does it comply with healthcare regulations?"}
]

# Financial domain criteria
financial_criteria = [
    {"name": "Risk Assessment", "description": "Has the financial risk been properly assessed?"},
    {"name": "Return on Investment", "description": "What is the expected ROI?"},
    {"name": "Compliance", "description": "Does it comply with financial regulations?"},
    {"name": "Transparency", "description": "Is the deal structure transparent to all parties?"}
]
```

## Benefits for Deal Negotiations

1. **More Comprehensive Analysis**: Considers multiple perspectives and alternatives for each decision
2. **Better Decision Quality**: Recursive self-critique leads to more refined solutions
3. **Alignment with Expertise**: Domain-specific reasoning based on agent specialty
4. **Transparent Reasoning**: Full thinking traces show how decisions were reached
5. **Adaptive Depth**: Dynamic thinking rounds based on problem complexity

## Performance Considerations

- **Token Usage**: CoRT increases token usage due to multiple thinking rounds
- **Latency**: Expect increased processing time, especially with many thinking rounds
- **Memory Usage**: Thinking traces can be large for complex scenarios

To optimize performance:

```python
# For simpler scenarios, use fewer rounds
simple_evaluator = CoRTDealEvaluator(
    llm_generator=llm_generator,
    max_rounds=2,
    generate_alternatives=2,
    dynamic_rounds=False  # Use fixed rounds for predictable performance
)

# For detailed scenarios, use more rounds
detailed_evaluator = CoRTDealEvaluator(
    llm_generator=llm_generator,
    max_rounds=4,
    generate_alternatives=3,
    dynamic_rounds=True  # Adapt to complexity
)
```

## Best Practices

1. **Start with Dynamic Rounds**: Let the system determine optimal thinking depth initially
2. **Use Domain-Specific Criteria**: Create criteria tailored to your agent's domain
3. **Store Thinking Traces**: Retain reasoning for auditability and analysis
4. **Match Rounds to Complexity**: Use more rounds for critical or complex decisions
5. **Provide Rich Context**: Include relevant information in negotiation context

## Additional Resources

- [Chain of Recursive Thoughts Repository](https://github.com/PhialsBasement/Chain-of-Recursive-Thoughts) - Original reference implementation
- [HMS-A2A Core Documentation](docs/agent.md) - Main A2A framework documentation
- [Example Code](examples/cort_deal_demo.py) - Complete demonstration script

## Troubleshooting

### Common Issues

1. **LLM Generation Failures**: 
   - Check API key is set correctly
   - Verify model name is valid
   - Check quota limits with your LLM provider

2. **JSON Parsing Errors**:
   - CoRT aims to handle unstructured responses gracefully
   - Adjust alternatives_prompt to encourage valid JSON format
   - Check LLM's formatting capabilities

3. **Poor Quality Results**:
   - Use more specific evaluation criteria
   - Increase number of rounds and alternatives
   - Use a more capable LLM model