# JCode v3.0 OpenCode/Superpowers 扩展层架构设计 - 工作计划

## TL;DR

> **Quick Summary**: 将 JCode 从独立 Agent 系统重新定位为 OpenCode/Superpowers 的治理扩展层，通过 MCP (Model Context Protocol) 标准协议集成，复用 Superpowers 的基础能力（Context Lock/Rule Engine/Incremental Build/Audit Log），专注于 6-Agent 治理逻辑的差异化实现。

> **Deliverables**:
> - 新增 `governance/OMO_INTEGRATION.md` - OMO 集成架构定义
> - 新增 `governance/CONTEXT_LOCK.md` - Context Lock 使用协议
> - 新增 `governance/RULE_ENGINE.md` - Rule Engine 使用协议
> - 新增 `governance/INCREMENTAL_BUILD.md` - Incremental Build 使用协议
> - 新增 `governance/AUDIT_LOG_SPEC.md` - 统一审计日志规范
> - 新增 `governance/JCODE_SWITCH.md` - 启用开关机制设计
> - 更新 `AGENTS.md` - 反映 v3.0 新定位（含开关功能）

> **Estimated Effort**: Medium (9-12 个任务)
> **Parallel Execution**: YES - 5 waves
> **Critical Path**: 文档设计 → 架构定义 → 集成规范 → 开关设计 → 更新索引

---

## Context

### Original Request
用户确认 JCode 定位为 OpenCode/Superpowers 的 Agent 治理扩展层，而非独立 Agent 系统。Superpowers 已集成在 OpenCode 中，4 个核心能力需要基于 MCP 标准定义集成接口。

### Interview Summary
**Key Discussions**:
- 战略定位决策：OpenCode 扩展层（复用 Superpowers 能力，专注差异化治理）
- MCP 标准发现：Model Context Protocol 是 Anthropic 开发的开放标准（modelcontextprotocol.io）
- 参考项目：everything-claude-code (51K stars) 提供完整的 Claude Code 配置参考
- 发现：4 个核心能力（Context Lock/Rule Engine/Incremental Build/Audit Log）需要 MCP Tool 定义
- OMO 能力探索：6 个后台任务并行探索 Superpowers/Context Lock/Rule Engine 等
- 发现：OMO 似乎是内部项目，无公开文档，需基于 MCP 标准设计集成

**Research Findings**:
- Superpowers 已集成到 OpenCode，提供基础能力
- JCode 通过 MCP Tool 定义 6 个 Agent 能力
- MCP 协议：JSON-RPC 2.0 格式，三层架构（Host → Client → Server）
- 参考：everything-claude-code 项目有 `.opencode` 目录和完整 MCP 配置
- JCode 应调用 OMO 的基础能力，自建治理逻辑
- 需要定义清晰的能力边界和集成接口

### Metis Review
**Identified Gaps** (addressed):
- Gap: OMO 能力接口未定义 → 解决：在 OMO_INTEGRATION.md 中定义 MCP Tool Schema
- Gap: 降级策略未说明 → 解决：增加 OMO 能力不可用时的降级方案
- Gap: 配置集成未定义 → 解决：增加 OMO 配置文件扩展示例
- Gap: 用户无法控制 JCode 启用 → 解决：新增 JCODE_SWITCH.md 开关机制

---

## Work Objectives

### Core Objective
完成 JCode v3.0 作为 OMO 扩展层的架构设计文档，定义与 OMO 的集成接口、能力边界、数据流和部署架构，并提供用户可控的启用开关。

### Concrete Deliverables
- `governance/OMO_INTEGRATION.md` - 核心集成架构文档
- `governance/CONTEXT_LOCK.md` - Context Lock 使用协议
- `governance/RULE_ENGINE.md` - Rule Engine 使用协议
- `governance/INCREMENTAL_BUILD.md` - Incremental Build 使用协议
- `governance/AUDIT_LOG_SPEC.md` - 审计日志统一规范
- `governance/JCODE_SWITCH.md` - 启用开关机制设计
- 更新 `AGENTS.md` 根文件 - 反映 v3.0 定位变化（含开关功能）

### Definition of Done
- [ ] 所有新增文档通过语法检查
- [ ] 集成架构被用户确认
- [ ] AGENTS.md 索引更新完成
- [ ] v3.0 版本号更新
- [ ] 开关机制设计完成

