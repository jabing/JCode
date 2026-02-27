#!/usr/bin/env python
"""
JCode VSCode Configuration Script
Automatically configures VSCode for JCode MCP integration.

Usage:
    python configure_vscode.py [--global] [--project] [--check] [--uninstall]
    
Options:
    --global    Configure global VSCode settings (user-level)
    --project   Configure project-level VSCode settings (.vscode/)
    --check     Check current configuration status
    --uninstall Remove JCode configuration from VSCode
"""

import json
import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any, Optional


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")


def print_error(message: str):
    print(f"{Colors.RED}✗{Colors.RESET} {message}")


def print_info(message: str):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")


def print_step(step: int, message: str):
    print(f"\n{Colors.CYAN}[{step}]{Colors.RESET} {Colors.BOLD}{message}{Colors.RESET}")


class VSCodeConfigurator:
    """Configures VSCode for JCode MCP integration."""
    
    def __init__(self, jcode_path: Optional[str] = None):
        self.jcode_path = Path(jcode_path).resolve() if jcode_path else Path(__file__).parent.parent.resolve()
        self.home = Path.home()
        
        # VSCode paths
        self.vscode_user_settings = self.home / ".vscode" / "settings.json"
        self.vscode_global_mcp = self.home / ".vscode" / "mcp.json"
        
        # Project paths (will be set based on current directory)
        self.project_dir = Path.cwd()
        self.project_vscode = self.project_dir / ".vscode"
        self.project_settings = self.project_vscode / "settings.json"
        self.project_mcp = self.project_vscode / "mcp.json"
        self.project_tasks = self.project_vscode / "tasks.json"
        self.project_snippets = self.project_vscode / "jcode.code-snippets"
        
        # JCode paths
        self.python_exe = self._find_python()
        self.jcode_abs_path = str(self.jcode_path).replace("\\", "/")
        
    def _find_python(self) -> str:
        """Find Python executable."""
        if sys.platform == "win32":
            candidates = ["python", "python3", "python.exe", "python3.exe"]
        else:
            candidates = ["python3", "python"]
        
        for candidate in candidates:
            try:
                result = os.popen(f"{candidate} --version 2>&1").read()
                if "Python" in result:
                    return candidate
            except:
                continue
        
        return sys.executable
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file or return empty dict."""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print_warning(f"Invalid JSON in {path}, creating backup")
                backup = path.with_suffix('.json.bak')
                shutil.copy(path, backup)
                print_info(f"Backup created: {backup}")
        return {}
    
    def _save_json(self, path: Path, data: Dict[str, Any]):
        """Save JSON file with proper formatting."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
    
    def _get_mcp_config(self) -> Dict[str, Any]:
        """Get JCode MCP server configuration."""
        return {
            "jcode": {
                "type": "local",
                "command": self.python_exe,
                "args": ["-m", "mcp.server", "--port", "8080"],
                "cwd": self.jcode_abs_path,
                "env": {
                    "PYTHONPATH": self.jcode_abs_path
                }
            }
        }
    
    def _get_vscode_settings(self) -> Dict[str, Any]:
        """Get VSCode settings for JCode."""
        return {
            "mcp.enabled": True,
            "mcp.servers": self._get_mcp_config(),
            "mcp.autoStart": True,
            "mcp.logLevel": "info"
        }
    
    def _get_tasks_config(self) -> Dict[str, Any]:
        """Get VSCode tasks configuration for JCode."""
        return {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "JCode: Start MCP Server",
                    "type": "shell",
                    "command": f"{self.python_exe} -m mcp.server --port 8080",
                    "options": {
                        "cwd": self.jcode_abs_path,
                        "env": {
                            "PYTHONPATH": self.jcode_abs_path
                        }
                    },
                    "isBackground": True,
                    "problemMatcher": [],
                    "presentation": {
                        "reveal": "never",
                        "panel": "new"
                    },
                    "group": {
                        "kind": "build",
                        "isDefault": False
                    }
                },
                {
                    "label": "JCode: Stop MCP Server",
                    "type": "shell",
                    "command": "taskkill /F /FI \"WINDOWTITLE eq python*\" /FI \"IMAGENAME eq python.exe\" 2>nul || pkill -f \"mcp.server\"",
                    "windows": {
                        "command": "taskkill /F /FI \"WINDOWTITLE eq python*\" /FI \"IMAGENAME eq python.exe\" 2>nul || echo \"Server stopped\""
                    },
                    "linux": {
                        "command": "pkill -f \"mcp.server\" || echo \"Server stopped\""
                    },
                    "osx": {
                        "command": "pkill -f \"mcp.server\" || echo \"Server stopped\""
                    },
                    "problemMatcher": []
                },
                {
                    "label": "JCode: Analyze Selection",
                    "type": "shell",
                    "command": f"curl -X POST http://localhost:8080/mcp -H \"Content-Type: application/json\" -d \"{{\\\"jsonrpc\\\":\\\"2.0\\\",\\\"id\\\":1,\\\"method\\\":\\\"tools/call\\\",\\\"params\\\":{{\\\"name\\\":\\\"analyze\\\",\\\"arguments\\\":{{\\\"input_data\\\":{{\\\"problem_statement\\\":\\\"${{selectedText}}\\\"}}}}}}}}\"",
                    "presentation": {
                        "reveal": "always",
                        "panel": "new"
                    },
                    "problemMatcher": []
                },
                {
                    "label": "JCode: Review Selection",
                    "type": "shell",
                    "command": f"curl -X POST http://localhost:8080/mcp -H \"Content-Type: application/json\" -d \"{{\\\"jsonrpc\\\":\\\"2.0\\\",\\\"id\\\":1,\\\"method\\\":\\\"tools/call\\\",\\\"params\\\":{{\\\"name\\\":\\\"review\\\",\\\"arguments\\\":{{\\\"input_data\\\":{{\\\"code\\\":\\\"${{selectedText}}\\\"}}}}}}}}\"",
                    "presentation": {
                        "reveal": "always",
                        "panel": "new"
                    },
                    "problemMatcher": []
                }
            ]
        }
    
    def _get_snippets(self) -> Dict[str, Any]:
        """Get VSCode code snippets for JCode."""
        return {
            "JCode MCP Analyze": {
                "prefix": "jcode-analyze",
                "body": [
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{",
                    "    \"jsonrpc\": \"2.0\",",
                    "    \"id\": 1,",
                    "    \"method\": \"tools/call\",",
                    "    \"params\": {",
                    "      \"name\": \"analyze\",",
                    "      \"arguments\": {",
                    "        \"input_data\": {",
                    "          \"problem_statement\": \"${1:Describe your requirement}\"",
                    "        }",
                    "      }",
                    "    }",
                    "  }'"
                ],
                "description": "Call JCode Analyst via MCP"
            },
            "JCode MCP Plan": {
                "prefix": "jcode-plan",
                "body": [
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{",
                    "    \"jsonrpc\": \"2.0\",",
                    "    \"id\": 1,",
                    "    \"method\": \"tools/call\",",
                    "    \"params\": {",
                    "      \"name\": \"plan\",",
                    "      \"arguments\": {",
                    "        \"input_data\": {",
                    "          \"analysis_result\": ${1:{}}",
                    "        }",
                    "      }",
                    "    }",
                    "  }'"
                ],
                "description": "Call JCode Planner via MCP"
            },
            "JCode MCP Review": {
                "prefix": "jcode-review",
                "body": [
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{",
                    "    \"jsonrpc\": \"2.0\",",
                    "    \"id\": 1,",
                    "    \"method\": \"tools/call\",",
                    "    \"params\": {",
                    "      \"name\": \"review\",",
                    "      \"arguments\": {",
                    "        \"input_data\": {",
                    "          \"code\": \"${1:code to review}\",",
                    "          \"requirements\": []",
                    "        }",
                    "      }",
                    "    }",
                    "  }'"
                ],
                "description": "Call JCode Reviewer via MCP"
            },
            "JCode MCP Test": {
                "prefix": "jcode-test",
                "body": [
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{",
                    "    \"jsonrpc\": \"2.0\",",
                    "    \"id\": 1,",
                    "    \"method\": \"tools/call\",",
                    "    \"params\": {",
                    "      \"name\": \"test\",",
                    "      \"arguments\": {",
                    "        \"input_data\": {",
                    "          \"verify_by\": [\"${1:test command}\"],",
                    "          \"implementation\": {}",
                    "        }",
                    "      }",
                    "    }",
                    "  }'"
                ],
                "description": "Call JCode Tester via MCP"
            },
            "JCode MCP Conductor": {
                "prefix": "jcode-conductor",
                "body": [
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{",
                    "    \"jsonrpc\": \"2.0\",",
                    "    \"id\": 1,",
                    "    \"method\": \"tools/call\",",
                    "    \"params\": {",
                    "      \"name\": \"conductor\",",
                    "      \"arguments\": {",
                    "        \"input_data\": {",
                    "          \"review_result\": \"${1:APPROVED}\",",
                    "          \"test_result\": \"${2:FAILED}\",",
                    "          \"iteration\": 1",
                    "        }",
                    "      }",
                    "    }",
                    "  }'"
                ],
                "description": "Call JCode Conductor via MCP"
            },
            "JCode Full Workflow": {
                "prefix": "jcode-full",
                "body": [
                    "# JCode Full Governance Workflow",
                    "# 1. Analyze",
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"analyze\",\"arguments\":{\"input_data\":{\"problem_statement\":\"${1:requirement}\"}}}}'",
                    "",
                    "# 2. Plan (use analysis result from step 1)",
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{\"name\":\"plan\",\"arguments\":{\"input_data\":{\"analysis_result\":{}}}}}'",
                    "",
                    "# 3. Implement",
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{\"name\":\"implement\",\"arguments\":{\"input_data\":{\"tasks\":[]}}}}'",
                    "",
                    "# 4. Review",
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"tools/call\",\"params\":{\"name\":\"review\",\"arguments\":{\"input_data\":{\"tasks\":[],\"implementation\":{}}}}}'",
                    "",
                    "# 5. Test",
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{\"jsonrpc\":\"2.0\",\"id\":5,\"method\":\"tools/call\",\"params\":{\"name\":\"test\",\"arguments\":{\"input_data\":{\"verify_by\":[],\"implementation\":{}}}}}'",
                    "",
                    "# 6. Conductor",
                    "curl -X POST http://localhost:8080/mcp \\",
                    "  -H \"Content-Type: application/json\" \\",
                    "  -d '{\"jsonrpc\":\"2.0\",\"id\":6,\"method\":\"tools/call\",\"params\":{\"name\":\"conductor\",\"arguments\":{\"input_data\":{\"review_result\":\"APPROVED\",\"test_result\":\"PASSED\",\"iteration\":1}}}}'"
                ],
                "description": "Complete JCode 6-step governance workflow"
            }
        }
    
    def check_global_config(self) -> Dict[str, bool]:
        """Check global VSCode configuration."""
        result = {
            "settings_exists": False,
            "mcp_configured": False,
            "jcode_enabled": False
        }
        
        if self.vscode_user_settings.exists():
            result["settings_exists"] = True
            settings = self._load_json(self.vscode_user_settings)
            
            if "mcp.servers" in settings or "mcp" in settings:
                result["mcp_configured"] = True
            
            if "mcp.servers" in settings and "jcode" in settings.get("mcp.servers", {}):
                result["jcode_enabled"] = True
        
        return result
    
    def check_project_config(self) -> Dict[str, bool]:
        """Check project-level VSCode configuration."""
        result = {
            "vscode_folder_exists": self.project_vscode.exists(),
            "settings_exists": False,
            "mcp_configured": False,
            "jcode_enabled": False,
            "tasks_configured": False,
            "snippets_configured": False
        }
        
        if self.project_settings.exists():
            result["settings_exists"] = True
            settings = self._load_json(self.project_settings)
            
            if "mcp" in str(settings):
                result["mcp_configured"] = True
            
            if "jcode" in str(settings):
                result["jcode_enabled"] = True
        
        if self.project_tasks.exists():
            tasks = self._load_json(self.project_tasks)
            if "JCode" in str(tasks):
                result["tasks_configured"] = True
        
        if self.project_snippets.exists():
            snippets = self._load_json(self.project_snippets)
            if "JCode" in str(snippets):
                result["snippets_configured"] = True
        
        return result
    
    def configure_global(self) -> bool:
        """Configure global VSCode settings."""
        print_step(1, "Configuring global VSCode settings")
        
        try:
            # Load existing settings
            settings = self._load_json(self.vscode_user_settings)
            
            # Add JCode MCP configuration
            if "mcp.servers" not in settings:
                settings["mcp.servers"] = {}
            
            settings["mcp.servers"].update(self._get_mcp_config())
            settings["mcp.enabled"] = True
            settings["mcp.autoStart"] = True
            
            # Save settings
            self._save_json(self.vscode_user_settings, settings)
            print_success(f"Updated: {self.vscode_user_settings}")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to configure global settings: {e}")
            return False
    
    def configure_project(self) -> bool:
        """Configure project-level VSCode settings."""
        print_step(1, "Configuring project VSCode settings")
        
        try:
            # Create .vscode directory
            self.project_vscode.mkdir(parents=True, exist_ok=True)
            print_success(f"Created: {self.project_vscode}")
            
            # Configure settings.json
            settings = self._load_json(self.project_settings)
            settings.update(self._get_vscode_settings())
            self._save_json(self.project_settings, settings)
            print_success(f"Created: {self.project_settings}")
            
            # Configure tasks.json
            tasks = self._get_tasks_config()
            self._save_json(self.project_tasks, tasks)
            print_success(f"Created: {self.project_tasks}")
            
            # Configure snippets
            snippets = self._get_snippets()
            self._save_json(self.project_snippets, snippets)
            print_success(f"Created: {self.project_snippets}")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to configure project settings: {e}")
            return False
    
    def uninstall_global(self) -> bool:
        """Remove JCode configuration from global VSCode settings."""
        print_step(1, "Removing global JCode configuration")
        
        try:
            if not self.vscode_user_settings.exists():
                print_warning("Global settings file not found")
                return True
            
            settings = self._load_json(self.vscode_user_settings)
            
            # Remove JCode from MCP servers
            if "mcp.servers" in settings and "jcode" in settings["mcp.servers"]:
                del settings["mcp.servers"]["jcode"]
                self._save_json(self.vscode_user_settings, settings)
                print_success("Removed JCode from global MCP servers")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to uninstall: {e}")
            return False
    
    def uninstall_project(self) -> bool:
        """Remove JCode configuration from project."""
        print_step(1, "Removing project JCode configuration")
        
        files_to_remove = [
            self.project_snippets,
            self.project_tasks
        ]
        
        for file_path in files_to_remove:
            if file_path.exists():
                file_path.unlink()
                print_success(f"Removed: {file_path}")
        
        # Clean up settings.json
        if self.project_settings.exists():
            settings = self._load_json(self.project_settings)
            
            # Remove JCode-specific settings
            keys_to_remove = ["mcp.servers", "mcp.enabled", "mcp.autoStart"]
            for key in keys_to_remove:
                if key in settings:
                    del settings[key]
            
            self._save_json(self.project_settings, settings)
            print_success(f"Cleaned: {self.project_settings}")
        
        return True
    
    def print_status(self):
        """Print configuration status."""
        print("\n" + "="*60)
        print(f"{Colors.BOLD}JCode VSCode Configuration Status{Colors.RESET}")
        print("="*60)
        
        # Global config
        print(f"\n{Colors.CYAN}Global Configuration:{Colors.RESET}")
        global_status = self.check_global_config()
        
        if global_status["settings_exists"]:
            print_success("VSCode settings file exists")
        else:
            print_warning("VSCode settings file not found")
        
        if global_status["jcode_enabled"]:
            print_success("JCode MCP configured globally")
        else:
            print_warning("JCode MCP not configured globally")
        
        # Project config
        print(f"\n{Colors.CYAN}Project Configuration ({self.project_dir}):{Colors.RESET}")
        project_status = self.check_project_config()
        
        checks = [
            ("vscode_folder_exists", ".vscode folder exists"),
            ("settings_exists", "settings.json exists"),
            ("jcode_enabled", "JCode MCP configured"),
            ("tasks_configured", "JCode tasks configured"),
            ("snippets_configured", "JCode snippets configured")
        ]
        
        for key, label in checks:
            if project_status.get(key, False):
                print_success(label)
            else:
                print_warning(label)
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Configure VSCode for JCode MCP integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python configure_vscode.py --check           Check current configuration
  python configure_vscode.py --project         Configure project-level settings
  python configure_vscode.py --global          Configure global user settings
  python configure_vscode.py --uninstall       Remove JCode configuration
  python configure_vscode.py -g -p             Configure both global and project
        """
    )
    
    parser.add_argument("-g", "--global-config", dest="global_config", action="store_true",
                       help="Configure global VSCode settings (user-level)")
    parser.add_argument("-p", "--project", action="store_true",
                       help="Configure project-level VSCode settings")
    parser.add_argument("-c", "--check", action="store_true",
                       help="Check current configuration status")
    parser.add_argument("-u", "--uninstall", action="store_true",
                       help="Remove JCode configuration from VSCode")
    parser.add_argument("--jcode-path", type=str,
                       help="Path to JCode installation (default: auto-detect)")
    
    args = parser.parse_args()
    
    # Default to project config if no option specified
    if not any([args.global_config, args.project, args.check, args.uninstall]):
        args.project = True
    
    # Create configurator
    configurator = VSCodeConfigurator(jcode_path=args.jcode_path)
    
    print(f"\n{Colors.BOLD}JCode VSCode Configuration Tool{Colors.RESET}")
    print(f"JCode Path: {configurator.jcode_path}")
    print(f"Python: {configurator.python_exe}")
    print(f"Project: {configurator.project_dir}")
    
    # Check mode
    if args.check:
        configurator.print_status()
        return 0
    
    # Uninstall mode
    if args.uninstall:
        success = True
        if args.global_config:
            success = configurator.uninstall_global() and success
        if args.project or not args.global_config:
            success = configurator.uninstall_project() and success
        
        if success:
            print_success("JCode configuration removed successfully")
            return 0
        else:
            print_error("Uninstallation failed")
            return 1
    
    # Install mode
    success = True
    
    if args.global_config:
        success = configurator.configure_global() and success
    
    if args.project or not args.global_config:
        success = configurator.configure_project() and success
    
    if success:
        print("\n" + "="*60)
        print_success("VSCode configured successfully!")
        print("="*60)
        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print("1. Restart VSCode if it's currently open")
        print("2. Open the Command Palette (Ctrl+Shift+P)")
        print("3. Search for 'MCP' to see available commands")
        print("4. Run task: 'JCode: Start MCP Server' (Ctrl+Shift+B)")
        print("5. Use snippets: type 'jcode-' to see available snippets")
        print(f"\n{Colors.CYAN}Quick Start:{Colors.RESET}")
        print(f"  Terminal: cd {configurator.jcode_path}")
        print(f"  Terminal: {configurator.python_exe} -m mcp.server --port 8080")
        print("="*60 + "\n")
        return 0
    else:
        print_error("Configuration failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
