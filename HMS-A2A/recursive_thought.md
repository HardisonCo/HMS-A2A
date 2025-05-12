# Chain of Recursive Thoughts (CoRT)

This document provides an overview of the Chain of Recursive Thoughts (CoRT) core implementation in the HMS-A2A framework.

## Overview

Chain of Recursive Thoughts (CoRT) is a technique that enhances AI decision-making by enabling agents to:

1. Generate multiple alternatives for each decision
2. Critically evaluate each alternative
3. Select the best option through recursive self-critique
4. Maintain a transparent thinking trace

The implementation is based on the approach described in the [Chain of Recursive Thoughts](https://github.com/PhialsBasement/Chain-of-Recursive-Thoughts) repository.

## Latest Updates

The CoRT implementation has been enhanced with:

- **Improved Pattern Recognition**: Better extraction of alternatives and evaluation results from unstructured text
- **Tool-Aware Processing**: Integration with agent tools for more informed decisions
- **Domain-Specific Instructions**: Support for domain-specific prompt instructions
- **Comprehensive Error Handling**: Robust recovery from various failure modes
- **Standardized Testing**: Detailed specification tests for every core functionality

## Core Components

### CoRTProcessor

The `CoRTProcessor` class in `src/common/utils/recursive_thought.py` implements the core recursive thinking pattern:

- **Alternative Generation**: Creates multiple approaches to solve a problem
- **Alternative Evaluation**: Critically assesses each alternative against criteria
- **Alternative Selection**: Chooses the best alternative through recursive improvement
- **Dynamic Thinking Depth**: Automatically determines the optimal number of thinking rounds based on problem complexity

## Key Features

### 1. Robust JSON Parsing

The processor handles various LLM response formats:

- Attempts to parse structured JSON responses first
- Falls back to text extraction with regex patterns if JSON parsing fails
- Uses multiple extraction methods to handle different response formats

### 2. Dynamic Thinking Rounds

CoRT can automatically determine the optimal number of thinking rounds:

```python
processor = CoRTProcessor(
    llm_generator=llm_fn,
    max_rounds=5,       # Upper limit on rounds
    dynamic_rounds=True # Enable dynamic round determination
)
```

### 3. Error Handling and Fallbacks

The implementation includes comprehensive error handling:

- Graceful recovery from LLM generation failures
- Alternative extraction fallbacks when structured parsing fails
- Default to previous best response when evaluation fails

### 4. Tool Integration

CoRT can be integrated with external tools through the `process_with_tools` method:

```python
result = processor.process_with_tools(
    query="What is the GDP of France in 2023?",
    tools=[calculator_tool, search_tool],
    tool_executor=execute_tool
)
```

## Usage Examples

### Basic Usage

```python
from src.common.utils.recursive_thought import get_recursive_thought_processor
from langchain_google_genai import ChatGoogleGenerativeAI

# Create a model and LLM generator function
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
def llm_generator(prompt):
    return model.invoke(prompt).content

# Create the CoRT processor
processor = get_recursive_thought_processor(
    llm_fn=llm_generator,
    max_rounds=3,
    generate_alternatives=3,
    dynamic_rounds=True
)

# Process a query
result = processor.process(
    query="What are the potential impacts of climate change on agricultural production?",
    initial_response=None,  # Optional starting point
    task_context={"domain": "environmental_science"},  # Optional context
    prompt_instructions="Focus on evidence-based findings and scientific consensus"  # Domain-specific guidance
)

# Access the results
print(f"Processing completed after {result['rounds_completed']} rounds of thinking")
print("\nFinal response:")
print(result["final_response"])

# Access the thinking trace if needed
thinking_trace = result["thinking_trace"]
for round_data in thinking_trace:
    print(f"Round {round_data.get('round', 0)}: {len(round_data.get('alternatives', []))} alternatives considered")
```

### Using the Unified Start Command

The simplest way to run the entire HMS-A2A system with CoRT enabled:

```bash
# Start all services with CoRT enabled
./start.sh --cort

# Run the demo script
./examples/cort_basic_demo.py
```

### Using CoRT with Tools

```python
from src.common.utils.recursive_thought import get_recursive_thought_processor

# Define tools and tool executor
calculator_tool = {
    "name": "calculator",
    "description": "Performs mathematical calculations"
}

weather_tool = {
    "name": "weather",
    "description": "Retrieves weather information"
}

def execute_tool(query, tool):
    """Execute a tool call."""
    if tool["name"] == "calculator":
        # Simple calculator implementation
        try:
            return str(eval(query))
        except:
            return "Error in calculation"
    elif tool["name"] == "weather":
        return f"Weather data for {query}: 72°F, Sunny"
    return "Unknown tool"

# Create the CoRT processor
processor = get_recursive_thought_processor(llm_fn=llm_generator)

# Process with tools
result = processor.process_with_tools(
    query="What will the temperature be tomorrow, and is it 5 degrees warmer than today?",
    tools=[calculator_tool, weather_tool],
    tool_executor=execute_tool
)

# Access the results including tool usage
for tool_use in result["tool_usage"]:
    print(f"Used tool: {tool_use['tool']}")
    print(f"Input: {tool_use['input']}")
    print(f"Output: {tool_use['output']}")
```

### Advanced Configuration

```python
# Create a CoRT processor with advanced settings
processor = CoRTProcessor(
    llm_generator=llm_generator,
    max_rounds=5,            # More rounds for complex decisions
    generate_alternatives=4, # Generate more alternatives per round
    dynamic_rounds=True,     # Automatically determine optimal rounds
    detailed_logging=True    # Enable detailed logging
)
```

## Specialized Implementations

The core CoRT processor has been extended for specific use cases:

- **Deal Negotiation**: For evaluating deals, comparing solutions, and negotiating transactions (see [cort_deal_negotiation.md](cort_deal_negotiation.md))
- **Agent Enhancement**: For enhancing any specialized agent with recursive thinking capabilities

## Performance Considerations

- **Token Usage**: CoRT increases token usage due to multiple thinking rounds
- **Latency**: Expect increased processing time, especially with many thinking rounds
- **Memory Usage**: Thinking traces can be large for complex scenarios

## Best Practices

1. **Start with Dynamic Rounds**: Let the system determine optimal thinking depth initially
2. **Store Thinking Traces**: Retain reasoning for auditability and analysis
3. **Match Rounds to Complexity**: Use more rounds for critical decisions, fewer for simple ones
4. **Provide Rich Context**: Include relevant information in the task context

## Testing

The CoRT implementation includes comprehensive tests:

### Core Unit Tests

```bash
# Run core CoRT unit tests
python -m unittest tests.test_recursive_thought
```

### Specification Tests

```bash
# Run detailed specification tests
python -m unittest tests.test_cort_specs
```

### Full Cycle Tests

```bash
# Run integration tests (requires dependencies)
python -m unittest tests.test_cort_full_cycle
```

### Complete Test Suite

The start script includes a complete testing workflow:

```bash
# Run all tests and start the system with CoRT enabled
./start_cort_demo.sh
```

### Key Specifications Tested

1. **Prompt Instructions Handling**: Properly uses domain-specific instructions
2. **Fallback Mechanisms**: Uses simpler approaches when main approach fails
3. **JSON Extraction Failures**: Handles various text formats gracefully
4. **Dynamic Round Determination**: Intelligently selects optimal thinking depth
5. **Thinking Trace Maintenance**: Preserves complete reasoning history
6. **Error Handling**: Recovers from failures in any component
7. **Pattern Recognition**: Extracts best options from unstructured text
8. **Tool Integration**: Works seamlessly with external tools
9. **Helper Functions**: Properly configures processors with correct parameters
10. **Alternative Extraction**: Handles various formats of alternative answers

## Additional Resources

- [Chain of Recursive Thoughts Repository](https://github.com/PhialsBasement/Chain-of-Recursive-Thoughts) - Original reference implementation
- [Deal Negotiation with CoRT](cort_deal_negotiation.md) - Specialized implementation for deal negotiations
- [Example Code](../examples/cort_deal_demo.py) - Complete demonstration script