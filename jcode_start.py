#!/usr/bin/env python3
"""
JCode v3.0 - Main Entry Point

JCode is an Oh-my-opencode (OMO) governance extension layer.
This script provides a unified entry point for starting JCode services.

Usage:
    python jcode_start.py --help
    python jcode_start.py api [--port 8000]
    python jcode_start.py cli <command>
    python jcode_start.py mcp
    python jcode_start.py status
"""

import sys
import argparse
import subprocess
from pathlib import Path


def start_api(port: int = 8000, host: str = "0.0.0.0"):
    """Start the JCode API server."""
    import uvicorn
    print(f"Starting JCode API server on {host}:{port}...")
    uvicorn.run("api.main:app", host=host, port=port, reload=True)


def run_cli(args: list):
    """Run CLI command."""
    from cli.commands import jcode
    print("Running JCode CLI...")
    jcode(args)


def start_mcp():
    """Start the JCode MCP server."""
    print("Starting JCode MCP server...")
    from mcp.jcode_server import create_server
    server = create_server()
    print(f"MCP Server initialized with {len(server.list_tools())} tools:")
    for tool in server.list_tools():
        print(f"  - {tool['name']}")
    print("\nMCP server is ready. Integrate with OMO via MCP protocol.")


def show_status():
    """Show JCode status."""
    print("=" * 50)
    print("JCode v3.0 Status")
    print("=" * 50)
    
    # Check configuration
    try:
        from core.switch_manager import create_switch_manager
        sm = create_switch_manager()
        enabled = sm.get("global", "enabled")
        mode = sm.get("mode")
        print(f"\nConfiguration:")
        print(f"  Enabled: {enabled}")
        print(f"  Mode: {mode}")
    except Exception as e:
        print(f"  Error reading config: {e}")
    
    # Check agents
    try:
        from core.agent_manager import AgentManager
        am = AgentManager()
        print(f"\nAgents: {', '.join(am.list_agents())}")
    except Exception as e:
        print(f"  Error loading agents: {e}")
    
    # Check API
    print(f"\nAPI Endpoints:")
    print(f"  http://localhost:8000/docs")
    print(f"  http://localhost:8000/health")
    
    print("\n" + "=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="JCode v3.0 - OMO Governance Extension Layer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python jcode_start.py api                    # Start API on default port
    python jcode_start.py api --port 3000        # Start API on port 3000
    python jcode_start.py cli show               # Run CLI 'show' command
    python jcode_start.py mcp                    # Start MCP server
    python jcode_start.py status                 # Show status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # API command
    api_parser = subparsers.add_parser("api", help="Start the API server")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    api_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    
    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run CLI command")
    cli_parser.add_argument("args", nargs="*", help="CLI arguments")
    
    # MCP command
    subparsers.add_parser("mcp", help="Start MCP server")
    
    # Status command
    subparsers.add_parser("status", help="Show JCode status")
    
    args = parser.parse_args()
    
    if args.command == "api":
        start_api(port=args.port, host=args.host)
    elif args.command == "cli":
        run_cli(args.args)
    elif args.command == "mcp":
        start_mcp()
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
