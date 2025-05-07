"""
A2A MCP Client in Python

This module provides a Python implementation of the A2A Client for MCP integration,
ported from the TypeScript implementation in MCP-A2A.
"""

import json
import uuid
import asyncio
import httpx
from typing import Dict, Any, Optional, List, AsyncIterator, Union, TypedDict, Literal
from pydantic import BaseModel, Field


# Type definitions
class MessagePart(BaseModel):
    text: str
    type: Optional[str] = "text"


class Message(BaseModel):
    role: Literal["user", "agent"]
    parts: List[MessagePart]


class TaskStatus(BaseModel):
    state: Literal["submitted", "working", "input-required", "completed", "canceled", "failed", "unknown"]
    message: Optional[Message] = None
    timestamp: Optional[str] = None


class Artifact(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[MessagePart]
    index: Optional[int] = None
    append: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    lastChunk: Optional[bool] = None


class Task(BaseModel):
    id: str
    status: TaskStatus
    artifacts: Optional[List[Artifact]] = None
    sessionId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskIdParams(BaseModel):
    id: str


class TaskSendParams(BaseModel):
    id: str
    message: Message


class TaskStatusUpdateEvent(BaseModel):
    id: str
    status: TaskStatus
    final: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskArtifactUpdateEvent(BaseModel):
    id: str
    artifact: Artifact
    final: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentProvider(BaseModel):
    organization: str
    url: Optional[str] = None


class AgentCapabilities(BaseModel):
    streaming: Optional[bool] = None
    pushNotifications: Optional[bool] = None
    stateTransitionHistory: Optional[bool] = None


class AgentAuthentication(BaseModel):
    schemes: List[str]
    credentials: Optional[str] = None


class AgentSkill(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    inputModes: Optional[List[str]] = None
    outputModes: Optional[List[str]] = None


class AgentCard(BaseModel):
    name: str
    description: Optional[str] = None
    url: str
    provider: Optional[AgentProvider] = None
    version: str
    documentationUrl: Optional[str] = None
    capabilities: AgentCapabilities
    authentication: Optional[AgentAuthentication] = None
    defaultInputModes: Optional[List[str]] = None
    defaultOutputModes: Optional[List[str]] = None
    skills: List[AgentSkill]


# JSON-RPC related types
class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Any


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None


class A2AClient:
    """Python implementation of the A2A client."""
    
    def __init__(self, base_url: str):
        # Ensure baseUrl doesn't end with a slash for consistency
        self.base_url = base_url[:-1] if base_url.endswith("/") else base_url
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    def _generate_request_id(self) -> str:
        """Helper to generate unique request IDs."""
        return str(uuid.uuid4())
    
    async def _make_http_request(
        self, 
        method: str, 
        params: Any, 
        accept_header: str = "application/json"
    ) -> httpx.Response:
        """Make a JSON-RPC request to the A2A server."""
        request_id = self._generate_request_id()
        request_body = JSONRPCRequest(
            jsonrpc="2.0",
            id=request_id,
            method=method,
            params=params
        )
        
        try:
            response = await self.http_client.post(
                self.base_url,
                headers={
                    "Content-Type": "application/json",
                    "Accept": accept_header,
                },
                json=request_body.model_dump(exclude_none=True),
            )
            return response
        except httpx.HTTPError as network_error:
            print(f"Network error during RPC call: {network_error}")
            raise Exception(f"Network error: {str(network_error)}")
    
    async def _handle_json_response(self, response: httpx.Response, expected_method: Optional[str] = None) -> Any:
        """Handle standard JSON-RPC responses."""
        response_body = None
        try:
            if not response.is_success:
                response_body = response.text
                try:
                    parsed_error = JSONRPCResponse.model_validate(json.loads(response_body))
                    if parsed_error.error:
                        raise Exception(f"{parsed_error.error.message} ({parsed_error.error.code})")
                except:
                    # Ignore parsing error, fall through to generic HTTP error
                    pass
                raise Exception(f"HTTP error {response.status_code}: {response.reason_phrase}{' - ' + response_body if response_body else ''}")
            
            response_body = response.text
            json_response = JSONRPCResponse.model_validate(json.loads(response_body))
            
            if json_response.error:
                raise Exception(f"{json_response.error.message} ({json_response.error.code})")
            
            return json_response.result
        except Exception as error:
            print(f"Error processing RPC response for method {expected_method or 'unknown'}: {error}")
            print(f"Response Body: {response_body}" if response_body else "")
            raise error
    
    async def _handle_streaming_response(
        self, 
        response: httpx.Response, 
        expected_method: Optional[str] = None
    ) -> AsyncIterator[Union[TaskStatusUpdateEvent, TaskArtifactUpdateEvent]]:
        """Handle streaming Server-Sent Events (SSE) responses."""
        if not response.is_success:
            error_text = None
            try:
                error_text = response.text
            except:
                # Ignore read error
                pass
            print(f"HTTP error {response.status_code} received for streaming method {expected_method or 'unknown'}.")
            if error_text:
                print(f"Response: {error_text}")
            raise Exception(f"HTTP error {response.status_code}: {response.reason_phrase} - Failed to establish stream.")
        
        buffer = ""
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data_line = line[6:].strip()
                if data_line:
                    try:
                        parsed_data = JSONRPCResponse.model_validate(json.loads(data_line))
                        if not parsed_data.jsonrpc or parsed_data.jsonrpc != "2.0":
                            print(f"Invalid SSE data structure received for method {expected_method}: {data_line}")
                            continue  # Skip invalid data
                        
                        if parsed_data.error:
                            print(f"Error received in SSE stream for method {expected_method}: {parsed_data.error}")
                            raise Exception(f"{parsed_data.error.message} ({parsed_data.error.code})")
                        elif parsed_data.result is not None:
                            # Determine if it's a status or artifact update
                            if isinstance(parsed_data.result, dict) and "status" in parsed_data.result:
                                yield TaskStatusUpdateEvent(**parsed_data.result)
                            elif isinstance(parsed_data.result, dict) and "artifact" in parsed_data.result:
                                yield TaskArtifactUpdateEvent(**parsed_data.result)
                            else:
                                yield parsed_data.result
                        else:
                            print(f"SSE data for {expected_method} has neither result nor error: {parsed_data}")
                    except Exception as e:
                        print(f"Failed to parse SSE data line for method {expected_method}: {data_line}")
                        print(f"Error: {e}")
    
    async def agent_card(self) -> AgentCard:
        """Retrieves the AgentCard."""
        try:
            # First try the well-known endpoint
            try:
                response = await self.http_client.get(f"{self.base_url}/.well-known/agent.json")
                if response.is_success:
                    return AgentCard.model_validate(response.json())
            except Exception as e:
                # Ignore and try the next approach
                pass
            
            # Then try the traditional endpoint
            card_url = f"{self.base_url}/agent-card"
            response = await self.http_client.get(
                card_url,
                headers={"Accept": "application/json"},
            )
            
            if not response.is_success:
                raise Exception(f"HTTP error {response.status_code} fetching agent card from {card_url}: {response.reason_phrase}")
            
            return AgentCard.model_validate(response.json())
        except Exception as error:
            print(f"Failed to fetch or parse agent card: {error}")
            raise Exception(f"Could not retrieve agent card: {str(error)}")
    
    async def send_task(self, params: TaskSendParams) -> Optional[Task]:
        """Sends a task request to the agent (non-streaming)."""
        http_response = await self._make_http_request("tasks/send", params.model_dump(exclude_none=True))
        result = await self._handle_json_response(http_response, "tasks/send")
        return Task.model_validate(result) if result else None
    
    async def send_task_subscribe(
        self, 
        params: TaskSendParams
    ) -> AsyncIterator[Union[TaskStatusUpdateEvent, TaskArtifactUpdateEvent]]:
        """Sends a task request and subscribes to streaming updates."""
        http_response = await self._make_http_request(
            "tasks/sendSubscribe",
            params.model_dump(exclude_none=True),
            "text/event-stream"
        )
        async for event in self._handle_streaming_response(http_response, "tasks/sendSubscribe"):
            yield event
    
    async def get_task(self, params: TaskIdParams) -> Optional[Task]:
        """Retrieves the current state of a task."""
        http_response = await self._make_http_request("tasks/get", params.model_dump(exclude_none=True))
        result = await self._handle_json_response(http_response, "tasks/get")
        return Task.model_validate(result) if result else None
    
    async def cancel_task(self, params: TaskIdParams) -> Optional[Task]:
        """Cancels a currently running task."""
        http_response = await self._make_http_request("tasks/cancel", params.model_dump(exclude_none=True))
        result = await self._handle_json_response(http_response, "tasks/cancel")
        return Task.model_validate(result) if result else None
    
    async def resubscribe_task(
        self, 
        params: TaskIdParams
    ) -> AsyncIterator[Union[TaskStatusUpdateEvent, TaskArtifactUpdateEvent]]:
        """Resubscribes to updates for a task after connection interruption."""
        http_response = await self._make_http_request(
            "tasks/resubscribe",
            params.model_dump(exclude_none=True),
            "text/event-stream"
        )
        async for event in self._handle_streaming_response(http_response, "tasks/resubscribe"):
            yield event
    
    async def supports(self, capability: Literal["streaming", "pushNotifications"]) -> bool:
        """Checks if the server likely supports optional methods based on agent card."""
        try:
            card = await self.agent_card()
            if capability == "streaming":
                return card.capabilities.streaming or False
            elif capability == "pushNotifications":
                return card.capabilities.pushNotifications or False
            else:
                return False
        except Exception as error:
            print(f"Failed to determine support for capability '{capability}': {error}")
            return False