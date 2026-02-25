# OMO_INTEGRATION — Oh-my-opencode 集成架构

> Status: **DESIGN DRAFT**
> Scope: MCP-based integration architecture
> Purpose: Define how JCode extends OMO with governance layer
> Integration Mode: Language-agnostic via Model Context Protocol (MCP)

---

## 0. 集成定位

JCode 不是 OMO 的替代品，而是 **OMO 的治理扩展层**。

```
┌─────────────────────────────────────────┐
│           Oh-my-opencode (OMO)          │
│  ┌───────────────────────────────────┐  │
│  │  Core Capabilities:               │  │
│  │  - Context Lock                   │  │
│  │  - Rule Engine                    │  │
│  │  - Incremental Build              │  │
│  │  - User Interface                 │  │
│  └───────────────────────────────────┘  │
│                   ↕                     │
│              MCP Protocol               │
│                   ↕                     │
│  ┌───────────────────────────────────┐  │
│  │     JCode Governance Layer        │  │
│  │  - 6-Agent System (司马迁-韩非子)  │  │
│  │  - Constitutional Rules          │  │
│  │  - Human-Interface Protocol       │  │
│  │  - Switch Mechanism (4-level)     │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**核心论据**：
- OMO 提供**能力**（让 AI 能写代码）
- JCode 提供**约束**（让 AI 写好代码）
- MCP 协议实现**语言无关集成**

---

## 1. MCP 工具定义

JCode 通过 MCP 协议向 OMO 暴露 6 个核心工具：

### 1.1 `jcode.analyze` - 问题分析

**输入**：
```json
{
  "problem_statement": "用户需求描述",
  "context_lock_id": "OMO上下文ID",
  "mode": "full|light|safe|fast|custom"
}
```

**输出**：
```json
{
  "section": "[ANALYSIS]",
  "verifiability": "HARD|SOFT|NON-VERIFIABLE",
  "nfrs": {
    "performance": "...",
    "maintainability": "...",
    "security": "..."
  },
  "risks": ["..."],
  "unknowns": ["..."]
}
```

**失败条件**：
- 返回 `verifiability: "NON-VERIFIABLE"` → 触发 HUMAN_INTERVENTION

---

### 1.2 `jcode.plan` - 任务规划

**输入**：
```json
{
  "analysis": "[ANALYSIS]输出",
  "context_lock_id": "OMO上下文ID",
  "mode": "full|light|safe|fast|custom"
}
```

**输出**：
```json
{
  "section": "[TASKS]",
  "tasks": [
    {
      "todo": "...",
      "done_when": "...",
      "verify_by": "..."
    }
  ],
  "dependencies": [["task1", "task2"]]
}
```

**失败条件**：
- 任务不可验证 → REVIEW 必须 REJECT

---

### 1.3 `jcode.implement` - 代码实现

**输入**：
```json
{
  "tasks": "[TASKS]输出",
  "context_lock_id": "OMO上下文ID",
  "om_rules": ["全局规则ID列表"],
  "mode": "full|light|safe|fast|custom"
}
```

**输出**：
```json
{
  "section": "[IMPLEMENTATION]",
  "artifacts": {
    "files": ["path/to/file.ext"],
    "diff": "统一diff格式",
    "metadata": {
      "iteration": 1,
      "changes_count": 42
    }
  }
}
```

**失败条件**：
- 越权改动（实现 TASKS 未授权内容）→ REVIEW REJECT

---

### 1.4 `jcode.review` - 合规审查

**输入**：
```json
{
  "tasks": "[TASKS]输出",
  "implementation": "[IMPLEMENTATION]输出",
  "mode": "full|light|safe|fast|custom",
  "quick_fix_eligible": true
}
```

**输出**：
```json
{
  "section": "[REVIEW]",
  "result": "APPROVED|REJECTED",
  "issues": [
    {
      "task_ref": "task1",
      "severity": "MAJOR|MINOR",
      "description": "具体问题",
      "suggested_fix": "仅在MINOR_FIX时提供"
    }
  ],
  "quick_fix_trigger": "MINOR_FIX|null"
}
```

**失败条件**：
- 任何 MAJOR 问题 → 迭代 +1
- 2+ MINOR 问题 → 快速修正通道

---

### 1.5 `jcode.test` - 证据验证

**输入**：
```json
{
  "tasks": "[TASKS]输出",
  "implementation": "[IMPLEMENTATION]输出",
  "verify_by_clauses": ["verify by列表"],
  "mode": "full|light|safe|fast|custom"
}
```

**输出**：
```json
{
  "section": "[TEST]",
  "result": "PASSED|FAILED|EVIDENCE_UNAVAILABLE",
  "evidence": {
    "test_output": "...",
    "metrics": {...},
    "screenshots": ["path/to/screenshot.png"]
  },
  "failed_clauses": ["verify by1", "verify by2"]
}
```

**失败条件**：
- 任何 verify by 失败 → 迭代 +1

---

### 1.6 `jcode.conductor` - 终局裁决

**输入**：
```json
{
  "review_result": "APPROVED|REJECTED",
  "test_result": "PASSED|FAILED|EVIDENCE_UNAVAILABLE",
  "iteration_count": 1,
  "max_iterations": 5,
  "mode": "full|light|safe|fast|custom"
}
```

**输出**：
```json
{
  "section": "[FINAL]",
  "decision": "DELIVER|ITERATE|STOP",
  "reason": "触发规则的描述",
  "next_iteration": 2,
  "deliverables": {
    "files": ["path/to/file.ext"],
    "audit_log": "path/to/audit.log"
  }
}
```

**失败条件**：
- `decision: "STOP"` → 系统暂停，等待 HUMAN_INTERVENTION

---

## 2. 集成架构

### 2.1 完整工作流

```
┌─────────────────────────────────────────────────────────────┐
│  OMO: User Request                                          │
│  "Add authentication to API endpoints"                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  OMO: Context Lock (项目上下文锁定)                          │
│  - 项目结构: src/api/, src/auth/                            │
│  - 现有规则: R001_no_skip_review, R002_test_required         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Call: jcode.analyze(problem="...", context_lock_id=...)│
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  JCode: Analyst (司马迁)                                      │
│  - Verifiability: HARD                                       │
│  - NFRs: Security=HIGH, Performance=100ms                  │
│  - Risks: Token leakage, Session hijacking                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Call: jcode.plan(analysis="...", ...)                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  JCode: Planner (商鞅)                                         │
│  - TASK1: Implement JWT middleware                           │
│  - TASK2: Add login endpoint                                  │
│  - TASK3: Add session management                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Call: jcode.implement(tasks="...", om_rules=["R001"])│
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  JCode: Implementer (鲁班) + OMO: Rule Engine                │
│  - Implementation: 完成代码编写                              │
│  - OMO Rule Check: R001_no_skip_review = PASSED             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Call: jcode.review(tasks="...", implementation="...") │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  JCode: Reviewer (包拯)                                       │
│  - Result: APPROVED                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Call: jcode.test(...verify_by_clauses=["test_auth"])  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  JCode: Tester (张衡) + OMO: Incremental Build               │
│  - Result: PASSED                                             │
│  - Evidence: Test output, Coverage metrics                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Call: jcode.conductor(review="APPROVED", test="PASSED")│
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  JCode: CONDUCTOR (韩非子)                                     │
│  - Decision: DELIVER                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  OMO: Incremental Build                                       │
│  - Apply changes incrementally                                │
│  - Update Context Lock                                       │
│  - Generate audit log                                        │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.2 开关机制集成

