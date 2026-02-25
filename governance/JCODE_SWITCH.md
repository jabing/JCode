# JCODE_SWITCH — JCode 启用开关机制

> Status: **DESIGN DRAFT**
> Scope: 4-level enablement switch for JCode integration
> Purpose: Define how users control JCode governance layer in OMO

---

## 0. 设计目标

JCode v3.0 引入 4 级启用开关，让用户在 **开发效率** 与 **代码质量** 之间灵活平衡：

> **JCode 可选，但关键时刻不可逃避。**

**核心原则**：
1. 用户可自由开关 JCode（除强制场景）
2. 配置支持多级覆盖（会话 > 项目 > 用户 > OMO）
3. 敏感操作强制启用 JCode（安全优先）
4. 所有开关变更必须审计

---

## 1. 4 级开关体系

### Level 1: 全局开关（Global Switch）

**定义**：控制 JCode 治理层是否启用

**配置位置**：
```yaml
# .omo/config.yaml 或 .jcode/config.yaml
jcode:
  enabled: true  # true | false
```

**行为**：
- `true` → 加载 JCode 治理层（6-Agent 系统）
- `false` → 绕过 JCode，OMO 原生模式工作

**例外**：强制启用场景（见 §4）仍会触发 JCode

---

### Level 2: 模式开关（Mode Switch）

**定义**：预设不同的治理强度

**配置位置**：
```yaml
jcode:
  mode: "full"  # full | light | safe | fast | custom
```

**模式定义**：

| 模式 | Analyst | Planner | Implementer | Reviewer | Tester | Conductor | Max Iterations |
|------|---------|---------|-------------|----------|--------|-----------|----------------|
| **full** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| **light** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 3 |
| **safe** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| **fast** | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | 2 |
| **custom** | ✓ | ✓ | ✓ | 用户配置 | 用户配置 | ✓ | 用户配置 |

**模式说明**：
- **full**：完整治理流程，所有 Agent 启用，5 次迭代限制
- **light**：轻量模式，3 次迭代限制，适合快速迭代
- **safe**：安全模式，启用所有 Agent + 强制人类介入
- **fast**：快速模式，跳过 Tester，2 次迭代限制（仅用于原型）
- **custom**：自定义模式，用户在 Level 3/4 中精确控制

---

### Level 3: Agent 级开关（Agent-Level Switch）

**定义**：精确控制每个 Agent 的启用状态

**配置位置**：
```yaml
jcode:
  agents:
    analyst: true      # 问题分析（司马迁）
    planner: true      # 任务规划（商鞅）
    implementer: true  # 代码实现（鲁班）
    reviewer: true     # 合规审查（包拯）
    tester: true       # 证据验证（张衡）
    conductor: true   # 终局裁决（韩非子）
```

**约束**：
- `analyst`、`planner`、`implementer`、`conductor` 不能同时禁用（否则流程断裂）
- `reviewer` 或 `tester` 禁用后，`conductor` 必须启用（作为兜底）

**无效组合示例**：
```yaml
# ❌ 流程断裂（无实现者）
agents:
  implementer: false
  conductor: false

# ❌ 无审查与测试，无兜底（危险）
agents:
  reviewer: false
  tester: false
  conductor: false
```

---

### Level 4: 规则级开关（Rule-Level Switch）

**定义**：控制宪法规则和治理规则是否启用

**配置位置**：
```yaml
jcode:
  rules:
    # 宪法规则
    constitution:
      R001_no_skip_review: true        # 禁止跳过审查
      R002_require_test: true          # 要求测试证据
      R003_nfr_required: true          # 要求非功能性需求
      R004_human_intervention_on_error: true  # 错误时强制介入

    # 治理规则
    governance:
      G001_audit_logging: true         # 审计日志
      G002_iteration_tracking: true    # 迭代追踪
      G003_context_lock_required: true # 上下文锁定
```

**行为**：
- `true` → 规则生效，违反规则触发相应流程
- `false` → 规则忽略，但审计日志仍记录规则禁用状态

**警告**：禁用宪法规则可能导致治理失效，仅在特殊场景使用

---

## 2. 配置优先级规则

### 2.1 优先级层级

```
会话内命令 > 项目配置 > 用户配置 > OMO 配置 > 默认值
```

