"""
Reviewer Agent - Code Review (合规审查 - 包拯)

Reviews code for quality, correctness, and compliance.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent
from core.llm_client import LLMClient


class ReviewerAgent(BaseAgent):
    """Reviewer Agent - Veto officer (包拯)"""

    name = "reviewer"
    section = "[REVIEW]"
    description = "Veto officer - reviews code for quality and compliance"

    SYSTEM_PROMPT = """你是 JCode 的审查员 Agent (包拯)。

你的职责是：
1. 审查代码质量
2. 检查是否符合规范
3. 识别潜在问题
4. 做出 APPROVED 或 REJECTED 决定

输出格式：
[REVIEW]
## 审查结果
APPROVED / REJECTED

## 代码质量
(评分和说明)

## 发现的问题
(问题列表，如果没有则为空)

## 改进建议
(建议列表)

## 结论
(最终判断和理由)"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        implementation = input_data.get("implementation", "")
        tasks = input_data.get("tasks", "")

        user_message = f"审查以下代码实现：\n\n任务：\n{tasks}\n\n实现：\n{implementation}"

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message}
        ]

        review = self.chat(messages)

        # Simple check for approval
        approved = "APPROVED" in review.upper()

        return {
            "review": review,
            "approved": approved
        }


def create_reviewer_agent(project_root: str = ".", llm_client: Optional[LLMClient] = None) -> ReviewerAgent:
    return ReviewerAgent(project_root=project_root, llm_client=llm_client)


__all__ = ["ReviewerAgent", "create_reviewer_agent"]