JCode 的 4 级开关通过 OMO 的配置系统暴露：

```yaml
# OMO Configuration (.omo/config.yaml)
jcode:
  # Level 1: 全局开关
  enabled: true

  # Level 2: 模式开关
  mode: "full"  # full | light | safe | fast | custom

  # Level 3: Agent 级开关
  agents:
    analyst: true
    planner: true
    implementer: true
    reviewer: true
    tester: true
    conductor: true

  # Level 4: 规则级开关
  rules:
    R001_no_skip_review: true
    R002_test_required: true
    R003_nfr_required: true
    R004_human_intervention_on_error: true

  # 迭代控制
  max_iterations: 5

  # 强制启用场景
  forced_enable:
    file_patterns:
      - "**/config/**"
      - "**/*secret*"
      - "**/*.env"
    operations:
      - delete_file
      - modify_permission
      - database_migration
```

**开关行为**：
- `enabled: false` → JCode 完全禁用，OMO 正常工作
- `mode: "light"` → 跳过 NFR 检查，仅保留核心审查
- `mode: "safe"` → 启用所有 Agent，+ 强制人类介入
- `forced_enable` → 无论全局开关如何，匹配条件时强制启用

---

## 3. 数据流与审计

### 3.1 审计日志格式

所有 JCode 调用生成审计日志：

```json
{
  "timestamp": "2026-02-24T10:30:00Z",
  "om_session_id": "omo_session_12345",
  "jcode_invocation_id": "jcode_inv_67890",
  "tool": "jcode.analyze",
  "input": {...},
  "output": {...},
  "duration_ms": 1250,
  "iteration": 1,
  "mode": "full",
  "agent": "analyst",
  "result": "SUCCESS"
}
```

**存储位置**：
- OMO 侧：`audit/jcode_invocations.jsonl`
- JCode 侧：`audit/om_requests.jsonl`（可选，用于调试）

---

### 3.2 HUMAN_INTERVENTION 集成

当 JCode 触发强制介入点，OMO 通过用户界面展示：

