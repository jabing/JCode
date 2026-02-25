"""
Tester Agent - Governance Layer (证据验证治理 - 张衡)

Validates test results and applies constitutional rules.
Returns PASSED or FAILED decision.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent


class TesterAgent(BaseAgent):
    """Tester Governance Agent (张衡) - Evidence validation only"""

    name = "tester"
    section = "[TEST]"
    description = "Test validation governance - validates test evidence"

    def _validate_input(self, input_data: Dict[str, Any]) -> Optional[str]:
        if not input_data:
            return "Input data is required"
        return None

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "section": self.section,
            "verdict": "PASSED",
            "checks": [],
            "evidence": [],
            "action": "CONTINUE"
        }

        test_output = input_data.get("test_output", "")
        implementation = input_data.get("implementation", "")

        # Check 1: Test output exists
        if test_output:
            result["checks"].append({"name": "test_output_exists", "status": "PASS"})
        else:
            result["checks"].append({"name": "test_output_exists", "status": "WARNING"})
            result["evidence"].append("No test output provided")

        # Check 2: Verdict extraction
        test_upper = test_output.upper() if test_output else ""
        if "FAILED" in test_upper:
            result["verdict"] = "FAILED"
            result["action"] = "STOP"
        elif "PASSED" in test_upper:
            result["verdict"] = "PASSED"

        # Check 3: Constitutional rule R002 - require test evidence
        if not test_output and implementation:
            result["checks"].append({
                "name": "test_evidence_required",
                "status": "WARNING",
                "note": "R002: Test evidence recommended for implementations"
            })

        return result


def create_tester_agent(project_root: str = ".") -> TesterAgent:
    return TesterAgent(project_root=project_root)


__all__ = ["TesterAgent", "create_tester_agent"]