| 优先级 | 配置源 | 文件路径 | 有效范围 |
|--------|--------|----------|----------|
| 1 | 会话内命令 | CLI 参数或会话命令 | 当前会话 |
| 2 | 项目配置 | `.jcode/config.yaml` | 当前项目 |
| 3 | 用户配置 | `~/.jcode/config.yaml` | 用户全局 |
| 4 | OMO 配置 | `.omo/config.yaml` | OMO 默认 |
| 5 | 默认值 | 系统内置 | 兜底 |

### 2.2 合并规则

**合并逻辑**：高优先级配置**覆盖**低优先级配置

```python
def resolve_jcode_config(cli_args, project_config, user_config, omo_config):
    """解析 JCode 配置（优先级从高到低）"""

    # 从默认值开始
    config = DEFAULT_JCODE_CONFIG

    # 逐层覆盖
    config = merge_config(config, omo_config)        # Level 4
    config = merge_config(config, user_config)       # Level 3
    config = merge_config(config, project_config)    # Level 2
    config = merge_config(config, cli_args)          # Level 1

    return config
```

**合并示例**：

```yaml
# OMO 配置（.omo/config.yaml）
jcode:
  enabled: true
  mode: full
  agents:
    tester: true

# 用户配置（~/.jcode/config.yaml）
jcode:
  mode: light           # 覆盖 OMO 的 mode
  agents:
    tester: false        # 覆盖 OMO 的 tester

# 项目配置（.jcode/config.yaml）
jcode:
  agents:
    reviewer: false     # 覆盖用户配置的 reviewer（新增）

# 最终结果
enabled: true           # 继承自 OMO
mode: light            # 继承自用户配置
agents:
  analyst: true         # 继承自默认值
  planner: true        # 继承自默认值
  implementer: true    # 继承自默认值
  reviewer: false      # 继承自项目配置
  tester: false        # 继承自用户配置
  conductor: true      # 继承自默认值
```

---

## 3. 配置格式定义

### 3.1 YAML 配置格式

**完整配置示例**：

```yaml
# .omo/config.yaml 或 .jcode/config.yaml

jcode:
  # Level 1: 全局开关
  enabled: true

  # Level 2: 模式选择
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
    constitution:
      R001_no_skip_review: true
      R002_require_test: true
      R003_nfr_required: true
      R004_human_intervention_on_error: true

    governance:
      G001_audit_logging: true
      G002_iteration_tracking: true
      G003_context_lock_required: true

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

  # 审计配置
  audit:
    log_switch_changes: true
    log_forced_enable: true
    retention_days: 90
```

### 3.2 JSON 配置格式

**等价 JSON 示例**：

```json
{
  "jcode": {
    "enabled": true,
    "mode": "full",
    "agents": {
      "analyst": true,
      "planner": true,
      "implementer": true,
      "reviewer": true,
      "tester": true,
      "conductor": true
    },
    "rules": {
      "constitution": {
        "R001_no_skip_review": true,
        "R002_require_test": true,
        "R003_nfr_required": true,
        "R004_human_intervention_on_error": true
      },
      "governance": {
        "G001_audit_logging": true,
        "G002_iteration_tracking": true,
        "G003_context_lock_required": true
      }
    },
    "max_iterations": 5,
    "forced_enable": {
      "file_patterns": [
        "**/config/**",
        "**/*secret*",
        "**/*.env"
      ],
      "operations": [
        "delete_file",
        "modify_permission",
        "database_migration"
      ]
    },
    "audit": {
      "log_switch_changes": true,
      "log_forced_enable": true,
      "retention_days": 90
    }
  }
}
```

---

## 4. 强制启用场景

### 4.1 强制启用条件

**定义**：某些敏感场景**必须启用 JCode**，即使全局开关为 `false`

**配置位置**：
```yaml
jcode:
  forced_enable:
    file_patterns:
      - "**/config/**"          # 配置文件目录
      - "**/*secret*"           # 包含 "secret" 的文件
      - "**/*.env"               # 环境变量文件
      - "**/secrets.yaml"        # 密钥配置
      - "**/credentials.json"    # 凭证文件

    operations:
      - delete_file              # 删除文件
      - modify_permission        # 修改权限
      - database_migration       # 数据库迁移
      - deploy_production        # 生产部署
```

### 4.2 强制启用逻辑

**判定流程**：

