"""Implementer Agent - Governance Layer (代码实现治理 - 鲁班)

Validates code implementation and applies governance rules.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent


class ImplementerAgent(BaseAgent):
    """Implementer Governance Agent (鲁班)"""

    name = "implementer"
    section = "[IMPLEMENTATION]"
    description = "Code implementation governance - validates code changes"

    def _validate_input(self, input_data: Dict[str, Any]) -> Optional[str]:
        if not input_data:
            return "Input data is required"
        return None

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "section": self.section,
            "checks": [],
            "warnings": [],
            "action": "CONTINUE"
        }

        implementation = input_data.get("implementation", "")
        files_changed = input_data.get("files_changed", [])

        # Check 1: Implementation exists
        if implementation:
            result["checks"].append({"name": "implementation_exists", "status": "PASS"})
        else:
            result["warnings"].append("No implementation provided")

        # Check 2: Files changed list
        if files_changed:
            result["checks"].append({
                "name": "files_changed",
                "status": "PASS",
                "count": len(files_changed)
            })

        # Check 3: No forbidden patterns
        forbidden = ["password", "secret", "api_key", "token"]
        found_forbidden = []
        if implementation:
            impl_lower = implementation.lower()
            for pattern in forbidden:
                if pattern in impl_lower:
                    found_forbidden.append(pattern)

        if found_forbidden:
            result["warnings"].append(f"Potential sensitive data: {found_forbidden}")
            result["action"] = "HUMAN_INTERVENTION"

        result["checks"].append({
            "name": "sensitive_data_check",
            "status": "PASS" if not found_forbidden else "WARNING"
        })

        return result


def create_implementer_agent(project_root: str = ".") -> ImplementerAgent:
    return ImplementerAgent(project_root=project_root)


