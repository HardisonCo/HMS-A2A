"""
A2A MCP Server

This module provides an MCP server that interfaces with A2A client functionality.
"""

import os
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union

from mcp import Server, StdioServerTransport, JupyterServerTransport
from mcp.server import RequestHandler, Error
from mcp.types import (
    CallToolRequestParams, CallToolResponseContent, CallToolErrorContent,
    ListToolsRequestParams, ListToolsResponseParams,
    ListResourcesRequestParams, ListResourcesResponseParams,
    ReadResourceRequestParams, ReadResourceResponseParams
)

from common.client.a2a_agent_manager import AgentManager
from common.client.a2a_mcp_client import (
    Message, MessagePart, TaskSendParams, TaskIdParams, 
    TaskStatusUpdateEvent, TaskArtifactUpdateEvent
)


class A2AMCPServer:
    """MCP server that interfaces with A2A clients."""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.server = Server(
            name="a2a-client-server",
            version="0.1.0",
            capabilities={
                "tools": {},
                "resources": {},
            }
        )
        self._init_request_handlers()
    
    def _init_request_handlers(self) -> None:
        """Initialize request handlers for MCP methods."""
        # List tools
        self.server.set_request_handler(
            "mcp.list_tools",
            self._handle_list_tools
        )
        
        # Call tool
        self.server.set_request_handler(
            "mcp.call_tool",
            self._handle_call_tool
        )
        
        # List resources
        self.server.set_request_handler(
            "mcp.list_resources",
            self._handle_list_resources
        )
        
        # Read resource
        self.server.set_request_handler(
            "mcp.read_resource",
            self._handle_read_resource
        )
    
    async def _handle_list_tools(
        self, 
        params: ListToolsRequestParams
    ) -> ListToolsResponseParams:
        """Handle MCP list_tools request."""
        return {
            "tools": [
                {
                    "name": "a2a_send_task",
                    "description": "Send a task to an A2A agent",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to send to the agent",
                            },
                            "taskId": {
                                "type": "string",
                                "description": "Optional task ID. If not provided, a new UUID will be generated",
                            },
                            "agentId": {
                                "type": "string",
                                "description": "Optional agent ID. If not provided, the first available agent will be used",
                            },
                        },
                        "required": ["message"],
                    },
                },
                {
                    "name": "a2a_get_task",
                    "description": "Get the current state of a task",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "taskId": {
                                "type": "string",
                                "description": "ID of the task to retrieve",
                            },
                            "agentId": {
                                "type": "string",
                                "description": "ID of the agent that handled the task",
                            },
                        },
                        "required": ["taskId", "agentId"],
                    },
                },
                {
                    "name": "a2a_cancel_task",
                    "description": "Cancel a running task",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "taskId": {
                                "type": "string",
                                "description": "ID of the task to cancel",
                            },
                            "agentId": {
                                "type": "string",
                                "description": "ID of the agent that is handling the task",
                            },
                        },
                        "required": ["taskId", "agentId"],
                    },
                },
                {
                    "name": "a2a_send_task_subscribe",
                    "description": "Send a task and subscribe to updates (streaming)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to send to the agent",
                            },
                            "taskId": {
                                "type": "string",
                                "description": "Optional task ID. If not provided, a new UUID will be generated",
                            },
                            "agentId": {
                                "type": "string",
                                "description": "Optional agent ID. If not provided, the first available agent will be used",
                            },
                            "maxUpdates": {
                                "type": "number",
                                "description": "Maximum number of updates to receive (default: 10)",
                            },
                        },
                        "required": ["message"],
                    },
                },
                {
                    "name": "a2a_agent_info",
                    "description": "Get information about the connected A2A agents",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "agentId": {
                                "type": "string",
                                "description": "Optional agent ID. If not provided, information for all agents will be returned",
                            },
                        },
                    },
                },
            ]
        }
    
    async def _handle_call_tool(
        self, 
        params: CallToolRequestParams
    ) -> Union[CallToolResponseContent, CallToolErrorContent]:
        """Handle MCP call_tool request."""
        name = params["name"]
        args = params["arguments"]
        
        try:
            if name == "a2a_send_task":
                message = args["message"]
                task_id = args.get("taskId")
                agent_id = args.get("agentId")
                
                clients = self.agent_manager.get_all_clients()
                client = None
                
                if agent_id:
                    client = self.agent_manager.get_client_by_id(agent_id)
                    if not client:
                        raise Exception(f"No agent found with ID {agent_id}")
                elif clients:
                    # Get first available client
                    client = next(iter(clients.values()))
                else:
                    raise Exception("No available A2A agents")
                
                result = await client.send_task(TaskSendParams(
                    id=task_id or str(uuid.uuid4()),
                    message=Message(
                        role="user",
                        parts=[MessagePart(text=message)]
                    )
                ))
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result.model_dump(exclude_none=True) if result else None, indent=2)
                        }
                    ]
                }
                
            elif name == "a2a_get_task":
                task_id = args["taskId"]
                agent_id = args["agentId"]
                
                client = self.agent_manager.get_client_by_id(agent_id)
                if not client:
                    raise Exception(f"No agent found with ID {agent_id}")
                
                result = await client.get_task(TaskIdParams(id=task_id))
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result.model_dump(exclude_none=True) if result else None, indent=2)
                        }
                    ]
                }
                
            elif name == "a2a_cancel_task":
                task_id = args["taskId"]
                agent_id = args["agentId"]
                
                client = self.agent_manager.get_client_by_id(agent_id)
                if not client:
                    raise Exception(f"No agent found with ID {agent_id}")
                
                result = await client.cancel_task(TaskIdParams(id=task_id))
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result.model_dump(exclude_none=True) if result else None, indent=2)
                        }
                    ]
                }
                
            elif name == "a2a_send_task_subscribe":
                message = args["message"]
                task_id = args.get("taskId")
                agent_id = args.get("agentId")
                max_updates = args.get("maxUpdates", 10)
                
                clients = self.agent_manager.get_all_clients()
                client = None
                
                if agent_id:
                    client = self.agent_manager.get_client_by_id(agent_id)
                    if not client:
                        raise Exception(f"No agent found with ID {agent_id}")
                elif clients:
                    # Get first available client
                    client = next(iter(clients.values()))
                else:
                    raise Exception("No available A2A agents")
                
                id = task_id or str(uuid.uuid4())
                updates = []
                count = 0
                
                stream = client.send_task_subscribe(TaskSendParams(
                    id=id,
                    message=Message(
                        role="user",
                        parts=[MessagePart(text=message)]
                    )
                ))
                
                async for event in stream:
                    updates.append(event.model_dump(exclude_none=True))
                    count += 1
                    if count >= max_updates:
                        break
                    
                    if getattr(event, "final", False):
                        break
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"taskId": id, "updates": updates}, indent=2)
                        }
                    ]
                }
                
            elif name == "a2a_agent_info":
                agent_id = args.get("agentId")
                
                if agent_id:
                    client = self.agent_manager.get_client_by_id(agent_id)
                    if not client:
                        raise Exception(f"No agent found with ID {agent_id}")
                    
                    card = await client.agent_card()
                    
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(card.model_dump(exclude_none=True), indent=2)
                            }
                        ]
                    }
                else:
                    results = []
                    for id, client in self.agent_manager.get_all_clients().items():
                        try:
                            card = await client.agent_card()
                            results.append({
                                "agentId": id, 
                                "card": card.model_dump(exclude_none=True)
                            })
                        except Exception as error:
                            results.append({
                                "agentId": id, 
                                "error": str(error)
                            })
                    
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(results, indent=2)
                            }
                        ]
                    }
            
            else:
                raise Exception(f"Unknown tool: {name}")
                
        except Exception as error:
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"Error: {str(error)}"
                    }
                ],
                "isError": True
            }
    
    async def _handle_list_resources(
        self, 
        params: ListResourcesRequestParams
    ) -> ListResourcesResponseParams:
        """Handle MCP list_resources request."""
        endpoints = self.agent_manager.get_endpoints()
        
        return {
            "resources": [
                *[{
                    "uri": f"a2a://agent-card/{endpoint.id}",
                    "mimeType": "application/json",
                    "name": f"A2A Agent Card Information ({endpoint.id})"
                } for endpoint in endpoints],
                {
                    "uri": "a2a://tasks",
                    "mimeType": "application/json",
                    "name": "Recent A2A Tasks"
                }
            ]
        }
    
    async def _handle_read_resource(
        self, 
        params: ReadResourceRequestParams
    ) -> ReadResourceResponseParams:
        """Handle MCP read_resource request."""
        uri = params["uri"]
        
        if uri.startswith("a2a://agent-card/"):
            agent_id = uri.split("/")[2]
            client = self.agent_manager.get_client_by_id(agent_id)
            
            if not client:
                raise Error(f"No agent found with ID {agent_id}")
            
            try:
                card = await client.agent_card()
                
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(card.model_dump(exclude_none=True), indent=2)
                        }
                    ]
                }
            except Exception as error:
                raise Error(f"Failed to read agent card: {error}")
                
        elif uri == "a2a://tasks":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({"tasks": []}, indent=2)
                    }
                ]
            }
        
        raise Error(f"Resource not found: {uri}")
    
    async def start(self) -> None:
        """Start the MCP server."""
        print("Starting A2A Client MCP Server")
        
        # Initialize agent manager
        await self.agent_manager.initialize()
        
        # Determine transport based on environment
        if os.environ.get("JUPYTER_KERNEL_ID"):
            transport = JupyterServerTransport()
        else:
            transport = StdioServerTransport()
        
        await self.server.connect(transport)
        print("A2A Client MCP Server running")


def run_server() -> None:
    """Run the MCP server."""
    server = A2AMCPServer()
    asyncio.run(server.start())


if __name__ == "__main__":
    try:
        run_server()
    except Exception as e:
        print(f"Fatal error running server: {e}")
        import sys
        sys.exit(1)