```python
def should_force_enable_jcode(file_path, operation, config):
    """判断是否需要强制启用 JCode"""

    if not config.forced_enable:
        return False

    # 检查文件模式匹配
    for pattern in config.forced_enable.file_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            log_warning(f"JCode 强制启用：文件匹配模式 {pattern}")
            return True

    # 检查操作类型匹配
    if operation in config.forced_enable.operations:
        log_warning(f"JCode 强制启用：操作类型 {operation}")
        return True

    return False
```

**强制启用行为**：

```python
def execute_with_jcode_check(file_path, operation, user_config):
    """执行操作前检查是否需要强制启用 JCode"""

    # 用户配置中 JCode 可能禁用
    jcode_enabled = user_config.enabled

    # 检查强制启用条件
    if should_force_enable_jcode(file_path, operation, user_config):
        if not jcode_enabled:
            # 记录强制启用
            log_forced_enable_event(file_path, operation)

            # 临时启用 JCode（本次操作）
            jcode_enabled = True

    # 执行操作
    if jcode_enabled:
        return execute_with_jcode_governance(file_path, operation)
    else:
        return execute_without_jcode(file_path, operation)
```

### 4.3 强制启用审计

**审计日志格式**：

```json
{
  "log_id": "JCODE-FORCED-20260224-001",
  "timestamp": "2026-02-24T10:30:00Z",
  "event_type": "FORCED_ENABLE",
  "trigger": {
    "type": "file_pattern",
    "pattern": "**/config/**",
    "file_path": "config/production.yaml"
  },
  "original_config": {
    "enabled": false,
    "mode": "none"
  },
  "action": "临时启用 JCode（本次操作）",
  "user": "user@example.com",
  "project": "myapp"
}
```

---

## 5. CLI 命令格式

### 5.1 全局开关命令

```bash
# 启用 JCode（使用默认模式）
opencode --jcode

# 禁用 JCode
opencode --no-jcode
```

### 5.2 模式选择命令

```bash
# 启用 JCode 并指定模式
opencode --jcode --jcode-mode=full
opencode --jcode --jcode-mode=light
opencode --jcode --jcode-mode=safe
opencode --jcode --jcode-mode=fast
opencode --jcode --jcode-mode=custom

# 使用预设
opencode --jcode-preset=full
opencode --jcode-preset=safe
opencode --jcode-preset=fast
```

### 5.3 Agent 级开关命令

```bash
# 禁用特定 Agent
opencode --jcode --jcode-disable-tester
opencode --jcode --jcode-disable-reviewer

# 启用特定 Agent
opencode --jcode --jcode-enable-tester
opencode --jcode --jcode-enable-reviewer
```

### 5.4 会话内命令

```bash
# 启用 JCode
/jcode enable
/jcode enable safe
/jcode enable fast

# 禁用 JCode（本次会话）
/jcode disable

# 查看当前状态
/jcode status

# 切换 Agent
/jcode agent enable tester
/jcode agent disable reviewer
```

**状态输出示例**：

```
$ /jcode status

JCode 状态：启用 (safe 模式)

全局开关：enabled
当前模式：safe
最大迭代：5

Agent 状态：
  ✓ Analyst      [问题分析]
  ✓ Planner      [任务规划]
  ✓ Implementer  [代码实现]
  ✓ Reviewer     [合规审查]
  ✓ Tester       [证据验证]
  ✓ Conductor    [终局裁决]

规则开关：
  ✓ R001_no_skip_review
  ✓ R002_require_test
  ✓ R003_nfr_required
  ✓ R004_human_intervention_on_error
```

---

## 6. UI 交互方案（如果 OMO 有界面）

### 6.1 状态栏指示器

```
┌─────────────────────────────────────────────────────────────┐
│  OMO + JCode  ✓  [safe 模式]              [⚙]  [🔍]         │
└─────────────────────────────────────────────────────────────┘
```

**状态指示**：
- ✓ 绿色：JCode 启用
- ⚠ 黄色：JCode 部分启用（某些 Agent 禁用）
- ✗ 红色：JCode 禁用（或强制启用场景触发）

### 6.2 开关面板

