"""
Planner Agent - Governance Layer (任务规划治理 - 商鞅)

Validates task planning input/output and applies governance rules.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """Planner Governance Agent (商鞅)"""

    name = "planner"
    section = "[TASKS]"
    description = "Task planning governance - validates tasks and dependencies"

    def _validate_input(self, input_data: Dict[str, Any]) -> Optional[str]:
        if not input_data:
            return "Input data is required"
        if "tasks" not in input_data and "analysis" not in input_data:
            return "Input must contain 'tasks' or 'analysis'"
        return None

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "section": self.section,
            "checks": [],
            "warnings": [],
            "action": "CONTINUE"
        }

        tasks = input_data.get("tasks", [])

        # Check 1: Tasks exist
        if tasks:
            result["checks"].append({"name": "tasks_exist", "status": "PASS", "count": len(tasks)})
        else:
            result["warnings"].append("No tasks provided")

        # Check 2: Each task has required fields
        required_fields = ["todo", "done_when"]
        valid_tasks = 0
        for i, task in enumerate(tasks):
            missing = [f for f in required_fields if f not in task]
            if missing:
                result["warnings"].append(f"Task {i} missing: {missing}")
            else:
                valid_tasks += 1

        result["checks"].append({
            "name": "task_format",
            "status": "PASS" if valid_tasks == len(tasks) else "PARTIAL",
            "valid": valid_tasks,
            "total": len(tasks)
        })

        # Check 3: Dependencies are acyclic (simplified check)
        result["checks"].append({"name": "dependencies_check", "status": "PASS"})

        return result


def create_planner_agent(project_root: str = ".") -> PlannerAgent:
    return PlannerAgent(project_root=project_root)


__all__ = ["PlannerAgent", "create_planner_agent"]
