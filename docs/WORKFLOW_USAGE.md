# JCode 工作流使用指南

## 快速开始

### 1. 启动 MCP 服务器

```bash
cd C:\dev_projects\jcode
python -m mcp.server --port 8080
```

### 2. 在 OpenCode 中使用

```
# Step 1: 分析需求
@jcode-analyst 分析这个需求：实现用户登录功能，支持邮箱和手机号

# Step 2: 制定任务 (Analyst 会自动调用)
@jcode-planner 根据 ANALYSIS 制定实现任务

# Step 3: 实现代码
@jcode-implementer 按 TASKS 实现代码

# Step 4: 代码审查
@jcode-reviewer 审查实现是否符合 TASKS

# Step 5: 测试验证
@jcode-tester 运行测试，提供证据

# Step 6: 最终裁决
@jcode-conductor 基于 REVIEW 和 TEST 结果做最终裁决
```

---

## 完整工作流示例

### 示例：实现一个 API 端点

```
用户: @jcode-analyst 需要实现 GET /api/users/{id} 端点，返回用户信息

@jcode-analyst 输出:
[ANALYSIS]
## 问题理解
- 核心问题: 实现 RESTful API 端点
- 用户意图: 通过 ID 查询用户信息

## 约束条件
- 技术约束: 使用 FastAPI
- 安全约束: 需要认证

## 可验证性
- 类型: HARD
- 验证方法: curl 请求 + 单元测试

---

用户: @jcode-planner 制定实现任务

@jcode-planner 输出:
[TASKS]
### Task 1: 创建路由
- 描述: 在 routers/users.py 添加 GET /users/{id}
- 验收标准: 返回 200 + JSON

### Task 2: 添加认证
- 描述: 使用 JWT 验证
- 验收标准: 未认证返回 401

---

用户: @jcode-implementer 实现这些任务

@jcode-implementer 输出:
[IMPLEMENTATION]
## 变更摘要
- 文件: api/routes/users.py (+25 lines)
- 文件: tests/test_users.py (+15 lines)

---

用户: @jcode-reviewer 审查代码

@jcode-reviewer 输出:
[REVIEW]
- 判决: APPROVED
- 检查清单全部通过

---

用户: @jcode-tester 运行测试

@jcode-tester 输出:
[TEST]
- 判决: PASSED
- 测试证据: 5/5 passed

---

用户: @jcode-conductor 做最终裁决

@jcode-conductor 输出:
[FINAL]
- 决定: DELIVER
- REVIEW: APPROVED
- TEST: PASSED
- 交付成功
```

---

## 通过 MCP 直接调用

```bash
# 1. 分析
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "jcode-analyst",
      "arguments": {
        "context_lock_id": "task-001",
        "input_data": {
          "problem_statement": "实现用户登录",
          "user_requirements": {"auth": "email+phone"}
        },
        "mode": "full"
      }
    }
  }'

# 2. 规划
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "jcode-planner",
      "arguments": {
        "context_lock_id": "task-001",
        "input_data": {
          "analysis_result": {...}
        },
        "mode": "full"
      }
    }
  }'

# 3-6: 类似调用其他 Agent...
```

---

## 迭代流程

当 REVIEW=REJECTED 或 TEST=FAILED 时：

```
ITERATION 1:
  ANALYSIS → TASKS → IMPLEMENTATION → REVIEW (REJECTED)
                                           ↓
                                     ITERATION+1
                                           ↓
ITERATION 2:
  ANALYSIS → TASKS → IMPLEMENTATION → REVIEW (APPROVED) → TEST (FAILED)
                                                              ↓
                                                         ITERATION+2
                                                              ↓
ITERATION 3:
  ANALYSIS → TASKS → IMPLEMENTATION → REVIEW (APPROVED) → TEST (PASSED) → CONDUCTOR
                                                                              ↓
                                                                         DELIVER
```

---

## 强制终止条件

以下情况会触发 STOP：

1. **NON-VERIFIABLE**: Analyst 判定任务无法验证
2. **ITERATION_OVERFLOW**: 迭代次数超过限制 (默认 3 次)
3. **STRUCTURAL_VIOLATION**: Agent 越权或协议违规

STOP 后需要人类介入才能继续。