```
┌─────────────────────────────────────────────────────────────┐
│  JCode 治理层                                                 │
│                                                               │
│  [✓] 启用 JCode                                               │
│                                                               │
│  模式选择：                                                   │
│  ○ 完整 (full)     所有 Agent 启用，5 次迭代                 │
│  ● 轻量 (light)    核心流程，3 次迭代                        │
│  ○ 安全 (safe)     全部启用 + 强制人类介入                   │
│  ○ 快速 (fast)     跳过测试，2 次迭代（仅原型）             │
│  ○ 自定义 (custom) 手动配置 Agent 和规则                    │
│                                                               │
│  Agent 开关：                                                 │
│  [✓] Analyst      [✓] Planner    [✓] Implementer            │
│  [✓] Reviewer     [✓] Tester     [✓] Conductor              │
│                                                               │
│  规则开关：                                                   │
│  [✓] R001 禁止跳过审查                                       │
│  [✓] R002 要求测试证据                                       │
│  [✓] R003 要求非功能性需求                                   │
│  [✓] R004 错误时强制介入                                     │
│                                                               │
│  迭代限制：[ 5 ] 次                                           │
│                                                               │
│  [保存配置] [恢复默认] [重置] [关闭]                          │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 快速切换菜单

```
┌─────────────────────────────────────────────────────────────┐
│  JCode 快速切换                                               │
│                                                               │
│  [快速模式]      [安全模式]      [禁用 JCode]                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. 状态持久化

### 7.1 存储位置

```
.omc/jcode_state.json    # 当前会话状态（临时）
.jcode/config.yaml       # 项目级配置（永久）
~/.jcode/config.yaml     # 用户级配置（全局默认）
```

### 7.2 会话状态格式

```json
{
  "session_id": "ses_abc123",
  "enabled": true,
  "mode": "safe",
  "enabled_at": "2026-02-24T10:30:00Z",
  "enabled_by": "user@example.com",
  "project": "jcode",
  "config_source": "cli",  # cli | session_command | project_config | user_config | omo_config
  "agents": {
    "analyst": true,
    "planner": true,
    "implementer": true,
    "reviewer": true,
    "tester": true,
    "conductor": true
  },
  "rules": {
    "R001_no_skip_review": true,
    "R002_require_test": true
  }
}
```

### 7.3 持久化策略

| 配置源 | 持久化 | 有效范围 | 示例 |
|--------|--------|----------|------|
| CLI 参数 | 否 | 当前会话 | `--jcode-mode=safe` |
| 会话命令 | 是 | 当前会话 | `/jcode enable` |
| 项目配置 | 是 | 项目所有会话 | `.jcode/config.yaml` |
| 用户配置 | 是 | 用户所有项目 | `~/.jcode/config.yaml` |
| OMO 配置 | 是 | OMO 默认 | `.omo/config.yaml` |

---

## 8. 审计日志格式

### 8.1 开关变更日志

```json
{
  "log_id": "JCODE-SWITCH-20260224-001",
  "timestamp": "2026-02-24T10:30:00Z",
  "event_type": "SWITCH_CHANGE",
  "actor": "user@example.com",
  "action": "ENABLE_JCODE",
  "details": {
    "from": {
      "enabled": false,
      "mode": "none",
      "config_source": "omo_config"
    },
    "to": {
      "enabled": true,
      "mode": "safe",
      "config_source": "cli"
    },
    "reason": "用户手动启用"
  },
  "session_id": "ses_abc123",
  "project": "myapp"
}
```

### 8.2 Agent 开关变更日志

```json
{
  "log_id": "JCODE-AGENT-20260224-002",
  "timestamp": "2026-02-24T11:00:00Z",
  "event_type": "AGENT_SWITCH_CHANGE",
  "actor": "user@example.com",
  "action": "DISABLE_AGENT",
  "details": {
    "agent": "tester",
    "from": true,
    "to": false,
    "reason": "快速模式原型开发"
  },
  "session_id": "ses_abc123",
  "project": "myapp"
}
```

### 8.3 规则开关变更日志

```json
{
  "log_id": "JCODE-RULE-20260224-003",
  "timestamp": "2026-02-24T11:30:00Z",
  "event_type": "RULE_SWITCH_CHANGE",
  "actor": "user@example.com",
  "action": "DISABLE_RULE",
  "details": {
    "rule": "R002_require_test",
    "from": true,
    "to": false,
    "reason": "测试环境暂时不可用"
  },
  "session_id": "ses_abc123",
  "project": "myapp"
}
```

### 8.4 日志存储

