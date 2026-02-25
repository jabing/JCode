# Agent 实际实现计划

## TL;DR
> 实现 JCode 6 个 Agent 的实际功能，集成智谱 GLM-5 模型，
> 支持代码读取、编写、命令执行、Git 操作。

## 技术方案

### AI 模型
- 模型: 智谱 GLM-5 (zhipuai-coding-plan/glm-5)
- SDK: zhipuai
- 配置: API Key 从环境变量读取

### Agent 架构
1. BaseAgent - 基础 Agent 类
2. ToolSystem - 工具系统（文件、命令、Git）
3. PromptTemplates - 提示词模板
4. ContextManager - 上下文管理

### 工具系统
- FileTools: read_file, write_file, list_files
- CommandTools: run_command, run_tests
- GitTools: git_status, git_commit, git_diff

## 实施任务

### Wave 1: 基础架构
- [ ] 1. 创建 core/llm_client.py - LLM 客户端
- [ ] 2. 创建 core/tools/file_tools.py - 文件工具
- [ ] 3. 创建 core/tools/command_tools.py - 命令工具
- [ ] 4. 创建 core/tools/git_tools.py - Git 工具
- [ ] 5. 创建 core/base_agent.py - 基础 Agent 类

### Wave 2: Agent 实现
- [ ] 6. 实现 Analyst Agent - 问题分析
- [ ] 7. 实现 Planner Agent - 任务规划
- [ ] 8. 实现 Implementer Agent - 代码实现
- [ ] 9. 实现 Reviewer Agent - 代码审查
- [ ] 10. 实现 Tester Agent - 测试验证
- [ ] 11. 实现 Conductor Agent - 终局裁决

### Wave 3: 集成测试
- [ ] 12. 更新 AgentManager 集成实际 Agent
- [ ] 13. 更新 API 端点
- [ ] 14. 添加集成测试
- [ ] 15. 文档更新

## 依赖
- zhipuai (智谱 SDK)
- 已有的 core/ 模块

## 验证策略
- 每个 Agent 有独立测试
- 端到端工作流测试
