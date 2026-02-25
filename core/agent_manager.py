"""
JCode Agent Manager - Pure Governance Layer

Manages the 6 JCode agents as governance controllers.
No LLM dependency - agents validate and govern, not generate.
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
    """JCode Agent Manager - Pure Governance Layer"""

    config_path: Optional[str] = None
    _iteration_count: int = field(default=0, init=False)
    _max_iterations: int = field(default=5, init=False)
    _agent_status: Dict[str, str] = field(init=False)
    _project_root: Path = field(init=False)
    _agents: Dict[str, Any] = field(init=False)

    def __post_init__(self):
        if self.config_path:
            self._project_root = Path(self.config_path).parent.parent
        else:
            self._project_root = Path.cwd()

        self._agent_status = {agent: "idle" for agent in ALL_AGENTS}
        self._agents = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all governance agents."""
        try:
            from core.agents import (
                AnalystAgent, PlannerAgent, ImplementerAgent,
                ReviewerAgent, TesterAgent, ConductorAgent
            )

            self._agents = {
                "analyst": AnalystAgent(str(self._project_root)),
                "planner": PlannerAgent(str(self._project_root)),
                "implementer": ImplementerAgent(str(self._project_root)),
                "reviewer": ReviewerAgent(str(self._project_root)),
                "tester": TesterAgent(str(self._project_root)),
                "conductor": ConductorAgent(str(self._project_root))
            }
        except ImportError:
            self._agents = {}

    def dispatch_agent(self, agent_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a governance agent."""
        if agent_type not in ALL_AGENTS:
            raise ValueError(f"Invalid agent_type: {agent_type}")

        self._agent_status[agent_type] = "running"

        if agent_type in self._agents:
            result = self._agents[agent_type].execute(input_data)
            self._agent_status[agent_type] = "completed" if result.success else "error"
            return {
                "section": result.section,
                "payload": result.output,
                "error": result.error,
                "action": result.action
            }
        else:
            self._agent_status[agent_type] = "error"
            return {
                "section": AGENT_SECTIONS.get(agent_type, "[OUTPUT]"),
                "payload": {},
                "error": "Agent not initialized",
                "action": "STOP"
            }

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

    @property
    def iteration_count(self) -> int:
        return self._iteration_count

    @property
    def max_iterations(self) -> int:
        return self._max_iterations


def create_agent_manager(config_path: Optional[str] = None) -> AgentManager:
    return AgentManager(config_path=config_path)


__all__ = ["AgentManager", "create_agent_manager", "ALL_AGENTS"]