**存储位置**：
```yaml
audit/
  ├── jcode_switch_changes.jsonl      # 开关变更日志
  ├── jcode_agent_changes.jsonl       # Agent 开关变更
  ├── jcode_rule_changes.jsonl        # 规则开关变更
  └── jcode_forced_enable.jsonl       # 强制启用事件
```

**日志格式**：JSON Lines（每行一条记录）

**保留策略**：默认 90 天，可配置

---

## 9. Python 实现示例

### 9.1 配置解析器

```python
import yaml
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ForcedEnableConfig:
    file_patterns: List[str]
    operations: List[str]


@dataclass
class AuditConfig:
    log_switch_changes: bool = True
    log_forced_enable: bool = True
    retention_days: int = 90


@dataclass
class JCodeConfig:
    enabled: bool = True
    mode: str = "full"
    agents: Dict[str, bool] = None
    rules: Dict[str, Dict[str, bool]] = None
    max_iterations: int = 5
    forced_enable: ForcedEnableConfig = None
    audit: AuditConfig = None

    def __post_init__(self):
        if self.agents is None:
            self.agents = {
                "analyst": True,
                "planner": True,
                "implementer": True,
                "reviewer": True,
                "tester": True,
                "conductor": True
            }
        if self.rules is None:
            self.rules = {
                "constitution": {
                    "R001_no_skip_review": True,
                    "R002_require_test": True,
                    "R003_nfr_required": True,
                    "R004_human_intervention_on_error": True
                }
            }
        if self.forced_enable is None:
            self.forced_enable = ForcedEnableConfig(
                file_patterns=["**/config/**", "**/*secret*", "**/*.env"],
                operations=["delete_file", "modify_permission", "database_migration"]
            )
        if self.audit is None:
            self.audit = AuditConfig()


class JCodeConfigResolver:
    """JCode 配置解析器（支持优先级合并）"""

    DEFAULT_CONFIG = JCodeConfig()

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.user_config_path = Path.home() / ".jcode" / "config.yaml"
        self.project_config_path = project_root / ".jcode" / "config.yaml"
        self.omo_config_path = project_root / ".omo" / "config.yaml"

    def resolve(self, cli_args: Optional[Dict] = None) -> JCodeConfig:
        """解析配置（优先级：CLI > 项目 > 用户 > OMO > 默认）"""

        config = self.DEFAULT_CONFIG

        # 逐层合并
        config = self._merge_config(config, self._load_omo_config())
        config = self._merge_config(config, self._load_user_config())
        config = self._merge_config(config, self._load_project_config())
        config = self._merge_config(config, self._parse_cli_args(cli_args or {}))

        return config

    def _load_omo_config(self) -> Optional[JCodeConfig]:
        """加载 OMO 配置"""
        if not self.omo_config_path.exists():
            return None

        with open(self.omo_config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return self._dict_to_config(data.get('jcode', {}))

    def _load_user_config(self) -> Optional[JCodeConfig]:
        """加载用户配置"""
        if not self.user_config_path.exists():
            return None

        with open(self.user_config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return self._dict_to_config(data.get('jcode', {}))

    def _load_project_config(self) -> Optional[JCodeConfig]:
        """加载项目配置"""
        if not self.project_config_path.exists():
            return None

        with open(self.project_config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return self._dict_to_config(data.get('jcode', {}))

    def _parse_cli_args(self, cli_args: Dict) -> Optional[JCodeConfig]:
        """解析 CLI 参数"""
        if not cli_args:
            return None

        config_data = {}

        if 'jcode' in cli_args:
            config_data['enabled'] = cli_args['jcode']

        if 'jcode_mode' in cli_args:
            config_data['mode'] = cli_args['jcode_mode']

        if 'jcode_disable_tester' in cli_args and cli_args['jcode_disable_tester']:
            if config_data.get('agents') is None:
                config_data['agents'] = {}
            config_data['agents']['tester'] = False

        return self._dict_to_config(config_data) if config_data else None

    def _merge_config(self, base: JCodeConfig, override: Optional[JCodeConfig]) -> JCodeConfig:
        """合并配置（override 覆盖 base）"""
        if override is None:
            return base

        # 简单字段直接覆盖
        if override.enabled is not None:
            base.enabled = override.enabled
        if override.mode:
            base.mode = override.mode
        if override.max_iterations:
            base.max_iterations = override.max_iterations

        # 嵌套字典合并
        if override.agents:
            for agent, enabled in override.agents.items():
                base.agents[agent] = enabled

        if override.rules:
            for category, rules in override.rules.items():
                if category not in base.rules:
                    base.rules[category] = {}
                base.rules[category].update(rules)

        return base

    def _dict_to_config(self, data: Dict) -> JCodeConfig:
        """将字典转换为 JCodeConfig"""
        return JCodeConfig(
            enabled=data.get('enabled'),
            mode=data.get('mode'),
            agents=data.get('agents'),
            rules=data.get('rules'),
            max_iterations=data.get('max_iterations'),
            forced_enable=ForcedEnableConfig(
                file_patterns=data.get('forced_enable', {}).get('file_patterns', []),
                operations=data.get('forced_enable', {}).get('operations', [])
            ) if 'forced_enable' in data else None,
            audit=AuditConfig(
                log_switch_changes=data.get('audit', {}).get('log_switch_changes', True),
                log_forced_enable=data.get('audit', {}).get('log_forced_enable', True),
                retention_days=data.get('audit', {}).get('retention_days', 90)
            ) if 'audit' in data else None
        )
```

