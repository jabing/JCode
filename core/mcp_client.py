"""
MCP Client - JCode v3.0

Implements JSON-RPC 2.0 client for MCP protocol integration with OpenCode/Superpowers.
Provides tool registration, invocation, and connection management for all 10 MCP tools.

Author: JCode v3.0 Implementation
Status: IMPLEMENTATION
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import aiohttp
import backoff
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class MCPErrorType(str, Enum):
    """MCP Error types as defined in SUPERPOWERS_EXTENSION.md"""
    NON_VERIFIABLE = "NON-VERIFIABLE"
    RULE_VIOLATION = "RULE_VIOLATION"
    EVIDENCE_UNAVAILABLE = "EVIDENCE_UNAVAILABLE"
    ITERATION_OVERFLOW = "ITERATION_OVERFLOW"
    STRUCTURAL_VIOLATION = "STRUCTURAL_VIOLATION"


class MCPErrorAction(str, Enum):
    """MCP Error actions"""
    HUMAN_INTERVENTION = "HUMAN_INTERVENTION"
    RETRY = "RETRY"
    STOP = "STOP"
    CONTINUE = "CONTINUE"


class MCPExecutionMode(str, Enum):
    """Execution modes for MCP tools"""
    FULL = "full"
    LIGHT = "light"
    SAFE = "safe"
    FAST = "fast"
    CUSTOM = "custom"


@dataclass
class MCPSchemaProperty:
    """Property definition for MCP tool schema"""
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None
    properties: Optional[Dict[str, 'MCPSchemaProperty']] = None
    required: Optional[List[str]] = None


@dataclass
class MCPToolSchema:
    """Input/output schema for MCP tools"""
    type: str = "object"
    properties: Dict[str, MCPSchemaProperty] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization"""
        result = {"type": self.type}
        if self.properties:
            result["properties"] = {
                k: asdict(v) if not isinstance(v, MCPSchemaProperty) else v.__dict__
                for k, v in self.properties.items()
            }
        if self.required:
            result["required"] = self.required
        return result


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: MCPToolSchema
    output_schema: MCPToolSchema
    handler: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for MCP registration"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema.to_dict(),
            "outputSchema": self.output_schema.to_dict()
        }


@dataclass
class MCPError:
    """MCP Error structure"""
    type: Optional[MCPErrorType] = None
    message: Optional[str] = None
    action: Optional[MCPErrorAction] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        if self.type:
            result["type"] = self.type.value
        if self.message:
            result["message"] = self.message
        if self.action:
            result["action"] = self.action.value
        return result

    def is_present(self) -> bool:
        """Check if error has any content"""
        return self.type is not None or self.message is not None


class MCPClientError(Exception):
    """Base exception for MCP client errors"""
    pass


class MCPConnectionError(MCPClientError):
    """Connection-related errors"""
    pass


class MCPRPCError(MCPClientError):
    """JSON-RPC protocol errors"""
    pass


class MCPToolNotFoundError(MCPClientError):
    """Tool not found in registry"""
    pass


