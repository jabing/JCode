# JCode 与 OMO/OpenCode 集成指南

## 概述

JCode 通过 MCP (Model Context Protocol) 协议与 OMO 集成，为 OpenCode 提供 6 个治理工具。

## 架构

```
OpenCode (AI 编程助手)
    ↓ MCP
OMO (Oh-my-opencode)
    ├── Context Lock
    ├── Rule Engine
    ├── LLM Client
    └── JCode MCP Server (治理工具)
        ├── jcode.analyze
        ├── jcode.plan
        ├── jcode.implement
        ├── jcode.review
        ├── jcode.test
        └── jcode.conductor
```

## 步骤 1: 安装 JCode

```bash
cd C:\dev_projects\jcode
pip install -r requirements.txt
```

## 步骤 2: 配置 OMO

在 OMO 配置文件中添加 JCode MCP 服务器：

**~/.omo/config.yaml** (或 OMO 配置位置):
```yaml
mcp_servers:
  jcode:
    command: python
    args:
      - C:\dev_projects\jcode\mcp\jcode_server.py
    enabled: true
```

## 步骤 3: 在 OpenCode 中使用

当 OMO 加载 JCode 后，OpenCode 可以调用以下工具：

### 工具列表

| 工具名 | 功能 | 输入 | 输出 |
|--------|------|------|------|
| jcode.analyze | 验证问题分析 | problem_statement | verifiability, checks |
| jcode.plan | 验证任务规划 | tasks | checks, warnings |
| jcode.implement | 验证代码实现 | implementation | checks, warnings |
| jcode.review | 代码审查裁决 | review | APPROVED/REJECTED |
| jcode.test | 测试验证裁决 | test_output | PASSED/FAILED |
| jcode.conductor | 终局裁决 | all outputs | SUCCESS/NEEDS_REVISION/FAILED |

### 使用示例

```python
# OpenCode 调用 JCode (通过 OMO)

# 1. 分析问题
result = call_mcp_tool("jcode.analyze", {
    "context_lock_id": "task-001",
    "input_data": {
        "problem_statement": "添加用户登录功能",
        "analysis": "[ANALYSIS] 问题分析内容...",
        "verifiability": "HARD"
    },
    "mode": "full"
})

# 2. 规划任务
result = call_mcp_tool("jcode.plan", {
    "context_lock_id": "task-001",
    "input_data": {
        "tasks": [
            {"todo": "创建登录表单", "done_when": "表单可提交"}
        ]
    },
    "mode": "full"
})

# 3. 审查代码
result = call_mcp_tool("jcode.review", {
    "context_lock_id": "task-001",
    "input_data": {
        "review": "[REVIEW] APPROVED",
        "implementation": "代码内容..."
    },
    "mode": "full"
})
# 返回: {"verdict": "APPROVED", "action": "CONTINUE"}
```

## 工作流集成

```
1. OpenCode 接收用户请求
2. OMO 锁定项目上下文 (Context Lock)
3. OMO 调用 jcode.analyze → JCode 验证分析结果
4. OMO 调用 jcode.plan → JCode 验证任务格式
5. OMO 执行实现 (LLM 生成代码)
6. OMO 调用 jcode.implement → JCode 验证代码
7. OMO 调用 jcode.review → JCode 返回 APPROVED/REJECTED
8. OMO 调用 jcode.test → JCode 返回 PASSED/FAILED
9. OMO 调用 jcode.conductor → JCode 做出最终裁决
10. 根据 decision: DELIVER/ITERATE/STOP 继续或停止
```

## 4-Level 开关

JCode 支持通过配置控制治理强度：

```yaml
# config/jcode_config.yaml
enabled: true
mode: full  # full/light/safe/fast/custom
agents:
  analyst: true
  planner: true
  implementer: true
  reviewer: true
  tester: true
  conductor: true
```

## 故障排除

1. **工具未找到**: 检查 OMO 配置中 jcode 服务器是否启用
2. **导入错误**: 确保 JCode 依赖已安装 (pip install -r requirements.txt)
3. **权限错误**: 检查文件路径权限