### 9.2 开关管理器

```python
import fnmatch
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class JCodeSwitchManager:
    """JCode 开关管理器"""

    def __init__(self, config: JCodeConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        self.audit_log_path = project_root / ".omc" / "jcode_switch_changes.jsonl"
        self.forced_enable_log_path = project_root / ".omc" / "jcode_forced_enable.jsonl"

    def should_enable_jcode(self, file_path: Optional[str] = None, operation: Optional[str] = None) -> bool:
        """判断是否应该启用 JCode（考虑强制启用）"""

        # 检查全局开关
        if self.config.enabled:
            return True

        # 检查强制启用条件
        if self._should_force_enable(file_path, operation):
            return True

        return False

    def _should_force_enable(self, file_path: Optional[str], operation: Optional[str]) -> bool:
        """判断是否需要强制启用"""
        if not file_path and not operation:
            return False

        # 检查文件模式匹配
        if file_path:
            for pattern in self.config.forced_enable.file_patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    self._log_forced_enable_event("file_pattern", pattern, file_path)
                    return True

        # 检查操作类型匹配
        if operation and operation in self.config.forced_enable.operations:
            self._log_forced_enable_event("operation", operation, file_path)
            return True

        return False

    def is_agent_enabled(self, agent: str) -> bool:
        """检查 Agent 是否启用"""
        return self.config.agents.get(agent, False)

    def is_rule_enabled(self, rule: str) -> bool:
        """检查规则是否启用"""
        for category in self.config.rules.values():
            if rule in category:
                return category[rule]
        return False

    def log_switch_change(self, action: str, from_state: Dict, to_state: Dict, reason: str = ""):
        """记录开关变更"""
        if not self.config.audit.log_switch_changes:
            return

        log_entry = {
            "log_id": f"JCODE-SWITCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "event_type": "SWITCH_CHANGE",
            "actor": "system",  # TODO: 获取实际用户
            "action": action,
            "details": {
                "from": from_state,
                "to": to_state,
                "reason": reason
            },
            "session_id": "unknown",  # TODO: 获取会话 ID
            "project": self.project_root.name
        }

        self._append_to_log(self.audit_log_path, log_entry)

    def _log_forced_enable_event(self, trigger_type: str, trigger_value: str, file_path: Optional[str]):
        """记录强制启用事件"""
        if not self.config.audit.log_forced_enable:
            return

        log_entry = {
            "log_id": f"JCODE-FORCED-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "event_type": "FORCED_ENABLE",
            "trigger": {
                "type": trigger_type,
                "value": trigger_value,
                "file_path": file_path
            },
            "original_config": {
                "enabled": self.config.enabled,
                "mode": self.config.mode
            },
            "action": "临时启用 JCode（本次操作）",
            "user": "system",  # TODO: 获取实际用户
            "project": self.project_root.name
        }

        self._append_to_log(self.forced_enable_log_path, log_entry)

    def _append_to_log(self, log_path: Path, log_entry: Dict):
        """追加日志条目"""
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


# 使用示例
if __name__ == "__main__":
    project_root = Path("C:/dev_projects/jcode")
    resolver = JCodeConfigResolver(project_root)
    config = resolver.resolve()

    switch_manager = JCodeSwitchManager(config, project_root)

    # 检查是否启用 JCode
    print(f"JCode enabled: {switch_manager.should_enable_jcode()}")

    # 检查敏感文件操作
    print(f"JCode enabled for config file: {switch_manager.should_enable_jcode('config/production.yaml', 'modify_permission')}")

    # 检查 Agent 状态
    print(f"Analyst enabled: {switch_manager.is_agent_enabled('analyst')}")
    print(f"Tester enabled: {switch_manager.is_agent_enabled('tester')}")
```