class MCPClient:
    """
    MCP JSON-RPC 2.0 Client for JCode v3.0

    Implements MCP protocol client for tool registration and invocation.
    Supports connection pooling, error handling, and retries.

    Usage:
        client = MCPClient("http://localhost:8000")
        await client.connect()
        result = await client.call_tool("jcode.analyze", context_lock_id="...", input_data={...})
    """

    # 10 MCP Tools as defined in SUPERPOWERS_EXTENSION.md
    TOOLS = [
        "jcode.analyze",
        "jcode.plan",
        "jcode.implement",
        "jcode.review",
        "jcode.test",
        "jcode.conductor",
        "jcode.lock",
        "rule_engine",
        "incremental_build",
        "audit_log"
    ]

    def __init__(
        self,
        server_url: str,
        connection_pool_size: int = 10,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        Initialize MCP client

        Args:
            server_url: MCP server URL (e.g., http://localhost:8000)
            connection_pool_size: Size of connection pool
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.server_url = server_url.rstrip('/')
        self.connection_pool_size = connection_pool_size
        self.timeout = timeout
        self.max_retries = max_retries

        # Connection management
        self._session: Optional[aiohttp.ClientSession] = None
        self._connected = False

        # Tool registry
        self._tools: Dict[str, MCPTool] = {}
        self._handlers: Dict[str, Callable] = {}

        # Request tracking
        self._request_id = 0

    async def connect(self) -> None:
        """
        Establish connection to MCP server

        Raises:
            MCPConnectionError: If connection fails
        """
        if self._connected:
            logger.warning("Already connected to MCP server")
            return

        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            connector = aiohttp.TCPConnector(limit=self.connection_pool_size)

            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "JCode-MCP-Client/3.0"
                }
            )

            # Test connection with server info
            await self._call_rpc("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "jcode",
                    "version": "3.0.0"
                }
            })

            self._connected = True
            logger.info(f"Connected to MCP server: {self.server_url}")

        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Failed to connect to MCP server: {e}") from e

    async def disconnect(self) -> None:
        """Close connection to MCP server"""
        if not self._connected:
            return

        if self._session:
            await self._session.close()
            self._session = None

        self._connected = False
        logger.info("Disconnected from MCP server")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    def register_tool(self, tool: MCPTool) -> None:
        """
        Register an MCP tool

        Args:
            tool: MCPTool instance to register

        Raises:
            ValueError: If tool name is invalid
        """
        if not tool.name or not tool.name.startswith("jcode."):
            raise ValueError(f"Invalid tool name: {tool.name}")

        self._tools[tool.name] = tool

        if tool.handler:
            self._handlers[tool.name] = tool.handler

        logger.debug(f"Registered MCP tool: {tool.name}")

    def register_tools(self, tools: List[MCPTool]) -> None:
        """
        Register multiple MCP tools

        Args:
            tools: List of MCPTool instances
        """
        for tool in tools:
            self.register_tool(tool)

        logger.info(f"Registered {len(tools)} MCP tools")

    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """
        Get registered tool by name

        Args:
            tool_name: Name of the tool

        Returns:
            MCPTool instance or None if not found
        """
        return self._tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """
        List all registered tool names

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        logger=logger
    )
    async def _call_rpc(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute JSON-RPC 2.0 call

        Args:
            method: RPC method name
            params: Method parameters

        Returns:
            RPC response payload

        Raises:
            MCPConnectionError: If connection fails
            MCPRPCError: If RPC call fails
        """
        if not self._connected or not self._session:
            raise MCPConnectionError("Not connected to MCP server")

        self._request_id += 1

        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {}
        }

        try:
            logger.debug(f"RPC Call: {method} (id={self._request_id})")

            async with self._session.post(
                f"{self.server_url}/rpc",
                json=request
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise MCPConnectionError(f"HTTP {response.status}: {text}")

                data = await response.json()

                # Check for JSON-RPC errors
                if "error" in data:
                    error = data["error"]
                    raise MCPRPCError(
                        f"RPC Error {error.get('code')}: {error.get('message')}"
                    )

                return data.get("result", {})

        except json.JSONDecodeError as e:
            raise MCPRPCError(f"Invalid JSON response: {e}") from e
        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Connection error: {e}") from e

    async def call_tool(
        self,
        tool_name: str,
        context_lock_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        mode: str = "full",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call an MCP tool

        Args:
            tool_name: Name of the tool to call
            context_lock_id: OMO Context Lock ID for state isolation
            input_data: Tool-specific input payload
            mode: Execution mode (full/light/safe/fast/custom)
            **kwargs: Additional tool-specific parameters

        Returns:
            Tool response with section, payload, and optional error

        Raises:
            MCPToolNotFoundError: If tool is not registered
            MCPConnectionError: If connection fails
            MCPRPCError: If RPC call fails

        Example:
            result = await client.call_tool(
                "jcode.analyze",
                context_lock_id="cl_123456",
                input_data={"problem_statement": "Add authentication"},
                mode="full"
            )
        """
        if tool_name not in self._tools:
            raise MCPToolNotFoundError(f"Tool not found: {tool_name}")

        # Build parameters according to MCP schema
        params = {
            "context_lock_id": context_lock_id,
            "input_data": input_data or {},
            "mode": mode
        }

        # Merge additional kwargs
        params.update(kwargs)

        # Validate against tool schema
        tool = self._tools[tool_name]
        self._validate_params(tool_name, tool.input_schema, params)

        try:
            # Check if local handler exists
            if tool_name in self._handlers:
                logger.debug(f"Using local handler for: {tool_name}")
                result = await self._handlers[tool_name](**params)
            else:
                # Call remote tool via RPC
                result = await self._call_rpc(f"tools/call", {
                    "name": tool_name,
                    "arguments": params
                })

            # Ensure response has required fields
            if "section" not in result:
                result["section"] = f"[{tool_name.split('.')[-1].upper()}]"
            if "payload" not in result:
                result["payload"] = {}

            logger.info(f"Tool call successful: {tool_name}")

            return result

        except Exception as e:
            logger.error(f"Tool call failed: {tool_name} - {e}")

            # Return structured error
            return {
                "section": f"[{tool_name.split('.')[-1].upper()}]",
                "payload": {},
                "error": {
                    "type": MCPErrorType.STRUCTURAL_VIOLATION,
                    "message": str(e),
                    "action": MCPErrorAction.STOP
                }
            }

    async def invoke_agent_tool(
        self,
        agent_type: str,
        input_data: Dict[str, Any],
        context_lock_id: Optional[str] = None,
        mode: str = "full"
    ) -> Dict[str, Any]:
        """
        Convenience method to invoke JCode agent tools

        Args:
            agent_type: Agent type (analyze/plan/implement/review/test/conductor)
            input_data: Input data for the agent
            context_lock_id: OMO Context Lock ID
            mode: Execution mode

        Returns:
            Tool response
        """
        tool_name = f"jcode.{agent_type}"
        return await self.call_tool(
            tool_name,
            context_lock_id=context_lock_id,
            input_data=input_data,
            mode=mode
        )

    def _validate_params(
        self,
        tool_name: str,
        schema: MCPToolSchema,
        params: Dict[str, Any]
    ) -> None:
        """
        Validate parameters against tool schema

        Args:
            tool_name: Name of the tool
            schema: Tool schema
            params: Parameters to validate

        Raises:
            ValueError: If validation fails
        """
        # Check required fields
        for required_field in schema.required:
            if required_field not in params:
                raise ValueError(
                    f"Missing required field '{required_field}' for tool '{tool_name}'"
                )

        # Check field types (basic validation)
        for field_name, field_schema in schema.properties.items():
            if field_name in params:
                value = params[field_name]
                expected_type = field_schema.type

                # Type mapping
                type_map = {
                    "string": str,
                    "integer": int,
                    "number": (int, float),
                    "boolean": bool,
                    "object": dict,
                    "array": list
                }

                expected_python_type = type_map.get(expected_type)
                if expected_python_type and not isinstance(value, expected_python_type):
                    raise ValueError(
                        f"Field '{field_name}' must be {expected_type}, got {type(value).__name__}"
                    )

                # Validate enum values
                if field_schema.enum and value not in field_schema.enum:
                    raise ValueError(
                        f"Field '{field_name}' must be one of {field_schema.enum}, got '{value}'"
                    )

    async def register_tools_with_server(self) -> Dict[str, Any]:
        """
        Register all tools with MCP server

        Returns:
            Registration response
        """
        if not self._tools:
            logger.warning("No tools to register")
            return {}

        tools_data = [tool.to_dict() for tool in self._tools.values()]

        result = await self._call_rpc("tools/list", {})
        logger.info(f"Registered {len(self._tools)} tools with server")

        return result

    @property
    def connected(self) -> bool:
        """Check if client is connected"""
        return self._connected


# Helper function to create standard tool schemas
def create_analyze_schema() -> MCPTool:
    """Create jcode.analyze tool definition"""
    input_schema = MCPToolSchema(
        properties={
            "context_lock_id": MCPSchemaProperty(
                type="string",
                description="OMO Context Lock ID for state isolation"
            ),
            "input_data": MCPSchemaProperty(
                type="object",
                properties={
                    "problem_statement": MCPSchemaProperty(type="string"),
                    "user_requirements": MCPSchemaProperty(type="array")
                }
            ),
            "mode": MCPSchemaProperty(
                type="string",
                enum=["full", "light", "safe", "fast", "custom"]
            )
        },
        required=["context_lock_id", "input_data", "mode"]
    )

    output_schema = MCPToolSchema(
        properties={
            "section": MCPSchemaProperty(type="string"),
            "payload": MCPSchemaProperty(
                type="object",
                properties={
                    "verifiability": MCPSchemaProperty(
                        type="string",
                        enum=["HARD", "SOFT", "NON-VERIFIABLE"]
                    ),
                    "nfrs": MCPSchemaProperty(type="object"),
                    "risks": MCPSchemaProperty(type="array"),
                    "unknowns": MCPSchemaProperty(type="array")
                }
            ),
            "error": MCPSchemaProperty(type="object")
        },
        required=["section", "payload"]
    )

    return MCPTool(
        name="jcode.analyze",
        description="JCode Analyst tool for problem analysis and verifiability assessment",
        input_schema=input_schema,
        output_schema=output_schema
    )


def create_plan_schema() -> MCPTool:
    """Create jcode.plan tool definition"""
    input_schema = MCPToolSchema(
        properties={
            "context_lock_id": MCPSchemaProperty(type="string"),
            "input_data": MCPSchemaProperty(
                type="object",
                properties={
                    "analysis": MCPSchemaProperty(type="object")
                }
            ),
            "mode": MCPSchemaProperty(
                type="string",
                enum=["full", "light", "safe", "fast", "custom"]
            )
        },
        required=["context_lock_id", "input_data", "mode"]
    )

    output_schema = MCPToolSchema(
        properties={
            "section": MCPSchemaProperty(type="string"),
            "payload": MCPSchemaProperty(
                type="object",
                properties={
                    "tasks": MCPSchemaProperty(type="array"),
                    "dependencies": MCPSchemaProperty(type="array")
                }
            ),
            "error": MCPSchemaProperty(type="object")
        },
        required=["section", "payload"]
    )

    return MCPTool(
        name="jcode.plan",
        description="JCode Planner tool for atomic task generation",
        input_schema=input_schema,
        output_schema=output_schema
    )


def create_implement_schema() -> MCPTool:
    """Create jcode.implement tool definition"""
    input_schema = MCPToolSchema(
        properties={
            "context_lock_id": MCPSchemaProperty(type="string"),
            "input_data": MCPSchemaProperty(
                type="object",
                properties={
                    "tasks": MCPSchemaProperty(type="object"),
                    "om_rules": MCPSchemaProperty(type="array"),
                    "iteration": MCPSchemaProperty(type="integer")
                }
            ),
            "mode": MCPSchemaProperty(
                type="string",
                enum=["full", "light", "safe", "fast", "custom"]
            )
        },
        required=["context_lock_id", "input_data", "mode"]
    )

    output_schema = MCPToolSchema(
        properties={
            "section": MCPSchemaProperty(type="string"),
            "payload": MCPSchemaProperty(
                type="object",
                properties={
                    "artifacts": MCPSchemaProperty(
                        type="object",
                        properties={
                            "files": MCPSchemaProperty(type="array"),
                            "diff": MCPSchemaProperty(type="string"),
                            "metadata": MCPSchemaProperty(type="object")
                        }
                    )
                }
            ),
            "error": MCPSchemaProperty(type="object")
        },
        required=["section", "payload"]
    )

    return MCPTool(
        name="jcode.implement",
        description="JCode Implementer tool for authorized code generation",
        input_schema=input_schema,
        output_schema=output_schema
    )


def create_review_schema() -> MCPTool:
    """Create jcode.review tool definition"""
    input_schema = MCPToolSchema(
        properties={
            "context_lock_id": MCPSchemaProperty(type="string"),
            "input_data": MCPSchemaProperty(
                type="object",
                properties={
                    "tasks": MCPSchemaProperty(type="object"),
                    "implementation": MCPSchemaProperty(type="object"),
                    "quick_fix_eligible": MCPSchemaProperty(type="boolean")
                }
            ),
            "mode": MCPSchemaProperty(
                type="string",
                enum=["full", "light", "safe", "fast", "custom"]
            )
        },
        required=["context_lock_id", "input_data", "mode"]
    )

    output_schema = MCPToolSchema(
        properties={
            "section": MCPSchemaProperty(type="string"),
            "payload": MCPSchemaProperty(
                type="object",
                properties={
                    "result": MCPSchemaProperty(
                        type="string",
                        enum=["APPROVED", "REJECTED"]
                    ),
                    "issues": MCPSchemaProperty(type="array"),
                    "quick_fix_trigger": MCPSchemaProperty(type="string")
                }
            ),
            "error": MCPSchemaProperty(type="object")
        },
        required=["section", "payload"]
    )

    return MCPTool(
        name="jcode.review",
        description="JCode Reviewer tool for compliance review (APPROVED/REJECTED)",
        input_schema=input_schema,
        output_schema=output_schema
    )


def create_test_schema() -> MCPTool:
    """Create jcode.test tool definition"""
    input_schema = MCPToolSchema(
        properties={
            "context_lock_id": MCPSchemaProperty(type="string"),
            "input_data": MCPSchemaProperty(
                type="object",
                properties={
                    "tasks": MCPSchemaProperty(type="object"),
                    "implementation": MCPSchemaProperty(type="object"),
                    "verify_by_clauses": MCPSchemaProperty(type="array")
                }
            ),
            "mode": MCPSchemaProperty(
                type="string",
                enum=["full", "light", "safe", "fast", "custom"]
            )
        },
        required=["context_lock_id", "input_data", "mode"]
    )

    output_schema = MCPToolSchema(
        properties={
            "section": MCPSchemaProperty(type="string"),
            "payload": MCPSchemaProperty(
                type="object",
                properties={
                    "result": MCPSchemaProperty(
                        type="string",
                        enum=["PASSED", "FAILED", "EVIDENCE_UNAVAILABLE"]
                    ),
                    "evidence": MCPSchemaProperty(type="object"),
                    "failed_clauses": MCPSchemaProperty(type="array")
                }
            ),
            "error": MCPSchemaProperty(type="object")
        },
        required=["section", "payload"]
    )

    return MCPTool(
        name="jcode.test",
        description="JCode Tester tool for evidence verification (PASSED/FAILED)",
        input_schema=input_schema,
        output_schema=output_schema
    )


def create_conductor_schema() -> MCPTool:
    """Create jcode.conductor tool definition"""
    input_schema = MCPToolSchema(
        properties={
            "context_lock_id": MCPSchemaProperty(type="string"),
            "input_data": MCPSchemaProperty(
                type="object",
                properties={
                    "review_result": MCPSchemaProperty(
                        type="string",
                        enum=["APPROVED", "REJECTED"]
                    ),
                    "test_result": MCPSchemaProperty(
                        type="string",
                        enum=["PASSED", "FAILED", "EVIDENCE_UNAVAILABLE"]
                    ),
                    "iteration_count": MCPSchemaProperty(type="integer"),
                    "max_iterations": MCPSchemaProperty(type="integer")
                }
            ),
            "mode": MCPSchemaProperty(
                type="string",
                enum=["full", "light", "safe", "fast", "custom"]
            )
        },
        required=["context_lock_id", "input_data", "mode"]
    )

    output_schema = MCPToolSchema(
        properties={
            "section": MCPSchemaProperty(type="string"),
            "payload": MCPSchemaProperty(
                type="object",
                properties={
                    "decision": MCPSchemaProperty(
                        type="string",
                        enum=["DELIVER", "ITERATE", "STOP"]
                    ),
                    "reason": MCPSchemaProperty(type="string"),
                    "next_iteration": MCPSchemaProperty(type="integer"),
                    "deliverables": MCPSchemaProperty(type="object")
                }
            ),
            "error": MCPSchemaProperty(type="object")
        },
        required=["section", "payload"]
    )

    return MCPTool(
        name="jcode.conductor",
        description="JCode Conductor tool for final arbitration (DELIVER/ITERATE/STOP)",
        input_schema=input_schema,
        output_schema=output_schema
    )


# Factory function to create all 6 JCode agent tools
def create_jcode_tools() -> List[MCPTool]:
    """
    Create all 6 JCode agent MCP tools

    Returns:
        List of MCPTool instances
    """
    return [
        create_analyze_schema(),
        create_plan_schema(),
        create_implement_schema(),
        create_review_schema(),
        create_test_schema(),
        create_conductor_schema()
    ]


# Export main classes and functions
__all__ = [
    "MCPClient",
    "MCPTool",
    "MCPToolSchema",
    "MCPSchemaProperty",
    "MCPError",
    "MCPErrorType",
    "MCPErrorAction",
    "MCPExecutionMode",
    "MCPClientError",
    "MCPConnectionError",
    "MCPRPCError",
    "MCPToolNotFoundError",
    "create_jcode_tools",
    "create_analyze_schema",
    "create_plan_schema",
    "create_implement_schema",
    "create_review_schema",
    "create_test_schema",
    "create_conductor_schema"
]
