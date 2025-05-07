from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage
import os
import asyncio
import sys
from typing import Any, Dict, AsyncIterable, List, Optional
from pydantic import BaseModel, Field

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from graph.a2a_tools import CurrencyTool, MathTool
from graph.a2a_mcp_tool import A2AMCPTool
from common.server.a2a_mcp_server import A2AMCPServer

memory = MemorySaver()

class A2ECombinedAgent:
    """An agent that combines Math, Currency, and generic A2A capabilities."""

    SYSTEM_INSTRUCTION = (
        "You are a helpful assistant that can perform math operations, currency conversions, "
        "and connect to other A2A-compatible agents. "
        "Use the provided tools to help users with calculations, currency exchange rates, "
        "and other tasks that can be delegated to specialized agents. "
        "Always select the most appropriate tool for the task at hand."
    )
     
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]
    
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.tools = []
        self.graph = None
        self.mcp_server = None
        self._initialize_tools()
        
    def _initialize_tools(self):
        """Initialize the agent with MCP tools and A2A tools."""
        asyncio.run(self._async_initialize_tools())
        
    async def _async_initialize_tools(self):
        """Asynchronously load MCP tools and initialize the agent."""
        # Get the root directory path
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # Set up the math server parameters
        math_server_params = StdioServerParameters(
            command="python",
            args=[os.path.join(root_dir, "test_mcp/server/math_server.py")],
        )
        
        # Set up the currency server parameters
        currency_server_params = StdioServerParameters(
            command="python",
            args=[os.path.join(root_dir, "test_mcp/server/currency_server.py")],
        )
        
        # Load tools from math server
        math_tools = []
        try:
            print("Connecting to Math MCP server...")
            async with stdio_client(math_server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    # Get tools
                    math_tools = await load_mcp_tools(session)
                    print(f"Loaded {len(math_tools)} math tools")
        except Exception as e:
            print(f"Error loading math tools: {e}")
        
        # Load tools from currency server
        currency_tools = []
        try:
            print("Connecting to Currency MCP server...")
            async with stdio_client(currency_server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    # Get tools
                    currency_tools = await load_mcp_tools(session)
                    print(f"Loaded {len(currency_tools)} currency tools")
        except Exception as e:
            print(f"Error loading currency tools: {e}")
        
        # Create direct A2A tools
        a2a_tools = [
            CurrencyTool(),
            MathTool(),
            A2AMCPTool()
        ]
        
        # Start A2A MCP server in background
        try:
            # Start the A2A MCP server in a separate thread/process
            # This is handled separately to avoid blocking
            print("Setting up A2A MCP server...")
            # Note: The actual server will be started in a separate process by the start_servers.py script
        except Exception as e:
            print(f"Error setting up A2A MCP server: {e}")
        
        # Combine all tools
        self.tools = math_tools + currency_tools + a2a_tools
        
        if not self.tools:
            print("WARNING: No tools were loaded. The agent may not function correctly.")
        else:
            print(f"Total tools loaded: {len(self.tools)}")
            for tool in self.tools:
                print(f"  - {tool.name}: {tool.description}")
        
        # Create the agent graph
        self.graph = create_react_agent(
            self.model, 
            tools=self.tools, 
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION
        )

    def invoke(self, query, sessionId) -> Dict[str, Any]:
        """Invoke the agent with a query."""
        if not self.graph:
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": "Agent initialization failed. Please try again later."
            }
            
        config = {"configurable": {"thread_id": sessionId}}
        result = self.graph.invoke({"messages": [("user", query)]}, config)
        
        # Process the result
        return {
            "is_task_complete": True,
            "require_user_input": False,
            "content": result["messages"][-1].content
        }

    async def stream(self, query, sessionId) -> AsyncIterable[Dict[str, Any]]:
        """Stream the agent's response."""
        if not self.graph:
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": "Agent initialization failed. Please try again later."
            }
            return
            
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": sessionId}}

        for item in self.graph.stream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Processing your request...",
                }
            elif isinstance(message, ToolMessage):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Computing results...",
                }
        
        # Send final response
        result = self.graph.get_state(config)
        final_message = result.values["messages"][-1]
        
        yield {
            "is_task_complete": True,
            "require_user_input": False,
            "content": final_message.content
        }