"""
Planner Agent - Task Planning (任务规划 - 商鞅)

Breaks down problems into executable tasks.
"""

from typing import Dict, Any, Optional, List
from core.base_agent import BaseAgent
from core.llm_client import LLMClient


class PlannerAgent(BaseAgent):
    """Planner Agent - Law maker (商鞅)"""

    name = "planner"
    section = "[TASKS]"
    description = "Law maker - breaks down problems into executable tasks"

    SYSTEM_PROMPT = """你是 JCode 的规划师 Agent (商鞅)。

你的职责是：
1. 根据分析结果制定任务计划
2. 将任务分解为具体步骤
3. 确定任务优先级和依赖关系
4. 定义验收标准

输出格式：
[TASKS]
## 任务列表
1. [任务名称]
   - 描述: (具体要做什么)
   - 优先级: (高/中/低)
   - 依赖: (依赖哪些任务)
   - 验收标准: (如何验证完成)

## 执行顺序
(建议的执行顺序)

## 预计工作量
(预估时间/复杂度)"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        analysis = input_data.get("analysis", "")
        problem_statement = input_data.get("problem_statement", "")

        user_message = f"基于以下分析，制定任务计划：\n\n问题：{problem_statement}\n\n分析结果：\n{analysis}"

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message}
        ]

        tasks = self.chat(messages)

        return {
            "tasks": tasks,
            "analysis": analysis
        }


def create_planner_agent(project_root: str = ".", llm_client: Optional[LLMClient] = None) -> PlannerAgent:
    return PlannerAgent(project_root=project_root, llm_client=llm_client)


__all__ = ["PlannerAgent", "create_planner_agent"]