---

## 10. 使用示例

### 示例 1：快速原型开发

**场景**：开发初期快速迭代，跳过 JCode

```bash
# 方式 1：命令行禁用
$ opencode --no-jcode

# 方式 2：会话内禁用
$ /jcode disable

# 结果：JCode 禁用，OMO 原生模式工作
```

---

### 示例 2：生产代码开发

**场景**：生产环境代码，需要完整治理

```bash
# 启用安全模式
$ opencode --jcode --jcode-mode=safe

# 或会话内启用
$ /jcode enable safe

# 结果：完整治理流程，质量优先
```

---

### 示例 3：团队协作

**场景**：项目配置强制启用 JCode

```yaml
# .jcode/config.yaml

jcode:
  enabled: true
  mode: full

  agents:
    reviewer: true  # 必须审查
    tester: true    # 必须测试
```

**行为**：团队成员自动继承项目配置，无法绕过

---

### 示例 4：敏感操作

**场景**：修改配置文件，自动启用 JCode

```yaml
# .omo/config.yaml（用户可能禁用 JCode）

jcode:
  enabled: false

  forced_enable:
    file_patterns:
      - "**/config/**"
```

**行为**：
```bash
$ opencode modify config/production.yaml

# 系统输出：
# WARNING: JCode 强制启用（文件匹配模式 **/config/**）
# JCode 状态：启用（临时）

# 执行时启用 JCode 治理层
```

---

### 示例 5：自定义模式

**场景**：根据项目需求自定义 Agent 和规则

```yaml
# .jcode/config.yaml

jcode:
  enabled: true
  mode: custom

  agents:
    analyst: true
    planner: true
    implementer: true
    reviewer: true
    tester: false   # 跳过测试（测试环境暂时不可用）
    conductor: true

  rules:
    constitution:
      R001_no_skip_review: true
      R002_require_test: false   # 禁用测试要求
      R003_nfr_required: true
```

---

## 11. 约束与验证

### 11.1 配置验证规则

| 规则 | 违规后果 |
|------|----------|
| `analyst`、`planner`、`implementer`、`conductor` 不能同时禁用 | 配置拒绝加载，返回错误 |
| `reviewer` 和 `tester` 同时禁用时，`conductor` 必须启用 | 警告，但允许（需确认） |
| `mode` 必须是有效值（full/light/safe/fast/custom） | 降级为 `full` |
| `max_iterations` 必须 >= 1 | 降级为 5 |

### 11.2 审计要求

**必须记录**：
- 所有开关变更（启用/禁用/模式切换）
- Agent 开关变更
- 规则开关变更
- 强制启用事件

**必须包含**：
- 时间戳
- 操作者
- 变更原因
- 旧状态和新状态

---

## 12. 成功标准

- [x] 定义 4 级开关体系（全局、模式、Agent、规则）
- [x] 定义配置格式（YAML/JSON）
- [x] 定义配置优先级规则（会话 > 项目 > 用户 > OMO）
- [x] 定义强制启用场景（敏感文件/操作）
- [x] 定义审计日志格式（开关变更）
- [x] 提供 Python 实现示例
- [x] 定义 CLI 命令格式
- [x] 定义 UI 交互方案

---

## 13. 相关文档

- `governance/OMO_INTEGRATION.md` - OMO 集成架构
- `governance/HUMAN_INTERFACE.md` - 人机协作接口
- `.sisyphus/plans/jcode-switch-design.md` - 开关设计补充

---

## 封印语

> **JCode 可选，但关键时刻不可逃避。**
>
> 让用户选择何时使用 JCode，但在敏感操作时强制启用，平衡效率与安全。

---

**END OF JCODE_SWITCH**
