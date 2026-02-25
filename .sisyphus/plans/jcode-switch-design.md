# JCode 启用开关设计 - 工作计划补充

## 需求背景

用户需要在 OpenCode/OMO 中控制是否启用 JCode 治理层，以平衡**开发效率**与**代码质量**。

---

## 设计方案

### 1. 开关位置

#### 1.1 配置文件开关（主要）

**OMO 配置文件** (`.omo/config.yaml`)：
```yaml
jcode:
  enabled: true  # 全局开关
  version: "3.0"
  
  # 分 Agent 开关
  agents:
    analyst: true
    planner: true
    implementer: true
    reviewer: true
    tester: true
    conductor: true
  
  # 分场景开关
  scenes:
    production_code: true   # 生产代码启用
    prototype: false        # 原型开发禁用
    sensitive_operation: true  # 敏感操作强制启用
```

**JCode 独立配置** (`.jcode/config.yaml`) - 覆盖 OMO 配置：
```yaml
# 优先级：.jcode/config.yaml > .omo/config.yaml > 默认值

enabled: true
mode: "full"  # full | light | custom

# 快速模式预设
presets:
  fast:  # 快速模式
    enabled: true
    agents:
      reviewer: false  # 跳过审查
      tester: false    # 跳过测试
    max_iterations: 3
  
  safe:  # 安全模式
    enabled: true
    agents:
      reviewer: true
      tester: true
    max_iterations: 5
    require_human_approval: true
  
  custom:  # 自定义
    # 用户自定义配置
```

---

#### 1.2 命令行开关（临时）

```bash
# 单次会话启用
opencode --jcode --jcode-mode=safe

# 单次会话禁用
opencode --no-jcode

# 使用预设
opencode --jcode-preset=fast
```

---

#### 1.3 会话内开关（动态）

```
用户：/jcode enable
系统：JCode 已启用 (safe 模式)

用户：/jcode disable
系统：JCode 已禁用（本次会话）

用户：/jcode status
系统：JCode 状态：启用 (safe 模式)
      - Analyst: ✓
      - Planner: ✓
      - Implementer: ✓
      - Reviewer: ✓
      - Tester: ✓
      - Conductor: ✓
```

---

### 2. 开关粒度

#### Level 1: 全局开关
```yaml
jcode:
  enabled: true  # 完全启用/禁用
```

**效果**：
- `true` → 完整 JCode 流程
- `false` → OMO 原生模式（无治理层）

---

#### Level 2: 模式开关
```yaml
jcode:
  mode: "full"  # full | light | none
  
presets:
  full:   # 完整模式
    all_agents: true
    max_iterations: 5
    
  light:  # 轻量模式
    reviewer: false  # 跳过审查
    tester: false    # 跳过测试
    max_iterations: 3
    
  none:   # 禁用
    enabled: false
```

---

#### Level 3: Agent 级开关
```yaml
jcode:
  agents:
    analyst: true    # 启用分析
    planner: true    # 启用规划
    implementer: true
    reviewer: false  # 跳过审查
    tester: false    # 跳过测试
    conductor: true
```

**效果**：自定义治理流程
```
任务 → Analyst → Planner → Implementer → (跳过 Reviewer/Tester) → Conductor
```

---

#### Level 4: 规则级开关
```yaml
jcode:
  rules:
    constitution:
      R001_no_skip_review: false  # 允许跳过审查
      R002_require_test: false    # 允许无测试
      R003_audit_required: true   # 审计必须启用
```

---

### 3. 开关状态持久化

#### 3.1 存储位置
```
.omc/jcode_state.json  # 当前会话状态
.jcode/config.yaml     # 项目级配置
~/.jcode/config.yaml   # 用户级配置（全局默认）
```

#### 3.2 优先级
```
会话内命令 > 项目配置 > 用户配置 > OMO 配置 > 默认值
```

#### 3.3 状态内容
```json
{
  "enabled": true,
  "mode": "safe",
  "session_id": "ses_abc123",
  "enabled_at": "2026-02-24T10:30:00Z",
  "enabled_by": "user@example.com",
  "project": "jcode",
  "agents": {
    "analyst": true,
    "planner": true,
    "implementer": true,
    "reviewer": true,
    "tester": true,
    "conductor": true
  }
}
```

---

### 4. 开关 UI 设计（如果 OMO 有界面）

#### 4.1 状态栏指示器
```
┌─────────────────────────────────────────┐
│  OMO + JCode  ✓  [safe 模式]      [⚙]  │
└─────────────────────────────────────────┘
```

#### 4.2 开关面板
```
┌─────────────────────────────────────────┐
│  JCode 治理层                            │
│                                         │
│  [✓] 启用 JCode                         │
│                                         │
│  模式：○ 完整  ● 轻量  ○ 自定义         │
│                                         │
│  Agent 开关：                           │
│  [✓] Analyst   [✓] Planner              │
│  [✓] Implementer [✓] Reviewer           │
│  [✓] Tester    [✓] Conductor            │
│                                         │
│  [保存] [重置] [关闭]                   │
└─────────────────────────────────────────┘
```

---

### 5. 安全限制

#### 5.1 强制启用场景

某些场景**必须启用 JCode**，即使开关为 false：

