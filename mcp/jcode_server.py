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
        from core.agent_manager import AgentManager
        self.manager = AgentManager()
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of available MCP tools."""
        return [
            {
                "name": "jcode.analyze",
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
                "name": "jcode.plan",
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
                "name": "jcode.implement",
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
                "name": "jcode.review",
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
                "name": "jcode.test",
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
                "name": "jcode.conductor",
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
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call."""
        # Map tool names to agent types
        agent_map = {
            "jcode.analyze": "analyst",
            "jcode.plan": "planner",
            "jcode.implement": "implementer",
            "jcode.review": "reviewer",
            "jcode.test": "tester",
            "jcode.conductor": "conductor"
        }
        
        if name not in agent_map:
            return {"error": f"Unknown tool: {name}"}
        
        agent_type = agent_map[name]
        input_data = arguments.get("input_data", {})
        
        result = self.manager.dispatch_agent(agent_type, input_data)
        
        return {
            "section": result.get("section"),
            "payload": result.get("payload"),
            "error": result.get("error"),
            "action": result.get("action")
        }


# For MCP protocol compatibility
def create_server():
    return JCodeMCPServer()


if __name__ == "__main__":
    server = create_server()
    print("JCode MCP Server initialized")
    print(f"Available tools: {[t['name'] for t in server.list_tools()]}")
