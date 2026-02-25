"""
Reviewer Agent - Governance Layer (合规审查治理 - 包拯)

Validates code review results and applies constitutional rules.
Returns APPROVED or REJECTED decision.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    """Reviewer Governance Agent (包拯) - Binary judgment only"""

    name = "reviewer"
    section = "[REVIEW]"
    description = "Code review governance - validates review decision"

    def _validate_input(self, input_data: Dict[str, Any]) -> Optional[str]:
        if not input_data:
            return "Input data is required"
        return None

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "section": self.section,
            "verdict": "APPROVED",
            "checks": [],
            "issues": [],
            "action": "CONTINUE"
        }

        review = input_data.get("review", "")
        implementation = input_data.get("implementation", "")

        # Check 1: Review exists
        if review:
            result["checks"].append({"name": "review_exists", "status": "PASS"})

        # Check 2: Verdict extraction
        review_upper = review.upper() if review else ""
        if "REJECTED" in review_upper:
            result["verdict"] = "REJECTED"
            result["action"] = "STOP"
        elif "APPROVED" in review_upper:
            result["verdict"] = "APPROVED"
        else:
            # Default to APPROVED if no explicit verdict
            result["checks"].append({
                "name": "verdict_present",
                "status": "WARNING",
                "note": "No explicit verdict found, defaulting to APPROVED"
            })

        # Check 3: Constitutional rule R001 - no skip review
        if input_data.get("skip_review", False):
            result["verdict"] = "REJECTED"
            result["issues"].append("R001 violation: Cannot skip review")
            result["action"] = "STOP"

        return result


def create_reviewer_agent(project_root: str = ".") -> ReviewerAgent:
    return ReviewerAgent(project_root=project_root)


__all__ = ["ReviewerAgent", "create_reviewer_agent"]
