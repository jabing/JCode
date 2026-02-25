"""
JCode Command Tools - Shell command execution for Agents
"""

import subprocess
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    """Result of a command execution."""
    command: str
    return_code: int
    stdout: str
    stderr: str
    success: bool


class CommandTools:
    """
    Command execution tools for Agents.
    """
    
    def __init__(self, project_root: str = ".", timeout: int = 60):
        self.project_root = Path(project_root).resolve()
        self.timeout = timeout
    
    def run_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None
    ) -> CommandResult:
        """Run a shell command."""
        work_dir = self.project_root / (cwd or "")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=work_dir,
                timeout=timeout or self.timeout,
                env={**dict(subprocess.os.environ), **(env or {})}
            )
            return CommandResult(
                command=command,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                success=result.returncode == 0
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout or self.timeout} seconds",
                success=False
            )
        except Exception as e:
            return CommandResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                success=False
            )
    
    def run_tests(self, test_path: str = "tests/") -> CommandResult:
        """Run pytest tests."""
        command = f"python -m pytest {test_path} -v"
        return self.run_command(command, timeout=120)
    
    def install_dependencies(self) -> CommandResult:
        """Install project dependencies."""
        command = "pip install -r requirements.txt"
        return self.run_command(command, timeout=300)


def create_command_tools(project_root: str = ".") -> CommandTools:
    """Create CommandTools instance."""
    return CommandTools(project_root=project_root)


__all__ = ["CommandTools", "CommandResult", "create_command_tools"]