### Must Have
- MCP Tool Schema 定义完整（符合 modelcontextprotocol.io 规范）
- 能力边界清晰（Superpowers 做什么，JCode 做什么）
- 降级策略明确
- 配置扩展示例（含开关配置）
- 开关机制设计（全局/模式/Agent 级）
- 参考 everything-claude-code 项目的 MCP 配置模式
### Must NOT Have (Guardrails)
- 不要实现实际代码（仅文档设计）
- 不要假设 OMO 内部实现（仅定义接口）
- 不要破坏现有 JCode 治理逻辑（仅增加集成层）

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed

### Test Decision
- **Infrastructure exists**: NO (JCode 仍处设计阶段)
- **Automated tests**: NO (设计文档阶段)
- **Agent-Executed QA**: ALWAYS

### QA Policy
每个任务必须包含 agent-executed QA 场景：
- **文档 QA**: Read 文档 → 验证结构完整性 → 截图
- **一致性 QA**: Grep 验证跨文档引用 → 输出验证报告

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - 核心架构设计):
├── Task 1: 创建 OMO_INTEGRATION.md 核心架构文档 [deep]
├── Task 2: 创建 CONTEXT_LOCK.md [quick]
├── Task 3: 创建 RULE_ENGINE.md [quick]
└── Task 4: 创建 INCREMENTAL_BUILD.md [quick]

Wave 2 (After Wave 1 - 支撑文档):
├── Task 5: 创建 AUDIT_LOG_SPEC.md [unspecified-high]
├── Task 6: 创建 SUPERPOWERS_EXTENSION.md [quick]
└── Task 7: 创建 JCODE_SWITCH.md - 启用开关机制 [unspecified-high]

Wave 3 (After Wave 2 - 更新索引):
├── Task 8: 更新 AGENTS.md 根文件 - 反映 v3.0 定位（含开关） [quick]
└── Task 9: 更新 governance/AGENTS.md - 新增文件索引 [quick]

Wave 4 (After Wave 3 - 验证):
├── Task F1: 文档结构验证 (oracle)
├── Task F2: 跨文档一致性检查 (unspecified-high)
└── Task F3: MCP Schema 语法验证 (quick)

Critical Path: Task 1 → Task 8 → F1-F3
Parallel Speedup: ~65% faster than sequential
Max Concurrent: 4 (Wave 1 & Wave 2)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1 | — | 2, 3, 4, 6, 7, 8 |
| 2 | 1 | 5 |
| 3 | 1 | 5 |
| 4 | 1 | 5 |
| 5 | 2, 3, 4 | 8 |
| 6 | 1 | 8 |
| 7 | 1 | 8 |
| 8 | 5, 6, 7 | F1, F2, F3 |
| 9 | 8 | — |
| F1-F3 | 8 | — |

### Agent Dispatch Summary

- **Wave 1**: 4 tasks → 1×`deep`, 3×`quick`
- **Wave 2**: 3 tasks → 2×`unspecified-high`, 1×`quick`
- **Wave 3**: 2 tasks → 2×`quick`
- **Wave 4**: 3 tasks → 1×`oracle`, 1×`unspecified-high`, 1×`quick`

---

## TODOs

- [ ] 1. 创建 OMO_INTEGRATION.md 核心架构文档

  **What to do**:
  - 定义 JCode v3.0 作为 OMO 扩展层的架构定位
  - 绘制能力边界图（OMO 提供什么，JCode 提供什么）
  - 定义 MCP Superpowers 扩展点（6 个 Agent 对应的 tools）
  - 定义 OMO 能力调用接口（伪代码示例）
  - 设计完整任务执行数据流
  - 设计快速修正流程
  - 定义配置集成（OMO config.yaml 扩展）
  - 定义降级策略（OMO 能力不可用时）
  - 定义错误码和异常处理
  - 添加部署架构（内嵌/Sidecar/云原生）

  **Must NOT do**:
  - 不要实现实际代码
  - 不要假设 OMO 内部实现细节

  **Recommended Agent Profile**:
  - **Category**: `deep` - 复杂架构设计，需要系统性思考
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocks**: Tasks 2, 3, 4, 6, 7, 8
  - **Blocked By**: None

  **References**:
  - `requairment.txt` - OMO 能力需求描述
  - `governance/AGENT_CONSTITUTION.md` - 现有宪法规则
  - MCP 官方文档 - https://modelcontextprotocol.io/
  - everything-claude-code - https://github.com/affaan-m/everything-claude-code (51K stars)
  - MCP GitHub - https://github.com/modelcontextprotocol/modelcontextprotocol
  **Acceptance Criteria**:
  - [ ] 文档 800-1500 行
  - [ ] 包含架构图（ASCII art）
  - [ ] 包含 MCP Tool Schema 定义
  - [ ] 包含 Python 伪代码示例
  - [ ] 包含配置扩展示例

  **QA Scenarios**:

  ```
  Scenario: 验证文档结构完整性
    Tool: Read
    Preconditions: OMO_INTEGRATION.md 已创建
    Steps:
      1. Read governance/OMO_INTEGRATION.md
      2. 验证包含章节：架构定位、能力边界、MCP 扩展点、数据流、配置集成、降级策略
      3. 计算文档行数
    Expected Result: 800-1500 行，包含所有必需章节
    Failure Indicators: <800 行或>1500 行，或缺少必需章节
    Evidence: .sisyphus/evidence/task-1-structure-check.txt
  ```

  **Commit**: YES (groups with 2, 3, 4)
  - Message: `docs(governance): add OMO integration architecture (v3.0)`
  - Files: `governance/OMO_INTEGRATION.md`

