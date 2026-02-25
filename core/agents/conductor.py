"""
Conductor Agent - Governance Layer (终局裁决治理 - 韩非子)

Makes final arbitration decisions based on all phase outputs.
Applies constitutional rules and determines workflow termination.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent


class ConductorAgent(BaseAgent):
    """Conductor Governance Agent (韩非子) - Final arbitration"""

    name = "conductor"
    section = "[FINAL]"
    description = "Final arbitration governance - makes workflow termination decisions"

    def _validate_input(self, input_data: Dict[str, Any]) -> Optional[str]:
        if not input_data:
            return "Input data is required"
        return None

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "section": self.section,
            "verdict": "SUCCESS",
            "checks": [],
            "workflow_summary": {},
            "action": "COMPLETE"
        }

        # Collect all phase results
        analysis = input_data.get("analysis", {})
        tasks = input_data.get("tasks", {})
        implementation = input_data.get("implementation", {})
        review = input_data.get("review", {})
        test = input_data.get("test", {})

        # Check 1: All phases present
        phases = {"analysis": analysis, "tasks": tasks, "implementation": implementation, "review": review, "test": test}
        for phase_name, phase_data in phases.items():
            if phase_data:
                result["checks"].append({"name": f"{phase_name}_present", "status": "PASS"})
            else:
                result["checks"].append({"name": f"{phase_name}_present", "status": "MISSING"})

        # Check 2: Review verdict
        review_verdict = review.get("verdict", "APPROVED") if isinstance(review, dict) else "APPROVED"
        if review_verdict == "REJECTED":
            result["verdict"] = "NEEDS_REVISION"
            result["action"] = "RETRY"
            result["workflow_summary"]["review_failed"] = True

        # Check 3: Test verdict
        test_verdict = test.get("verdict", "PASSED") if isinstance(test, dict) else "PASSED"
        if test_verdict == "FAILED":
            result["verdict"] = "NEEDS_REVISION"
            result["action"] = "RETRY"
            result["workflow_summary"]["test_failed"] = True

        # Check 4: Any STOP actions from previous phases
        for phase_name, phase_data in phases.items():
            if isinstance(phase_data, dict) and phase_data.get("action") == "STOP":
                result["verdict"] = "FAILED"
                result["action"] = "STOP"
                result["workflow_summary"]["stop_from"] = phase_name
                break

        # Final decision
        result["workflow_summary"]["all_phases"] = len([p for p in phases.values() if p])
        result["workflow_summary"]["ready_to_commit"] = result["verdict"] == "SUCCESS"

        return result


def create_conductor_agent(project_root: str = ".") -> ConductorAgent:
    return ConductorAgent(project_root=project_root)


__all__ = ["ConductorAgent", "create_conductor_agent"]
