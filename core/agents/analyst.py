"""
Analyst Agent - Problem Analysis (问题分析 - 司马迁)

Analyzes problems, identifies root causes, and proposes solutions.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent, AgentResult
from core.llm_client import LLMClient, LLMConfig


class AnalystAgent(BaseAgent):
    """
    Analyst Agent - Problem reconnaissance officer (司马迁)

    Responsibilities:
    - Analyze user requirements
    - Identify root causes
    - Assess risks
    - Propose solution approaches
    """

    name = "analyst"
    section = "[ANALYSIS]"
    description = "Problem reconnaissance officer - analyzes requirements and identifies solutions"

    SYSTEM_PROMPT = """你是 JCode 的分析师 Agent (司马迁)。

你的职责是：
1. 分析用户需求和问题描述
2. 识别问题的根本原因
3. 评估潜在风险
4. 提出解决方案建议

输出格式：
[ANALYSIS]
## 问题理解
(你对问题的理解)

## 根本原因
(识别的根本原因)

## 风险评估
(潜在风险和影响)

## 建议方案
(推荐的解决方法)

## 需要澄清的问题
(如果有不明确的地方)"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis."""
        problem_statement = input_data.get("problem_statement", "")
        context = input_data.get("context", {})

        # Build prompt
        user_message = f"请分析以下问题：\n\n{problem_statement}"

        if context:
            user_message += f"\n\n上下文信息：\n{self._format_context(context)}"

        # Get analysis from LLM
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message}
        ]

        analysis = self.chat(messages)

        return {
            "analysis": analysis,
            "problem_statement": problem_statement,
            "context": context
        }

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary as string."""
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)


def create_analyst_agent(
    project_root: str = ".",
    llm_client: Optional[LLMClient] = None
) -> AnalystAgent:
    """Create AnalystAgent instance."""
    return AnalystAgent(project_root=project_root, llm_client=llm_client)


__all__ = ["AnalystAgent", "create_analyst_agent"]