---

- [ ] 2. 创建 CONTEXT_LOCK.md

  **What to do**:
  - 定义 Context Lock 存储结构（.memory/ 目录）
  - 定义记忆类型（项目结构、关键文件、规则集、会话历史）
  - 定义检索协议（优先级、触发条件）
  - 定义更新策略（自动/手动/定期）
  - 定义与 OMO Context Lock 的集成方式
  - 提供 Python 集成示例

  **Must NOT do**:
  - 不要实现实际存储逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick` - 单一关注点文档
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 3, 4)
  - **Blocks**: Task 5
  - **Blocked By**: Task 1

  **References**:
  - `governance/OMO_INTEGRATION.md` - 集成架构
  - `agents/planner.md` - Planner 记忆复用需求

  **Acceptance Criteria**:
  - [ ] 文档 100-200 行
  - [ ] 包含记忆存储结构定义
  - [ ] 包含检索协议
  - [ ] 包含 Python 集成示例

  **QA Scenarios**:

  ```
  Scenario: 验证文档完整性
    Tool: Read
    Preconditions: CONTEXT_LOCK.md 已创建
    Steps:
      1. Read governance/CONTEXT_LOCK.md
      2. 验证包含章节：存储结构、记忆类型、检索协议、更新策略
    Expected Result: 100-200 行，包含所有必需章节
    Evidence: .sisyphus/evidence/task-2-structure-check.txt
  ```

  **Commit**: YES (groups with 1, 3, 4)

---

- [ ] 3. 创建 RULE_ENGINE.md

  **What to do**:
  - 定义规则语法（YAML 格式）
  - 定义规则优先级（P0-P3）
  - 定义规则执行时机（IMPLEMENTATION/REVIEW 阶段）
  - 定义违规处理（TERMINATE/QUICK_FIX/LOG_ONLY）
  - 定义 Soft Hooks 机制
  - 定义与 OMO Rule Engine 的集成
  - 提供规则示例和 Python 集成代码

  **Must NOT do**:
  - 不要实现实际规则引擎

  **Recommended Agent Profile**:
  - **Category**: `quick` - 单一关注点文档
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 4)
  - **Blocks**: Task 5
  - **Blocked By**: Task 1

  **References**:
  - `governance/AGENT_CONSTITUTION.md` - 宪法规则
  - `governance/QUICK_FIX_CHANNEL.md` - 快速修正规则

  **Acceptance Criteria**:
  - [ ] 文档 150-250 行
  - [ ] 包含 YAML 规则示例
  - [ ] 包含优先级定义
  - [ ] 包含违规处理流程

  **QA Scenarios**:

  ```
  Scenario: 验证规则语法示例
    Tool: Read
    Preconditions: RULE_ENGINE.md 已创建
    Steps:
      1. Read governance/RULE_ENGINE.md
      2. 找到 YAML 规则示例部分
      3. 验证包含 rule id、pattern、severity、message 字段
    Expected Result: YAML 语法有效，包含必需字段
    Evidence: .sisyphus/evidence/task-3-syntax-check.txt
  ```

  **Commit**: YES (groups with 1, 2, 4)

---

- [ ] 4. 创建 INCREMENTAL_BUILD.md

  **What to do**:
  - 定义 diff 生成协议（行级/块级/文件级）
  - 定义 diff 格式（unified diff）
  - 定义代码合并策略（人类优先原则）
  - 定义依赖影响分析流程
  - 定义回滚机制（任务级/文件级/代码块级）
  - 定义与 OMO Incremental Build 的集成
  - 提供 Python 集成示例

  **Must NOT do**:
  - 不要实现实际 diff 算法

  **Recommended Agent Profile**:
  - **Category**: `quick` - 单一关注点文档
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Task 5
  - **Blocked By**: Task 1

  **References**:
  - `governance/QUICK_FIX_CHANNEL.md` - 快速修正中的增量修改
  - Git unified diff 格式

  **Acceptance Criteria**:
  - [ ] 文档 150-250 行
  - [ ] 包含 diff 格式示例
  - [ ] 包含合并策略定义
  - [ ] 包含回滚流程

  **QA Scenarios**:

  ```
  Scenario: 验证 diff 格式示例
    Tool: Read
    Preconditions: INCREMENTAL_BUILD.md 已创建
    Steps:
      1. Read governance/INCREMENTAL_BUILD.md
      2. 找到 diff 示例部分
      3. 验证包含 --- a/、+++ b/、@@ 行号 等 unified diff 元素
    Expected Result: diff 格式正确，符合 unified diff 标准
    Evidence: .sisyphus/evidence/task-4-diff-check.txt
  ```

  **Commit**: YES (groups with 1, 2, 3)

---

- [ ] 5. 创建 AUDIT_LOG_SPEC.md

  **What to do**:
  - 定义统一审计日志格式（JSON Schema）
  - 定义日志字段（log_id、timestamp、actor_type、action_type、context、details、integrity）
  - 定义存储位置（.omo/audit/）
  - 定义查询接口（search、get_task_history、get_human_interventions）
  - 定义与 OMO Audit Log 的集成
  - 定义日志轮转策略
  - 提供 Python 查询示例

  **Must NOT do**:
  - 不要实现实际日志存储

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` - 需要设计统一规范
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Tasks 2, 3, 4

  **References**:
  - `governance/HUMAN_INTERFACE.md` - 人类介入审计
  - `governance/QUICK_FIX_CHANNEL.md` - 快速修正审计
  - `governance/EDGE_CASES.md` - 状态机审计

  **Acceptance Criteria**:
  - [ ] 文档 150-250 行
  - [ ] 包含 JSON Schema 定义
  - [ ] 包含查询接口定义
  - [ ] 包含 Python 示例

  **QA Scenarios**:

  ```
  Scenario: 验证 JSON Schema 有效性
    Tool: Read
    Preconditions: AUDIT_LOG_SPEC.md 已创建
    Steps:
      1. Read governance/AUDIT_LOG_SPEC.md
      2. 找到 JSON Schema 定义部分
      3. 验证包含必需字段：log_id、timestamp、actor_type、action_type
    Expected Result: JSON Schema 语法有效
    Evidence: .sisyphus/evidence/task-5-schema-check.txt
  ```

  **Commit**: YES (groups with 6, 7)
  - Message: `docs(governance): add audit log spec, superpowers extension, and switch mechanism (v3.0)`
  - Files: `governance/AUDIT_LOG_SPEC.md`, `governance/SUPERPOWERS_EXTENSION.md`, `governance/JCODE_SWITCH.md`

