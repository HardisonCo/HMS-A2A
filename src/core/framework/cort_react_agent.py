"""
CoRT-enhanced React Agent using A2A Tools and Specialized Agents

This module implements a React-style agent enhanced with Chain of Recursive Thoughts
capabilities that can use A2A protocol-compatible agents and standards-compliant 
specialized agents as tools.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the graph package
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from src.core.framework.a2a_tools import CurrencyTool, MathTool
from src.core.framework.a2a_mcp_tool import A2AMCPTool
from src.core.framework.specialized_agent_tool import SpecializedAgentTool
from common.utils.recursive_thought import CoRTProcessor, get_recursive_thought_processor

# Load environment variables
load_dotenv()

# Initialize memory for the agent
memory = MemorySaver()

class CoRTReactAgent:
    """
    CoRT-enhanced ReAct agent that uses A2A protocol-compatible agents 
    and specialized agents as tools with Chain of Recursive Thoughts capabilities.
    """
    
    SYSTEM_INSTRUCTION = """
    You are an intelligent assistant that can help with various tasks by using specialized tools.
    You can think recursively to improve your responses through multiple rounds of self-critique.
    
    You have access to these tools:
    1. currency_tool: Use this when the user asks about currency conversions or exchange rates.
    2. math_tool: Use this when the user asks about mathematical calculations, specifically addition and multiplication.
    3. a2a_generic_agent: Use this for general questions requiring external knowledge or complex reasoning.
    4. specialized_agent: Use this for industry-specific questions that require compliance with standards.
       
       When using the specialized_agent tool, your query should be in this format:
       "Domain: specific question"
       
       Example:
       "Agriculture: What are the best organic pest management practices for tomatoes?"
    
    For all other types of questions, answer directly to the best of your knowledge without using tools.
    
    Always use the most appropriate tool for the task, and interpret the results for the user in a helpful way.
    After generating an initial response, you will recursively critique and improve your answer through
    multiple rounds of reflection until you arrive at the best possible response.
    """
    
    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        cort_max_rounds: int = 3,
        cort_alternatives: int = 3,
        cort_enabled_by_default: bool = True
    ):
        """Initialize the CoRT-enhanced React agent.
        
        Args:
            model_name: The LLM model to use
            cort_max_rounds: Maximum CoRT thinking rounds
            cort_alternatives: Number of alternatives to generate per round
            cort_enabled_by_default: Whether CoRT is enabled by default
        """
        # Check for API key
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        # Initialize the model
        self.model = ChatGoogleGenerativeAI(model=model_name)
        self.model_name = model_name
        
        # Initialize the tools
        self.tools = [
            CurrencyTool(),
            MathTool(),
            A2AMCPTool(),
            SpecializedAgentTool()
        ]
        
        # Create the agent graph
        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION
        )
        
        # Configure CoRT
        self.cort_max_rounds = cort_max_rounds
        self.cort_alternatives = cort_alternatives
        self.cort_enabled_by_default = cort_enabled_by_default
        self._cort_processor = None
    
    @property
    def cort_processor(self) -> CoRTProcessor:
        """Get the CoRT processor, creating it if needed."""
        if self._cort_processor is None:
            # Create a function that handles LLM generation
            def llm_generator(prompt: str) -> str:
                """Generate a response using the agent's LLM."""
                try:
                    response = self.model.invoke(prompt).content
                    return response
                except Exception as e:
                    print(f"Error in LLM generation: {e}")
                    return f"Error generating response: {str(e)}"
            
            # Create the CoRT processor
            self._cort_processor = get_recursive_thought_processor(
                llm_fn=llm_generator,
                max_rounds=self.cort_max_rounds,
                generate_alternatives=self.cort_alternatives
            )
        
        return self._cort_processor
    
    def invoke(
        self,
        query: str,
        session_id: str = "default",
        use_cort: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Invoke the agent with a query, optionally using CoRT.
        
        Args:
            query: The query to process
            session_id: Session identifier
            use_cort: Whether to use CoRT (defaults to self.cort_enabled_by_default)
            
        Returns:
            Dictionary with the result
        """
        # Determine if CoRT should be used
        if use_cort is None:
            use_cort = self.cort_enabled_by_default
        
        # Configure the agent
        config = {"configurable": {"thread_id": session_id}}
        
        # First, invoke the agent graph to get an initial response
        response = self.graph.invoke({"messages": [("human", query)]}, config)
        
        # If CoRT is disabled, return the direct response
        if not use_cort:
            return {
                "input": query,
                "output": response["messages"][-1].content,
                "full_response": response,
                "cort_enabled": False
            }
        
        # Extract the initial response
        initial_response = response["messages"][-1].content
        
        # Process with CoRT
        cort_result = self.cort_processor.process(
            query=query,
            initial_response=initial_response,
            task_context={
                "session_id": session_id,
                "available_tools": [tool.name for tool in self.tools]
            }
        )
        
        # Return the enhanced result
        return {
            "input": query,
            "output": cort_result["final_response"],
            "initial_output": initial_response,
            "cort_enabled": True,
            "thinking_trace": cort_result["thinking_trace"],
            "rounds_completed": cort_result["rounds_completed"],
            "full_response": response
        }
    
    def invoke_with_tools(
        self,
        query: str,
        session_id: str = "default",
        use_cort: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Invoke the agent with a query using tools and CoRT.
        
        Args:
            query: The query to process
            session_id: Session identifier
            use_cort: Whether to use CoRT (defaults to self.cort_enabled_by_default)
            
        Returns:
            Dictionary with the result including tool usage
        """
        # Determine if CoRT should be used
        if use_cort is None:
            use_cort = self.cort_enabled_by_default
        
        # Configure the agent
        config = {"configurable": {"thread_id": session_id}}
        
        # First, invoke the agent graph to get an initial response with tool usage
        response = self.graph.invoke({"messages": [("human", query)]}, config)
        
        # Extract the initial response
        initial_response = response["messages"][-1].content
        
        # Extract tool usage
        tool_usage = []
        for msg in response["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_usage.append({
                        "tool": tool_call.name,
                        "input": tool_call.args,
                        "output": None  # Will be filled in later
                    })
            elif hasattr(msg, "name") and msg.name:
                # This is a tool response
                if tool_usage and tool_usage[-1]["output"] is None:
                    tool_usage[-1]["output"] = msg.content
        
        # If CoRT is disabled, return the direct response
        if not use_cort:
            return {
                "input": query,
                "output": initial_response,
                "full_response": response,
                "tool_usage": tool_usage,
                "cort_enabled": False
            }
        
        # Create a tool executor for CoRT
        def tool_executor(tool_name: str, tool_input: str) -> str:
            """Execute a tool call."""
            # Find the tool
            for tool in self.tools:
                if tool.name == tool_name:
                    try:
                        result = tool.invoke(tool_input)
                        return str(result)
                    except Exception as e:
                        return f"Error executing tool {tool_name}: {str(e)}"
            
            return f"Tool {tool_name} not found"
        
        # Process with CoRT and tools
        cort_result = self.cort_processor.process_with_tools(
            query=query,
            tools=self.tools,
            tool_executor=tool_executor,
            initial_response=initial_response,
            task_context={
                "session_id": session_id,
                "available_tools": [tool.name for tool in self.tools]
            }
        )
        
        # Return the enhanced result
        return {
            "input": query,
            "output": cort_result["final_response"],
            "initial_output": initial_response,
            "cort_enabled": True,
            "thinking_trace": cort_result["thinking_trace"],
            "rounds_completed": cort_result["rounds_completed"],
            "tool_usage": tool_usage,
            "full_response": response
        }
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get the chat history for a session."""
        config = {"configurable": {"thread_id": session_id}}
        current_state = self.graph.get_state(config)
        
        if current_state and "messages" in current_state.values:
            messages = current_state.values["messages"]
            return [
                {
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content
                }
                for msg in messages
            ]
        
        return []


# Simple test function
def test_cort_agent():
    """Run some test queries against the CoRT-enhanced agent."""
    agent = CoRTReactAgent()
    
    # Test with CoRT
    print("Test 1: With CoRT")
    result = agent.invoke("What is the exchange rate from USD to EUR?", use_cort=True)
    print(f"Input: {result['input']}")
    print(f"Initial Output: {result['initial_output']}")
    print(f"Final Output: {result['output']}")
    print(f"Rounds Completed: {result['rounds_completed']}")
    print("-" * 50)
    
    # Test without CoRT
    print("Test 2: Without CoRT")
    result = agent.invoke("Calculate 25 + 17", use_cort=False)
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
    print("-" * 50)
    
    # Test tool usage with CoRT
    print("Test 3: Tool Usage with CoRT")
    result = agent.invoke_with_tools(
        "If I have 100 USD, how many Euros would that be, and if I split it equally between 5 people, how much would each person get?",
        use_cort=True
    )
    print(f"Input: {result['input']}")
    print(f"Initial Output: {result['initial_output']}")
    print(f"Final Output: {result['output']}")
    print(f"Tool Usage: {len(result['tool_usage'])} tools used")
    print(f"Rounds Completed: {result['rounds_completed']}")
    print("-" * 50)

if __name__ == "__main__":
    test_cort_agent()