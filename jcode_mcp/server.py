"""
JCode MCP Server - FastAPI server for MCP protocol integration.

This module provides a minimal FastAPI server with JSON-RPC 2.0 endpoint
for JCode v3.0 agent system. It is designed for OMO (Oh-my-opencode)
integration following the MCP (Model Context Protocol) standard.

Current implementation provides:
- /health endpoint with tool count (6 JCode agents)
- Foundation for JSON-RPC 2.0 protocol
- CLI interface with --port argument

Future implementations will add:
- Tool invocation logic for 6 JCode agents
- Context lock management
- Rule engine integration
"""
import argparse
import sys
from datetime import datetime, UTC
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# JCode agent tools count (fixed at 6 as per specification)
JCODE_TOOLS_COUNT = 6

# Create FastAPI application
app = FastAPI(
    title="JCode MCP Server",
    description="JCode v3.0 Agent System MCP Server - Oh-my-opencode governance extension layer",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns system status and tool count for MCP protocol compliance.
    This is a foundational endpoint for OMO tool discovery.
    
    Returns:
        dict: {
            "status": "ok",
            "tools": 6  # Count of available JCode agents
        }
    """
    return {
        "status": "ok",
        "tools": JCODE_TOOLS_COUNT
    }


@app.post("/rpc", tags=["JSON-RPC"])
async def json_rpc_handler(request: Request):
    """
    JSON-RPC 2.0 endpoint for tool invocation.
    
    This endpoint is reserved for future implementation of:
    - Tool call dispatching
    - Agent invocation via MCP protocol
    - Context lock integration
    
    Current status: Placeholder for JSON-RPC 2.0 protocol
    """
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": -32000,
            "message": "Tool invocation not yet implemented",
            "data": "This endpoint will be implemented in the next phase"
        },
        "id": None
    }


@app.post("/mcp", tags=["JSON-RPC"])
async def json_rpc_20_handler(request: Request):
    """
    JSON-RPC 2.0 Protocol endpoint.
    
    Implements the JSON-RPC 2.0 specification as defined in:
    https://www.jsonrpc.org/specification
    
    Request format:
        {
            "jsonrpc": "2.0",
            "id": <identifier>,
            "method": <method_name>,
            "params": <parameters>
        }
    
    Response format (success):
        {
            "jsonrpc": "2.0",
            "id": <identifier>,
            "result": <result>
        }
    
    Response format (error):
        {
            "jsonrpc": "2.0",
            "id": <identifier> or null,
            "error": {
                "code": <error_code>,
                "message": <error_message>,
                "data": <additional_data>
            }
        }
    
    Error codes:
        -32700  ParseError    Invalid JSON was received
        -32600  InvalidRequest JSON is not a valid request object
        -32601  MethodNotFound The method does not exist
        -32602  InvalidParams Input parameters are invalid
        -32603  InternalError Internal JSON-RPC error
    """
    import json
    
    # Try to parse the request body as JSON
    try:
        body = await request.json()
    except json.JSONDecodeError as e:
        # ParseError (-32700): Invalid JSON received
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error: Invalid JSON",
                    "data": str(e)
                }
            },
            status_code=200  # JSON-RPC errors are always 200 with error in body
        )
    except Exception as e:
        # Unexpected error parsing request
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": f"Failed to parse request: {str(e)}"
                }
            },
            status_code=200
        )
    
    # Validate JSON-RPC 2.0 request structure
    if not isinstance(body, dict):
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: Request must be a single object",
                    "data": "Batch requests are not supported"
                }
            },
            status_code=200
        )
    
    # Check required fields
    if "jsonrpc" not in body:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: Missing 'jsonrpc' field",
                    "data": "The 'jsonrpc' field is required and must be set to '2.0'"
                }
            },
            status_code=200
        )
    
    if body["jsonrpc"] != "2.0":
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: Unsupported JSON-RPC version",
                    "data": f"Expected '2.0', got '{body['jsonrpc']}'"
                }
            },
            status_code=200
        )
    
    if "id" not in body:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: Missing 'id' field",
                    "data": "The 'id' field is required"
                }
            },
            status_code=200
        )
    
    if "method" not in body:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: Missing 'method' field",
                    "data": "The 'method' field is required"
                }
            },
            status_code=200
        )
    
    # Extract request fields
    request_id = body["id"]
    method = body["method"]
    params = body.get("params", {})
    
    # Handle tools/list method
    if method == "tools/list":
        try:
            from jcode_mcp.jcode_server import create_server
            server = create_server()
            result = server.get_tool_list()
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                },
                status_code=200
            )
        except ImportError as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": f"Failed to import JCode server: {str(e)}"
                    }
                },
                status_code=200
            )
        except Exception as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": f"Tool list failed: {str(e)}"
                    }
                },
                status_code=200
            )
    
    # Handle tools/call method
    if method == "tools/call":
        params = body.get("params", {})
        
        # Extract tool name and arguments
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        # Handle analyze tool
        if tool_name == "analyze":
            try:
                from core.agents import AnalystAgent
                
                context_lock_id = arguments.get("context_lock_id", "")
                input_data = arguments.get("input_data", {})
                mode = arguments.get("mode", "full")
                
                if not input_data:
                    return JSONResponse(
                        content={
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32602,
                                "message": "Invalid params",
                                "data": "input_data is required"
                            }
                        },
                        status_code=200
                    )
                
                agent = AnalystAgent(project_root=".")
                result = agent.execute(input_data)
                
                analysis_result = {
                    "section": result.section,
                    "verifiability": result.output.get("verifiability", "UNKNOWN"),
                    "checks": result.output.get("checks", []),
                    "warnings": result.output.get("warnings", []),
                    "action": result.output.get("action", "CONTINUE")
                }
                
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Analysis complete: {result.section}\n\n"
                                           f"Verifiability: {analysis_result['verifiability']}\n"
                                           f"Action: {analysis_result['action']}\n"
                                           f"Checks: {len(analysis_result['checks'])}\n"
                                           f"Warnings: {len(analysis_result['warnings'])}"
                                }
                            ]
                        }
                    },
                    status_code=200
                )
                
            except ImportError as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Failed to import AnalystAgent: {str(e)}"
                        }
                    },
                    status_code=200
                )
            except Exception as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Analyst agent execution failed: {str(e)}"
                        }
                    },
                    status_code=200
                )
        
        # Handle plan tool
        if tool_name == "plan":
            try:
                from core.agents import PlannerAgent
                
                context_lock_id = arguments.get("context_lock_id", "")
                input_data = arguments.get("input_data", {})
                mode = arguments.get("mode", "full")
                
                if not input_data:
                    return JSONResponse(
                        content={
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32602,
                                "message": "Invalid params",
                                "data": "input_data is required"
                            }
                        },
                        status_code=200
                    )
                
                agent = PlannerAgent(project_root=".")
                result = agent.execute(input_data)
                
                planner_result = {
                    "section": result.section,
                    "checks": result.output.get("checks", []),
                    "warnings": result.output.get("warnings", []),
                    "action": result.output.get("action", "CONTINUE")
                }
                
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Analysis complete: {result.section}\n\n"
                                           f"Verifiability: CHECKS_COMPLETE\n"
                                           f"Action: {planner_result['action']}\n"
                                           f"Checks: {len(planner_result['checks'])}\n"
                                           f"Warnings: {len(planner_result['warnings'])}"
                                }
                            ]
                        }
                    },
                    status_code=200
                )
                
            except ImportError as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Failed to import PlannerAgent: {str(e)}"
                        }
                    },
                    status_code=200
                )
            except Exception as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Planner agent execution failed: {str(e)}"
                        }
                    },
                    status_code=200
                )
        
        # Handle implement tool
        if tool_name == "implement":
            try:
                from core.agents import ImplementerAgent
                
                context_lock_id = arguments.get("context_lock_id", "")
                input_data = arguments.get("input_data", {})
                mode = arguments.get("mode", "full")
                
                if not input_data:
                    return JSONResponse(
                        content={
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32602,
                                "message": "Invalid params",
                                "data": "input_data is required"
                            }
                        },
                        status_code=200
                    )
                
                agent = ImplementerAgent(project_root=".")
                result = agent.execute(input_data)
                
                implementer_result = {
                    "section": result.section,
                    "checks": result.output.get("checks", []),
                    "warnings": result.output.get("warnings", []),
                    "action": result.output.get("action", "CONTINUE")
                }
                
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Implementation complete: {result.section}\n\n"
                                           f"Verifiability: CHECKS_COMPLETE\n"
                                           f"Action: {implementer_result['action']}\n"
                                           f"Checks: {len(implementer_result['checks'])}\n"
                                           f"Warnings: {len(implementer_result['warnings'])}"
                                }
                            ]
                        }
                    },
                    status_code=200
                )
                
            except ImportError as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Failed to import ImplementerAgent: {str(e)}"
                        }
                    },
                    status_code=200
                )
            except Exception as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Implementer agent execution failed: {str(e)}"
                        }
                    },
                    status_code=200
                )
        
        # Handle review tool
        if tool_name == "review":
            try:
                from core.agents import ReviewerAgent
                
                context_lock_id = arguments.get("context_lock_id", "")
                input_data = arguments.get("input_data", {})
                mode = arguments.get("mode", "full")
                
                if not input_data:
                    return JSONResponse(
                        content={
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32602,
                                "message": "Invalid params",
                                "data": "input_data is required"
                            }
                        },
                        status_code=200
                    )
                
                agent = ReviewerAgent(project_root=".")
                result = agent.execute(input_data)
                
                reviewer_result = {
                    "section": result.section,
                    "verdict": result.output.get("verdict", "UNKNOWN"),
                    "checks": result.output.get("checks", []),
                    "warnings": result.output.get("warnings", []),
                    "action": result.output.get("action", "CONTINUE")
                }
                
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Review complete: {result.section}\n\n"
                                           f"Verdict: {reviewer_result['verdict']}\n"
                                           f"Action: {reviewer_result['action']}\n"
                                           f"Checks: {len(reviewer_result['checks'])}\n"
                                           f"Warnings: {len(reviewer_result['warnings'])}"
                                }
                            ]
                        }
                    },
                    status_code=200
                )
                
            except ImportError as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Failed to import ReviewerAgent: {str(e)}"
                        }
                    },
                    status_code=200
                )
            except Exception as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Reviewer agent execution failed: {str(e)}"
                        }
                    },
                    status_code=200
                )
        
        # Handle test tool
        if tool_name == "test":
            try:
                from core.agents import TesterAgent
                
                context_lock_id = arguments.get("context_lock_id", "")
                input_data = arguments.get("input_data", {})
                mode = arguments.get("mode", "full")
                
                if not input_data:
                    return JSONResponse(
                        content={
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32602,
                                "message": "Invalid params",
                                "data": "input_data is required"
                            }
                        },
                        status_code=200
                    )
                
                agent = TesterAgent(project_root=".")
                result = agent.execute(input_data)
                
                tester_result = {
                    "section": result.section,
                    "verdict": result.output.get("verdict", "UNKNOWN"),
                    "checks": result.output.get("checks", []),
                    "warnings": result.output.get("warnings", []),
                    "action": result.output.get("action", "CONTINUE")
                }
                
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Test complete: {result.section}\n\n"
                                           f"Verdict: {tester_result['verdict']}\n"
                                           f"Action: {tester_result['action']}\n"
                                           f"Checks: {len(tester_result['checks'])}\n"
                                           f"Warnings: {len(tester_result['warnings'])}"
                                }
                            ]
                        }
                    },
                    status_code=200
                )
                
            except ImportError as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Failed to import TesterAgent: {str(e)}"
                        }
                    },
                    status_code=200
                )
            except Exception as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Tester agent execution failed: {str(e)}"
                        }
                    },
                    status_code=200
                )
        
        # Handle conductor tool
        if tool_name == "conductor":
            try:
                from core.agents import ConductorAgent
                
                context_lock_id = arguments.get("context_lock_id", "")
                input_data = arguments.get("input_data", {})
                mode = arguments.get("mode", "full")
                
                if not input_data:
                    return JSONResponse(
                        content={
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32602,
                                "message": "Invalid params",
                                "data": "input_data is required"
                            }
                        },
                        status_code=200
                    )
                
                agent = ConductorAgent(project_root=".")
                result = agent.execute(input_data)
                
                conductor_result = {
                    "section": result.section,
                    "verdict": result.output.get("verdict", "UNKNOWN"),
                    "checks": result.output.get("checks", []),
                    "warnings": result.output.get("warnings", []),
                    "action": result.output.get("action", "CONTINUE")
                }
                
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Conductor decision: {result.section}\n\n"
                                           f"Verdict: {conductor_result['verdict']}\n"
                                           f"Action: {conductor_result['action']}\n"
                                           f"Checks: {len(conductor_result['checks'])}\n"
                                           f"Warnings: {len(conductor_result['warnings'])}"
                                }
                            ]
                        }
                    },
                    status_code=200
                )
                
            except ImportError as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Failed to import ConductorAgent: {str(e)}"
                        }
                    },
                    status_code=200
                )
            except Exception as e:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": f"Conductor agent execution failed: {str(e)}"
                        }
                    },
                    status_code=200
                )
        
        # Tool not found
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": "Method not found",
                    "data": f"Tool '{tool_name}' is not implemented"
                }
            },
            status_code=200
        )
    
    # Check for unknown method
    return JSONResponse(
        content={
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": f"Method '{method}' is not implemented. Available methods: tools/list, tools/call (pending)"
            }
        },
        status_code=200
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions with consistent error response format."""
    return JSONResponse(
        status_code=500,
        content={
            "error_type": type(exc).__name__,
            "message": str(exc) if str(exc) else "An unexpected error occurred",
            "action": "Contact system administrator or check logs",
            "timestamp": datetime.now(UTC).isoformat()
        }
    )


def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    """
    Find an available port starting from start_port.
    
    Args:
        start_port: The port to start checking from
        max_attempts: Maximum number of ports to try
        
    Returns:
        int: Available port number
    """
    import socket
    
    # If port 0 is requested, ask the OS for an available ephemeral port
    # and return that port so the server can bind to it explicitly.
    if start_port == 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", 0))  # OS selects an available port
            assigned_port = s.getsockname()[1]
            return assigned_port

    port = start_port
    for _ in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
            return port
        except OSError:
            port += 1
    
    return port


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="JCode MCP Server - FastAPI server for MCP protocol"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the server on (default: 8080)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    return parser.parse_args()


def main():
    """Main entry point for the MCP server."""
    args = parse_args()
    
    port = find_available_port(args.port)
    
    if port != args.port:
        if args.port == 0:
            print(f"Dynamic port allocated: {port}")
        else:
            print(f"Warning: Port {args.port} is busy, using port {port}")
    
    print(f"JCode MCP Server v3.0.0")
    print(f"Available tools: {JCODE_TOOLS_COUNT} (analyst, planner, implementer, reviewer, tester, conductor)")
    print(f"Health endpoint: http://{args.host}:{port}/health")
    print(f"JSON-RPC endpoint: http://{args.host}:{port}/rpc")
    print(f"Server starting...")
    
    uvicorn.run(
        "jcode_mcp.server:app",
        host=args.host,
        port=port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