---

- [ ] 6. 创建 SUPERPOWERS_EXTENSION.md

  **What to do**:
  - 定义 Superpowers 扩展机制
  - 定义 MCP Tool 注册流程
  - 定义 6 个 JCode Agent 对应的 MCP Tool
  - 定义 Tool 调用参数和返回值格式
  - 提供扩展示例代码
  - 定义与 OMO Superpowers 的集成

  **Must NOT do**:
  - 不要实现实际 MCP Server

  **Recommended Agent Profile**:
  - **Category**: `quick` - 单一关注点文档
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Task 1

  **References**:
  - MCP 官方文档 - https://modelcontextprotocol.io/
  - `governance/OMO_INTEGRATION.md` - 集成架构

  **Acceptance Criteria**:
  - [ ] 文档 100-200 行
  - [ ] 包含 MCP Tool JSON Schema
  - [ ] 包含 6 个 Tool 定义
  - [ ] 包含扩展示例

  **QA Scenarios**:

  ```
  Scenario: 验证 MCP Tool Schema
    Tool: Read
    Preconditions: SUPERPOWERS_EXTENSION.md 已创建
    Steps:
      1. Read governance/SUPERPOWERS_EXTENSION.md
      2. 找到 MCP Tool Schema 定义
      3. 验证包含 name、description、inputSchema 字段
    Expected Result: Schema 符合 MCP 规范
    Evidence: .sisyphus/evidence/task-6-mcp-check.txt
  ```

  **Commit**: YES (groups with 5, 7)

