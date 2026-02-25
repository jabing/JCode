"""
JCode Base Agent - Governance Layer Foundation

Base class for all JCode governance agents.
JCode is an OMO extension layer - agents perform governance, not execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from core.switch_manager import SwitchManager, create_switch_manager
from core.audit_logger import AuditLogger, create_audit_logger


@dataclass
class AgentResult:
    """Result of agent governance check."""
    agent: str
    section: str
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    action: Optional[str] = None  # CONTINUE, STOP, HUMAN_INTERVENTION
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all JCode governance agents.
    
    JCode agents are governance controllers, not executors.
    They validate, check, verify, and record - but don't generate content.
    
    Responsibilities:
    - Check if agent is enabled via switch
    - Validate input data format
    - Apply governance rules
    - Record audit logs
    - Return governance decisions
    """
    
    name: str = "base"
    section: str = "[BASE]"
    description: str = "Base governance agent"
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.switch = create_switch_manager()
        self.audit = create_audit_logger()
    
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute agent governance logic.
        
        Workflow:
        1. Check if agent is enabled
        2. Validate input format
        3. Run governance logic
        4. Record audit log
        5. Return result
        """
        try:
            # Step 1: Check switch
            if not self._check_enabled():
                return AgentResult(
                    agent=self.name,
                    section=self.section,
                    success=False,
                    output={},
                    error="Agent disabled by switch",
                    action="STOP"
                )
            
            # Step 2: Validate input
            validation_error = self._validate_input(input_data)
            if validation_error:
                return AgentResult(
                    agent=self.name,
                    section=self.section,
                    success=False,
                    output={},
                    error=validation_error,
                    action="STOP"
                )
            
            # Step 3: Run governance logic
            output = self._run(input_data)
            
            # Step 4: Record audit
            self._record_audit(input_data, output)
            
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
                error=str(e),
                action="HUMAN_INTERVENTION"
            )
    
    def _check_enabled(self) -> bool:
        """Check if this agent is enabled via switch."""
        try:
            return self.switch.get("agent", self.name)
        except:
            return True  # Default to enabled
    
    def _validate_input(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Validate input format. Override in subclasses."""
        if not isinstance(input_data, dict):
            return "Input must be a dictionary"
        return None
    
    def _record_audit(self, input_data: Dict[str, Any], output: Dict[str, Any]) -> None:
        """Record audit log entry."""
        self.audit.write_log(
            actor_type="agent",
            actor_id=self.name,
            action_type=self.section.replace("[", "").replace("]", ""),
            context={"input_keys": list(input_data.keys())},
            details={"output_keys": list(output.keys()) if output else []}
        )
    
    @abstractmethod
    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal governance logic. Must be implemented by subclasses.
        
        Args:
            input_data: Input data from OMO or caller
            
        Returns:
            Governance decision output
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


__all__ = ["BaseAgent", "AgentResult"]
