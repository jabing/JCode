"""
JCode MCP Server - Exposes JCode governance tools via MCP protocol

This server allows OMO (Oh-my-opencode) to call JCode agents as MCP tools.
"""

import json
from typing import Dict, Any, List

# MCP Server implementation
class JCodeMCPServer:
    """JCode MCP Server for OMO integration."""
    
    def __init__(self):
        # Agents are now called directly from mcp/server.py
        self.manager = None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of available MCP tools."""
        return [
            {
                "name": "analyze",
                "description": "JCode Analyst Agent - Validates problem analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "context_lock_id": {"type": "string"},
                        "input_data": {"type": "object"},
                        "mode": {"type": "string", "enum": ["full", "light", "safe", "fast", "custom"]}
                    },
                    "required": ["context_lock_id", "input_data", "mode"]
                }
            },
            {
                "name": "plan",
                "description": "JCode Planner Agent - Validates task planning",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "context_lock_id": {"type": "string"},
                        "input_data": {"type": "object"},
                        "mode": {"type": "string"}
                    },
                    "required": ["context_lock_id", "input_data", "mode"]
                }
            },
            {
                "name": "implement",
                "description": "JCode Implementer Agent - Validates code implementation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "context_lock_id": {"type": "string"},
                        "input_data": {"type": "object"},
                        "mode": {"type": "string"}
                    },
                    "required": ["context_lock_id", "input_data", "mode"]
                }
            },
            {
                "name": "review",
                "description": "JCode Reviewer Agent - Returns APPROVED/REJECTED verdict",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "context_lock_id": {"type": "string"},
                        "input_data": {"type": "object"},
                        "mode": {"type": "string"}
                    },
                    "required": ["context_lock_id", "input_data", "mode"]
                }
            },
            {
                "name": "test",
                "description": "JCode Tester Agent - Returns PASSED/FAILED verdict",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "context_lock_id": {"type": "string"},
                        "input_data": {"type": "object"},
                        "mode": {"type": "string"}
                    },
                    "required": ["context_lock_id", "input_data", "mode"]
                }
            },
            {
                "name": "conductor",
                "description": "JCode Conductor Agent - Final arbitration decision",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "context_lock_id": {"type": "string"},
                        "input_data": {"type": "object"},
                        "mode": {"type": "string"}
                    },
                    "required": ["context_lock_id", "input_data", "mode"]
                }
            }
        ]
    
    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Return tools list compatible with MCP tools/list method."""
        tools = self.list_tools()
        return {
            "tools": tools
        }


# For MCP protocol compatibility
    
    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Return tools list compatible with MCP tools/list method."""
        tools = self.list_tools()
        return {
            "tools": tools
        }


# For MCP protocol compatibility
def create_server():
    return JCodeMCPServer()


if __name__ == "__main__":
    server = create_server()
    print("JCode MCP Server initialized")
    print(f"Available tools: {[t['name'] for t in server.list_tools()]}")
