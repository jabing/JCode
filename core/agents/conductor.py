"""
Conductor Agent - Final Arbitration (终局裁决 - 韩非子)

Makes final decisions and coordinates workflow.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent
from core.llm_client import LLMClient


class ConductorAgent(BaseAgent):
    """Conductor Agent - Final arbiter (韩非子)"""

    name = "conductor"
    section = "[FINAL]"
    description = "Final arbiter - makes final decisions and coordinates workflow"

    SYSTEM_PROMPT = """你是 JCode 的调度员 Agent (韩非子)。

你的职责是：
1. 审查所有 Agent 的输出
2. 做出最终决策
3. 协调工作流程
4. 处理冲突情况

输出格式：
[FINAL]
## 决策结果
SUCCESS / NEEDS_REVISION / FAILED

## 工作流摘要
(整个过程回顾)

## 最终结论
(最终判断)

## 后续行动
(如果有需要进一步处理的)

## 提交建议
(是否建议提交代码)"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        analysis = input_data.get("analysis", "")
        tasks = input_data.get("tasks", "")
        implementation = input_data.get("implementation", "")
        review = input_data.get("review", "")
        test_output = input_data.get("test_output", "")

        user_message = f"""审查完整工作流并做出最终决策：

## 分析结果
{analysis}

## 任务计划
{tasks}

## 实现
{implementation}

## 审查结果
{review}

## 测试结果
{test_output}

请做出最终决策。"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message}
        ]

        final_decision = self.chat(messages)
        success = "SUCCESS" in final_decision.upper()

        return {
            "final_decision": final_decision,
            "success": success
        }


def create_conductor_agent(project_root: str = ".", llm_client: Optional[LLMClient] = None) -> ConductorAgent:
    return ConductorAgent(project_root=project_root, llm_client=llm_client)


__all__ = ["ConductorAgent", "create_conductor_agent"]
