"""
Analyst Agent - Governance Layer (问题分析治理 - 司马迁)

Validates analysis input/output and applies governance rules.
Does NOT generate content - only validates and governs.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent, AgentResult

class AnalystAgent(BaseAgent):
    """
    Analyst Governance Agent (司马迁)

    Responsibilities (Governance only):
    - Validate problem statement format
    - Check verifiability classification
    - Apply constitutional rules
    - Record audit log
    """

    name = "analyst"
    section = "[ANALYSIS]"
    description = "Problem analysis governance - validates input and applies rules"

    def _validate_input(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Validate input format."""
        if not input_data:
            return "Input data is required"

        # Check for problem_statement or analysis result
        has_statement = "problem_statement" in input_data
        has_analysis = "analysis" in input_data

        if not has_statement and not has_analysis:
            return "Input must contain 'problem_statement' or 'analysis'"

        return None

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute governance logic."""
        result = {
            "section": self.section,
            "verifiability": "HARD",  # Default
            "checks": [],
            "warnings": [],
            "action": "CONTINUE"
        }

        # Check 1: Problem statement exists
        problem = input_data.get("problem_statement", "")
        if problem:
            result["checks"].append({
                "name": "problem_statement_exists",
                "status": "PASS"
            })
        else:
            result["checks"].append({
                "name": "problem_statement_exists",
                "status": "SKIP",
                "reason": "Using provided analysis"
            })

        # Check 2: Analysis result format (if provided)
        analysis = input_data.get("analysis", "")
        if analysis:
            result["checks"].append({
                "name": "analysis_format",
                "status": "PASS"
            })
            # Check for required sections
            required_sections = ["[ANALYSIS]", "## 问题理解", "## 风险"]
            missing = [s for s in required_sections if s not in analysis]
            if missing:
                result["warnings"].append(f"Missing sections: {missing}")

        # Check 3: Verifiability assessment
        verifiability = input_data.get("verifiability", "HARD")
        if verifiability not in ["HARD", "SOFT", "NON-VERIFIABLE"]:
            result["warnings"].append(f"Unknown verifiability: {verifiability}")
            verifiability = "SOFT"
        result["verifiability"] = verifiability

        # Check 4: NON-VERIFIABLE triggers human intervention
        if verifiability == "NON-VERIFIABLE":
            result["action"] = "HUMAN_INTERVENTION"
            result["warnings"].append("Problem is non-verifiable - human intervention required")

        # Check 5: NFRs present (if provided)
        nfrs = input_data.get("nfrs", {})
        if nfrs:
            result["checks"].append({
                "name": "nfrs_present",
                "status": "PASS",
                "count": len(nfrs)
            })

        return result


def create_analyst_agent(project_root: str = ".") -> AnalystAgent:
    """Create AnalystAgent instance."""
    return AnalystAgent(project_root=project_root)


__all__ = ["AnalystAgent", "create_analyst_agent"]