---

- [ ] 7. 创建 JCODE_SWITCH.md - 启用开关机制设计

  **What to do**:
  - 定义开关配置格式（YAML/JSON）
  - 定义开关位置（配置文件/命令行/会话内）
  - 定义开关粒度（全局/模式/Agent 级/规则级）
  - 定义开关优先级规则（会话内命令 > 项目配置 > 用户配置 > OMO 配置）
  - 定义开关状态持久化方案
  - 定义强制启用场景（敏感文件/删除操作/权限修改）
  - 定义开关变更审计日志格式
  - 提供 Python 实现示例
  - 定义 CLI 命令格式（--jcode/--no-jcode）
  - 定义 UI 交互方案（如果 OMO 有界面）

  **Must NOT do**:
  - 不要实现实际开关逻辑
  - 不要假设 OMO 的 UI 能力

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` - 需要设计用户体验和配置系统
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Task 1
  - **Blocks**: Task 8

  **References**:
  - `governance/OMO_INTEGRATION.md` - 配置集成章节
  - `governance/HUMAN_INTERFACE.md` - 人类介入机制
  - `.sisyphus/plans/jcode-switch-design.md` - 开关设计补充文档

  **Acceptance Criteria**:
  - [ ] 文档 200-400 行
  - [ ] 包含配置文件格式定义
  - [ ] 包含 CLI 命令定义
  - [ ] 包含优先级规则
  - [ ] 包含强制启用场景
  - [ ] 包含审计日志格式
  - [ ] 包含使用场景示例（≥4 个）

  **QA Scenarios**:

  ```
  Scenario: 验证配置格式定义
    Tool: Read
    Preconditions: JCODE_SWITCH.md 已创建
    Steps:
      1. Read governance/JCODE_SWITCH.md
      2. 找到配置文件格式部分
      3. 验证包含 enabled、mode、agents 配置项
    Expected Result: YAML 格式有效，包含必需配置项
    Evidence: .sisyphus/evidence/task-7-switch-config-check.txt
  ```

  **Commit**: YES (groups with 5, 6)

---

- [ ] 8. 更新 AGENTS.md 根文件 - 反映 v3.0 定位（含开关）

  **What to do**:
  - 更新 OVERVIEW - 明确 OMO 扩展层定位
  - 更新 STRUCTURE - 新增 governance/ 下的集成文档（7 个文件）
  - 更新 WHERE TO LOOK - 新增 OMO 集成相关索引（含开关配置）
  - 更新 NOTES - 添加 v3.0 更新说明（含开关功能）
  - 版本号更新为 v3.0

  **Must NOT do**:
  - 不要删除现有内容（仅更新）

  **Recommended Agent Profile**:
  - **Category**: `quick` - 文档更新
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Tasks 5, 6, 7

  **References**:
  - `AGENTS.md` - 当前版本
  - 所有新增的 governance/*.md 文件

  **Acceptance Criteria**:
  - [ ] 新增 OMO 扩展层定位说明
  - [ ] 新增 7 个集成文档的索引
  - [ ] 版本号更新为 v3.0
  - [ ] 添加 v3.0 更新说明（集成架构 + 开关机制）

  **QA Scenarios**:

  ```
  Scenario: 验证 v3.0 定位说明
    Tool: Read
    Preconditions: AGENTS.md 已更新
    Steps:
      1. Read AGENTS.md
      2. 找到 OVERVIEW 部分
      3. 验证包含"Oh-my-opencode 的治理扩展层"描述
    Expected Result: 明确说明 OMO 扩展层定位
    Evidence: .sisyphus/evidence/task-8-positioning-check.txt
  ```

  **Commit**: YES (groups with 9)
  - Message: `docs: update AGENTS.md for v3.0 OMO extension positioning (with switch)`
  - Files: `AGENTS.md`, `governance/AGENTS.md`

---

- [ ] 9. 更新 governance/AGENTS.md - 新增文件索引

  **What to do**:
  - 更新 WHERE TO LOOK - 新增 OMO_INTEGRATION.md 等 7 个文件
  - 更新 ANTI-PATTERNS - 新增"脱离 OMO 独立实现"的反模式
  - 更新 CONVENTIONS - 新增开关机制说明
  - 版本号/状态更新

  **Must NOT do**:
  - 不要删除现有内容

  **Recommended Agent Profile**:
  - **Category**: `quick` - 文档更新
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 8)
  - **Blocked By**: Tasks 5, 6, 7

  **References**:
  - `governance/AGENTS.md` - 当前版本
  - 所有新增的 governance/*.md 文件

  **Acceptance Criteria**:
  - [ ] 新增 7 个集成文档的索引
  - [ ] 新增反模式说明
  - [ ] 新增开关机制说明

  **QA Scenarios**:

  ```
  Scenario: 验证新增文件索引
    Tool: Read
    Preconditions: governance/AGENTS.md 已更新
    Steps:
      1. Read governance/AGENTS.md
      2. 找到 WHERE TO LOOK 部分
      3. 验证包含 OMO_INTEGRATION.md、JCODE_SWITCH.md 等 7 个新文件
    Expected Result: 所有新增文件都被索引
    Evidence: .sisyphus/evidence/task-9-index-check.txt
  ```

  **Commit**: YES (groups with 8)

---

## Final Verification Wave

- [ ] F1. **文档结构验证** — `oracle`
  读取所有新增文档（OMO_INTEGRATION.md、CONTEXT_LOCK.md、RULE_ENGINE.md、INCREMENTAL_BUILD.md、AUDIT_LOG_SPEC.md、SUPERPOWERS_EXTENSION.md、JCODE_SWITCH.md）。验证：
  - 每个文档都有完整的章节结构
  - 文档行数在预期范围内
  - 无明显的逻辑跳跃或缺失
  Output: `Documents [N/N valid] | Structure [PASS/FAIL] | VERDICT`

- [ ] F2. **跨文档一致性检查** — `unspecified-high`
  Grep 搜索所有新增文档中的关键术语：
  - OMO 能力调用是否在多个文档中一致
  - MCP Tool 定义是否一致
  - 配置示例是否一致（含开关配置）
  - 引用是否准确（文档名、章节名）
  Output: `Terms [N/N consistent] | References [N/N accurate] | VERDICT`

- [ ] F3. **MCP Schema 语法验证** — `quick`
  读取 SUPERPOWERS_EXTENSION.md 和 OMO_INTEGRATION.md 中的 MCP Schema 定义，验证：
  - JSON Schema 语法有效性
  - 必需字段完整性
  - 与 MCP 官方规范的一致性
  Output: `Schema [VALID/INVALID] | Fields [N/N present] | VERDICT`

---

## Commit Strategy

- **1-4**: `docs(governance): add OMO integration core architecture (v3.0)` — OMO_INTEGRATION.md, CONTEXT_LOCK.md, RULE_ENGINE.md, INCREMENTAL_BUILD.md
- **5-7**: `docs(governance): add audit log spec, superpowers extension, and switch mechanism (v3.0)` — AUDIT_LOG_SPEC.md, SUPERPOWERS_EXTENSION.md, JCODE_SWITCH.md
- **8-9**: `docs: update AGENTS.md for v3.0 OMO extension positioning (with switch)` — AGENTS.md, governance/AGENTS.md
- **F1-F3**: `docs: verify v3.0 integration architecture` — (no files, verification only)

---

## Success Criteria

### Verification Commands
```bash
# 验证文档结构
find governance -name "*.md" -newer governance/AGENT_CONSTITUTION.md  # 应返回新增的 7 个文件

# 验证版本号
grep "v3.0" AGENTS.md governance/AGENTS.md  # 应返回版本更新

# 验证文件完整性
ls -la governance/OMO_INTEGRATION.md governance/CONTEXT_LOCK.md governance/RULE_ENGINE.md governance/INCREMENTAL_BUILD.md governance/AUDIT_LOG_SPEC.md governance/SUPERPOWERS_EXTENSION.md governance/JCODE_SWITCH.md  # 应全部存在

# 验证开关配置索引
grep "JCODE_SWITCH" governance/AGENTS.md  # 应返回开关文档引用
```

### Final Checklist
- [ ] 所有新增文档存在且语法正确
- [ ] AGENTS.md 已更新反映 v3.0 定位
- [ ] 所有跨文档引用准确
- [ ] MCP Schema 符合官方规范
- [ ] 能力边界清晰（OMO vs JCode）
- [ ] 开关机制设计完整（配置/CLI/会话内）
- [ ] 强制启用场景定义明确
