"""
JCode v3.0 - OMO Governance Extension Layer

A code governance system for OpenCode with 6-agent workflow
and 4-level switch mechanism.
"""

__version__ = "3.0.0"

# Import commonly used modules
from core.agent_manager import AgentManager, create_agent_manager
from core.switch_manager import SwitchManager, create_switch_manager

__all__ = [
    "__version__",
    "AgentManager",
    "create_agent_manager",
    "SwitchManager",
    "create_switch_manager",
]
