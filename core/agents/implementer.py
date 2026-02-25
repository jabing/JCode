"""
Implementer Agent - Code Implementation (代码实现 - 鲁班)

Implements code based on task specifications.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent
from core.llm_client import LLMClient


class ImplementerAgent(BaseAgent):
    """Implementer Agent - Execution craftsman (鲁班)"""

    name = "implementer"
    section = "[IMPLEMENTATION]"
    description = "Execution craftsman - implements code based on specifications"

    SYSTEM_PROMPT = """你是 JCode 的实现者 Agent (鲁班)。

你的职责是：
1. 根据任务计划实现代码
2. 遵循项目代码规范
3. 编写清晰、可维护的代码
4. 处理边界情况和错误

输出格式：
[IMPLEMENTATION]
## 实现内容
(代码实现)

## 修改的文件
- 文件路径: (修改内容摘要)

## 注意事项
(需要特别注意的地方)"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        tasks = input_data.get("tasks", "")
        task_name = input_data.get("task_name", "")
        existing_code = input_data.get("existing_code", "")

        user_message = f"实现以下任务：\n\n任务：{task_name}\n\n任务计划：\n{tasks}"

        if existing_code:
            user_message += f"\n\n现有代码：\n{existing_code}"

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message}
        ]

        implementation = self.chat(messages)

        return {
            "implementation": implementation,
            "task_name": task_name
        }


def create_implementer_agent(project_root: str = ".", llm_client: Optional[LLMClient] = None) -> ImplementerAgent:
    return ImplementerAgent(project_root=project_root, llm_client=llm_client)


__all__ = ["ImplementerAgent", "create_implementer_agent"]