```json
{
  "intervention_type": "NON-VERIFIABLE|ITERATION_OVERFLOW|STRUCTURAL_VIOLATION|EVIDENCE_UNAVAILABLE",
  "jcode_session_id": "jcode_session_abc123",
  "om_context": {
    "current_task": "Add authentication",
    "iteration": 6,
    "max_iterations": 5
  },
  "intervention_options": [
    {
      "id": "retry",
      "label": "重新定义任务",
      "requires_admin": false
    },
    {
      "id": "extend",
      "label": "延长迭代限制",
      "requires_admin": true
    },
    {
      "id": "stop",
      "label": "终止任务",
      "requires_admin": false
    }
  ]
}
```

OMO UI 渲染为交互式对话框，用户选择后通过 MCP 调用 `jcode.human_intervention`。

---

## 4. 错误处理与恢复

### 4.1 JCode 侧错误

| 错误类型 | JCode 响应 | OMO 处理 |
|---|---|---|
| NON-VERIFIABLE | 停止，返回 `verifiability: "NON-VERIFIABLE"` | 展示 HUMAN_INTERVENTION |
| 越权实现 | REVIEW: REJECTED | 迭代 +1 |
| 规则冲突 | CONDUCTOR: STOP | 展示冲突详情，请求人类决策 |
| 迭代溢出 | CONDUCTOR: STOP | 展示溢出详情，请求延长或终止 |

### 4.2 OMO 侧错误

| 错误类型 | OMO 响应 | JCode 处理 |
|---|---|---|
| Context Lock 失败 | 返回 `context_lock_error` | Implementer 停止，REVIEW: REJECTED |
| Rule Engine 不可用 | 返回 `rule_engine_unavailable` | JCode 记录警告，继续执行 |
| Incremental Build 失败 | 返回 `build_failed` | CONDUCTOR: STOP |
| MCP 连接失败 | 返回 `mcp_connection_error` | JCode 降级到独立模式（如果可用） |

---

## 5. 性能优化

### 5.1 并行化机会

JCode 6-Agent 系统内部串行（宪法约束），但与 OMO 的集成可并行：

```
OMO Context Lock + JCode Analyst ── 并行
        ↓
        Planner
        ↓
    Implementer (串行)
        ↓
OMO Rule Engine + JCode Reviewer ── 并行
        ↓
        Tester
        ↓
    Conductor
```

### 5.2 缓存策略

- **Context Lock** → 缓存 1 小时（项目结构不变）
- **JCode 分析结果** → 缓存 30 分钟（相同问题）
- **OMO 规则检查结果** → 缓存 10 分钟（规则不变）

---

## 6. 安全性

### 6.1 认证与授权

- MCP 通信使用 TLS 1.3
- 所有调用必须包含 `om_session_token`
- JCode 验证 OMO 令牌有效性

### 6.2 数据隔离

- 每个 OMO session 有独立的 `context_lock_id`
- JCode 审计日志包含 `om_session_id` 用于追溯
- 跨 session 数据隔离，无共享状态

---

## 7. 测试与验证

### 7.1 集成测试场景

| 场景 | 预期行为 |
|---|---|
| 正常流程（6步全通过） | DELIVER，文件提交到 OMO Incremental Build |
| REVIEW: REJECTED | 迭代 +1，重新从 ANALYSIS 开始 |
| 迭代溢出 | CONDUCTOR: STOP，HUMAN_INTERVENTION |
| 开关：`mode: "light"` | 跳过 NFR 检查，保留核心审查 |
| 强制启用：修改配置文件 | 即使 `enabled: false`，也启用 JCode |

### 7.2 兼容性测试

- OMO 版本：>= 2.0
- MCP 协议：>= 1.0
- JCode 版本：>= 3.0 (本版本)

---

## 8. 未来扩展

### 8.1 计划中的增强

- **自适应模式**：根据任务复杂度自动调整 `mode`
- **规则热更新**：OMO Rule Engine 动态更新 JCode 规则
- **分布式 JCode**：多个 JCode 实例负载均衡（需要状态同步）

### 8.2 可选集成

- **CI/CD 集成**：JCode 作为 GitHub Actions 步骤
- **IDE 插件**：实时显示 REVIEW 和 TEST 状态
- **监控面板**：可视化 JCode 性能指标

---

## 9. 实施路线图

### Phase 1: 核心集成（Week 1-2）
- [ ] 实现 6 个 MCP 工具
- [ ] 实现基础审计日志
- [ ] 实现 4 级开关机制

### Phase 2: 错误处理与恢复（Week 3）
- [ ] 实现 HUMAN_INTERVENTION 集成
- [ ] 实现错误恢复机制
- [ ] 实现缓存策略

### Phase 3: 性能优化（Week 4）
- [ ] 实现并行化机会
- [ ] 实现性能监控
- [ ] 压力测试

### Phase 4: 文档与测试（Week 5-6）
- [ ] 编写完整集成文档
- [ ] 编写测试用例
- [ ] 编写用户手册

---

## 封印语

> **OMO 提供能力，JCode 提供约束。**
> **让 AI 能写代码，更要让 AI 写好代码。**

---

**END OF OMO_INTEGRATION**
