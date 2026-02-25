"""
JCode Agent Manager - Agent Dispatch and Lifecycle Management

Manages the 6 JCode agents (analyst, planner, implementer, reviewer, tester, conductor).
Handles agent dispatch, status tracking, and iteration management.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

ALL_AGENTS = ["analyst", "planner", "implementer", "reviewer", "tester", "conductor"]

AGENT_SECTIONS = {
    "analyst": "[ANALYSIS]",
    "planner": "[TASKS]",
    "implementer": "[IMPLEMENTATION]",
    "reviewer": "[REVIEW]",
    "tester": "[TEST]",
    "conductor": "[FINAL]"
}

@dataclass
class AgentManager:
    config_path: Optional[str] = None
    _iteration_count: int = field(default=0, init=False)
    _max_iterations: int = field(default=5, init=False)
    _agent_status: Dict[str, str] = field(init=False)
    _project_root: Path = field(init=False)

    def __post_init__(self):
        if self.config_path:
            self._project_root = Path(self.config_path).parent.parent
        else:
            self._project_root = Path.cwd()
        self._agent_status = {agent: "idle" for agent in ALL_AGENTS}

    def dispatch_agent(self, agent_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if agent_type not in ALL_AGENTS:
            raise ValueError(f"Invalid agent_type: {agent_type}")
        self._agent_status[agent_type] = "running"
        output = self._mock_dispatch(agent_type, input_data)
        self._agent_status[agent_type] = "completed"
        return output

    def get_agent_status(self, agent_type: str) -> str:
        if agent_type not in ALL_AGENTS:
            raise ValueError(f"Invalid agent_type: {agent_type}")
        return self._agent_status.get(agent_type, "idle")

    def list_agents(self) -> List[str]:
        return ALL_AGENTS.copy()

    def start_iteration(self) -> None:
        self._iteration_count += 1

    def check_iteration_count(self) -> bool:
        return self._iteration_count < self._max_iterations

    def reset_iterations(self) -> None:
        self._iteration_count = 0

    def _mock_dispatch(self, agent_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "section": AGENT_SECTIONS.get(agent_type, "[OUTPUT]"),
            "payload": {"agent": agent_type, "input": input_data, "status": "mock"}
        }

    @property
    def iteration_count(self) -> int:
        return self._iteration_count

    @property
    def max_iterations(self) -> int:
        return self._max_iterations

def create_agent_manager(config_path: Optional[str] = None) -> AgentManager:
    return AgentManager(config_path=config_path)

__all__ = ["AgentManager", "create_agent_manager", "ALL_AGENTS"]
