"""
JCode Base Agent - Foundation class for all Agents

Provides common functionality for all JCode agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

from core.llm_client import LLMClient, LLMConfig, create_llm_client
from core.tools.file_tools import FileTools, create_file_tools
from core.tools.command_tools import CommandTools, create_command_tools
from core.tools.git_tools import GitTools, create_git_tools


@dataclass
class AgentResult:
    """Result of agent execution."""
    agent: str
    section: str
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all JCode agents.

    Provides:
    - LLM client for AI interactions
    - File tools for file operations
    - Command tools for shell commands
    - Git tools for version control
    """

    # Subclasses must define these
    name: str = "base"
    section: str = "[BASE]"
    description: str = "Base agent class"

    def __init__(
        self,
        project_root: str = ".",
        llm_client: Optional[LLMClient] = None,
        llm_config: Optional[LLMConfig] = None
    ):
        self.project_root = Path(project_root).resolve()

        # Initialize LLM client
        self.llm = llm_client or create_llm_client(llm_config)

        # Initialize tools
        self.files = create_file_tools(project_root)
        self.commands = create_command_tools(project_root)
        self.git = create_git_tools(project_root)

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute agent logic.

        Args:
            input_data: Input data for the agent

        Returns:
            AgentResult with output and status
        """
        try:
            output = self._run(input_data)
            return AgentResult(
                agent=self.name,
                section=self.section,
                success=True,
                output=output
            )
        except Exception as e:
            return AgentResult(
                agent=self.name,
                section=self.section,
                success=False,
                output={},
                error=str(e)
            )

    @abstractmethod
    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal execution logic. Must be implemented by subclasses.

        Args:
            input_data: Input data for the agent

        Returns:
            Output dictionary
        """
        pass

    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        return f"You are the {self.name} agent. {self.description}"

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages to LLM and get response."""
        if not self.llm.is_available():
            raise RuntimeError("LLM client not available. Check API key configuration.")

        return self.llm.chat(messages)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, project_root={self.project_root})"


__all__ = ["BaseAgent", "AgentResult"]