```yaml
forced_enable_conditions:
  - file_pattern: "**/config/**"      # 配置文件
  - file_pattern: "**/*secret*"       # 敏感文件
  - operation_type: "delete_file"     # 删除操作
  - operation_type: "modify_permission" # 权限修改
```

**处理逻辑**：
```python
if should_force_jcode(file_path, operation):
    if not jcode_enabled:
        log_warning("JCode 强制启用（敏感操作）")
        jcode_enabled = True  # 临时启用
```

---

#### 5.2 开关变更审计

```json
{
  "log_id": "JCODE-SWITCH-20260224-001",
  "timestamp": "2026-02-24T10:30:00Z",
  "actor": "user@example.com",
  "action": "JCODE_SWITCH_CHANGE",
  "details": {
    "from": {"enabled": true, "mode": "safe"},
    "to": {"enabled": false, "mode": "none"},
    "reason": "快速原型开发"
  },
  "project": "jcode"
}
```

---

### 6. 默认值策略

#### 6.1 推荐默认值

| 用户类型 | 推荐默认值 | 理由 |
|---|---|---|
| **新用户** | enabled=true, mode=light | 平衡体验与性能 |
| **企业用户** | enabled=true, mode=safe | 质量优先 |
| **个人开发者** | enabled=false | 速度优先 |
| **合规项目** | enabled=true, mode=full | 强制审计 |

#### 6.2 智能默认值

```yaml
# 根据项目类型自动选择
auto_mode_detection:
  financial_project: "full"     # 金融项目 → 完整模式
  healthcare_project: "full"    # 医疗项目 → 完整模式
  prototype_project: "light"    # 原型项目 → 轻量模式
  personal_project: "none"      # 个人项目 → 禁用
```

---

### 7. 开关实现架构

```
┌─────────────────────────────────────────────────────────┐
│                    OMO Core                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  JCode Switch Manager                             │  │
│  │  • 读取配置（优先级处理）                         │  │
│  │  • 状态管理（会话/项目/用户）                     │  │
│  │  • 强制启用检测                                   │  │
│  │  • 审计日志                                       │  │
│  └───────────────────────────────────────────────────┘  │
│                            │                              │
│                            ▼                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  JCode Governance Layer (条件加载)                │  │
│  │  • 如果 enabled=true → 加载 6 Agent               │  │
│  │  • 如果 enabled=false → 绕过治理层                │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 新增任务

### Task 9. 创建 JCODE_SWITCH.md - 开关机制设计

**What to do**:
- 定义开关配置格式（YAML/JSON）
- 定义开关优先级规则
- 定义强制启用场景
- 定义开关状态持久化方案
- 定义审计日志格式（开关变更）
- 提供 Python 实现示例
- 定义 CLI 命令格式
- 定义 UI 交互方案（如果适用）

**References**:
- `governance/OMO_INTEGRATION.md` - 配置集成章节
- `governance/HUMAN_INTERFACE.md` - 人类介入机制

---

### Task 10. 更新 OMO_INTEGRATION.md - 增加开关章节

**What to do**:
- 在配置集成章节增加开关配置
- 增加开关与 MCP 集成的说明
- 增加开关状态查询的 MCP Tool 定义

---

### Task 11. 更新 AGENTS.md - 增加开关说明

**What to do**:
- 在 WHERE TO LOOK 增加开关配置索引
- 在 NOTES 增加 v3.0 开关功能说明

---

## 配置示例汇总

### 完整配置示例

```yaml
# .omo/config.yaml

jcode:
  # 全局开关
  enabled: true
  
  # 模式选择
  mode: "custom"  # full | light | safe | fast | custom
  
  # Agent 级开关
  agents:
    analyst: true
    planner: true
    implementer: true
    reviewer: true
    tester: false  # 快速模式跳过测试
    conductor: true
  
  # 迭代限制
  max_iterations: 3
  
  # 强制启用场景
  forced_enable:
    file_patterns:
      - "**/config/**"
      - "**/*secret*"
    operations:
      - delete_file
      - modify_permission
  
  # 审计
  audit:
    log_switch_changes: true
    retention_days: 90
```

---

## 使用场景

### 场景 1：快速原型开发

```bash
# 命令行禁用 JCode
opencode --no-jcode

# 或会话内禁用
/jcode disable

# 结果：OMO 原生模式，无治理层，速度最快
```

---

### 场景 2：生产代码开发

```bash
# 启用安全模式
opencode --jcode --jcode-mode=safe

# 或会话内启用
/jcode enable safe

# 结果：完整治理流程，质量优先
```

---

### 场景 3：团队协作

```yaml
# 项目配置 (.jcode/config.yaml)
enabled: true
mode: full
agents:
  reviewer: true  # 必须审查
  tester: true    # 必须测试

# 团队成员自动继承项目配置
```

---

### 场景 4：敏感操作

```yaml
# 即使全局禁用，敏感操作自动启用
enabled: false
forced_enable:
  file_patterns:
    - "**/config/**"

# 修改 config.py 时自动启用 JCode
```

---

## 成功标准

- [ ] 配置文件格式明确
- [ ] CLI 命令定义完整
- [ ] 优先级规则清晰
- [ ] 强制启用场景定义
- [ ] 审计日志格式完整
- [ ] 实现示例可用
- [ ] 文档更新完成

---

**END OF JCODE_SWITCH_DESIGN**
