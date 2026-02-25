"""
Tester Agent - Testing & Validation (证据验证 - 张衡)

Validates implementations through testing.
"""

from typing import Dict, Any, Optional
from core.base_agent import BaseAgent
from core.llm_client import LLMClient


class TesterAgent(BaseAgent):
    """Tester Agent - Evidence officer (张衡)"""

    name = "tester"
    section = "[TEST]"
    description = "Evidence officer - validates implementations through testing"

    SYSTEM_PROMPT = """你是 JCode 的测试员 Agent (张衡)。

你的职责是：
1. 设计测试用例
2. 验证功能正确性
3. 检查边界情况
4. 做出 PASSED 或 FAILED 决定

输出格式：
[TEST]
## 测试结果
PASSED / FAILED

## 测试用例
(执行的测试)

## 测试输出
(实际输出)

## 问题列表
(发现的问题，如果没有则为空)

## 结论
(最终判断)"""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        implementation = input_data.get("implementation", "")
        tasks = input_data.get("tasks", "")
        run_actual_tests = input_data.get("run_tests", False)

        test_results = ""

        # Optionally run actual tests
        if run_actual_tests:
            result = self.commands.run_tests()
            test_results = f"\n实际测试结果：\n{result.stdout}\n{result.stderr}"

        user_message = f"验证以下实现：\n\n任务：\n{tasks}\n\n实现：\n{implementation}{test_results}"

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message}
        ]

        test_output = self.chat(messages)
        passed = "PASSED" in test_output.upper()

        return {
            "test_output": test_output,
            "passed": passed
        }


def create_tester_agent(project_root: str = ".", llm_client: Optional[LLMClient] = None) -> TesterAgent:
    return TesterAgent(project_root=project_root, llm_client=llm_client)


__all__ = ["TesterAgent", "create_tester_agent"]
