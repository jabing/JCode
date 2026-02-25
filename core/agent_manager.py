"""
JCode Agent Manager - Agent Dispatch and Lifecycle Management

Manages the 6 JCode agents (analyst, planner, implementer, reviewer, tester, conductor).
Integrates with actual agent implementations using LLM.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from core.llm_client import LLMClient, create_llm_client

# All JCode agents
ALL_AGENTS = [
    "analyst",
    "planner",
    "implementer",
    "reviewer",
    "tester",
    "conductor"
]

# Agent sections for output identification
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
    """JCode Agent Manager with actual agent implementations."""
    
    config_path: Optional[str] = None
    _iteration_count: int = field(default=0, init=False)
    _max_iterations: int = field(default=5, init=False)
    _agent_status: Dict[str, str] = field(init=False)
    _project_root: Path = field(init=False)
    _agents: Dict[str, Any] = field(init=False)
    _llm_client: Optional[LLMClient] = field(init=False)
    
    def __post_init__(self):
        if self.config_path:
            self._project_root = Path(self.config_path).parent.parent
        else:
            self._project_root = Path.cwd()
        
        self._agent_status = {agent: "idle" for agent in ALL_AGENTS}
        self._agents = {}
        self._llm_client = None
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agent instances."""
        try:
            from core.agents import (
                AnalystAgent, PlannerAgent, ImplementerAgent,
                ReviewerAgent, TesterAgent, ConductorAgent
            )
            
            self._llm_client = create_llm_client()
            
            self._agents = {
                "analyst": AnalystAgent(str(self._project_root), self._llm_client),
                "planner": PlannerAgent(str(self._project_root), self._llm_client),
                "implementer": ImplementerAgent(str(self._project_root), self._llm_client),
                "reviewer": ReviewerAgent(str(self._project_root), self._llm_client),
                "tester": TesterAgent(str(self._project_root), self._llm_client),
                "conductor": ConductorAgent(str(self._project_root), self._llm_client)
            }
        except ImportError:
            # Fall back to mock mode if agents not available
            self._agents = {}
    
    def dispatch_agent(self, agent_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch an agent with input data."""
        if agent_type not in ALL_AGENTS:
            raise ValueError(f"Invalid agent_type: {agent_type}")
        
        self._agent_status[agent_type] = "running"
        
        if agent_type in self._agents:
            # Use actual agent
            result = self._agents[agent_type].execute(input_data)
            self._agent_status[agent_type] = "completed" if result.success else "error"
            return {
                "section": result.section,
                "payload": result.output,
                "error": result.error
            }
        else:
            # Fall back to mock
            self._agent_status[agent_type] = "completed"
            return self._mock_dispatch(agent_type, input_data)
    
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
            "payload": {"agent": agent_type, "input": input_data, "status": "mock", "message": "LLM not configured"}
        }
    
    @property
    def iteration_count(self) -> int:
        return self._iteration_count
    
    @property
    def max_iterations(self) -> int:
        return self._max_iterations
    
    def is_llm_available(self) -> bool:
        """Check if LLM is available."""
        return self._llm_client is not None and self._llm_client.is_available()


def create_agent_manager(config_path: Optional[str] = None) -> AgentManager:
    return AgentManager(config_path=config_path)


__all__ = ["AgentManager", "create_agent_manager", "ALL_AGENTS"]
