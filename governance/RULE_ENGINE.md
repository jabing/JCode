# RULE_ENGINE — MCP Tool Interface for OpenCode Superpowers Rule Engine

> Status: **DRAFT**  
> Scope: OpenCode Superpowers Rule Engine Integration  
> Purpose: Define MCP Tool interface for rule registration, execution, and violation handling

---

## 0. 协议定位

本协议定义 **Rule Engine MCP Tool**，为 OpenCode Superpowers 提供统一的规则治理能力接口。

JCode 作为 Agent 治理扩展层，通过 Rule Engine MCP Tool 实现：

- **规则注册**：注册 JCode宪法规则、快速修正规则等
- **规则执行**：在特定阶段（IMPLEMENTATION/REVIEW）触发规则检查
- **违规处理**：根据优先级（P0-P3）执行 TERMINATE/QUICK_FIX/LOG_ONLY

核心原则：
> **规则即代码，代码即法律。**

---

## 1. Rule Engine MCP Tool 概览

### 1.1 能力边界

| 能力 | Superpowers Rule Engine | JCode Agent |
|------|------------------------|-------------|
| 规则定义 | ✅ 提供规则引擎底层能力 | ✅ 定义业务规则（宪法规则、修正规则） |
| 规则注册 | ✅ 提供 tools/register 接口 | ✅ 注册预定义规则集 |
| 规则执行 | ✅ 提供 tools/call 执行规则 | ✅ 在特定阶段触发规则检查 |
| 违规处理 | ✅ 提供 notification/ops/priority | ✅ 根据优先级决定处理策略 |
| Soft Hooks | ✅ 提供 hooks API | ✅ 实现软性拦截机制 |

### 1.2 MCP Tool Schema

```json
{
  "name": "rule_engine",
  "title": "OpenCode Rule Engine",
  "description": "Unified rule governance for AI agent system",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["register", "execute", "check_violation"],
        "description": "Rule engine action"
      },
      "rule": {
        "type": "object",
        "description": "Rule definition (for registration)"
      },
      "phase": {
        "type": "string",
        "enum": ["ANALYSIS", "TASKS", "IMPLEMENTATION", "REVIEW", "TEST"],
        "description": "Execution phase"
      },
      "context": {
        "type": "object",
        "description": "Execution context data"
      }
    },
    "required": ["action"]
  }
}
```

---

## 2. 规则语法定义（YAML）

### 2.1 基础规则结构

```yaml
rule:
  id: "JCODE-001"                    # 唯一规则ID
  version: "1.0.0"                   # 规则版本
  severity: "CRITICAL"               # 优先级映射（P0-P3）
  category: "constitutional"         # 规则分类
  phase: "IMPLEMENTATION"            # 执行时机
  handler: " VIOLATION "             # 违规处理策略
  
  # 规则匹配条件
  match:
    pattern: "function.*\$\w+\("      # 正则表达式匹配
    file_patterns: ["*.py", "*.js"]   # 文件限定
    context_filter:                   # 上下文过滤
      agent_type: "Implementer"       # Agent类型
      task_status: "in_progress"      # 任务状态

  # 违规消息
  message: "Function name contains special characters"
  
  # 补充数据
  metadata:
    owner: "agentic-governance"
    doc_url: "https://github.com/.../RULE_ENGINE.md"
    last_updated: "2026-02-24"
```

### 2.2 规则优先级定义

| Priority | Severity | 处理策略 | 说明 |
|----------|----------|----------|------|
| P0 | CRITICAL | TERMINATE | 违反宪法/安全规则，立即终止 |
| P1 | HIGH | QUICK_FIX | 可快速修正的小问题，无需完整迭代 |
| P2 | MEDIUM | LOG_ONLY | 记录日志但不中断，用于监控 |
| P3 | LOW | SOFT_HOOK | 软性警告，可被忽略 |

### 2.3 优先级到处理策略映射

```yaml
priority_mapping:
  P0: 
    action: TERMINATE
    notify_human: true
    rollback: true
    iteration_penalty: +MAX
  
  P1:
    action: QUICK_FIX
    notify_human: false
    rollback: false
    iteration_penalty: +0
  
  P2:
    action: LOG_ONLY
    notify_human: false
    rollback: false
    iteration_penalty: +0
  
  P3:
    action: SOFT_HOOK
    notify_human: false
    rollback: false
    iteration_penalty: +0
```

---

## 3. 规则执行时机

### 3.1 执行阶段矩阵

| 阶段 | 可执行规则 | 说明 |
|------|-----------|------|
| ANALYSIS | 所有P0-P3 | 检查需求边界定义 |
| TASKS | P0-P2 | 检查任务可验证性 |
| IMPLEMENTATION | P0-P1 | 实现阶段强规则 |
| REVIEW | P0-P2 | 审查阶段合规检查 |
| TEST | P0-P3 | 测试规则验证 |

### 3.2 执行流程

```
[RECEIVE MCP request: tools/call]
        ↓
[PARSE action + rule_id + phase + context]
        ↓
[LOOKUP rule by rule_id]
        ↓
[EVALUATE: phase_allowed? && context_matches?]
        ↓
    [YES] → [EXECUTE match logic]
        ↓
    [NO] → [SKIP rule]
        ↓
[EVALUATE violation?]
        ↓
   [YES] → [CHECK priority]
        ↓
   [NO] → [PASS]
        ↓
[DETERMINE handler: TERMINATE/QUICK_FIX/LOG_ONLY/SOFT_HOOK]
        ↓
[EXECUTE handler + emit notification]
```

---

## 4. 违规处理机制

### 4.1 TERMINATE（P0）

**触发条件**：
- 违反宪法规则（角色越权、职责重叠）
- 安全违规（密码泄露、权限提升）

**处理流程**：
1. 暂停当前任务
2. 通知人类介入（HUMAN_ADMIN）
3. 记录审计日志
4. 触发回滚（rollback:

**示例**：
```yaml
rule:
  id: "CONSTITUTION-001"
  severity: "CRITICAL"
  phase: "ANALYSIS"
  message: "Agent attempted to suggest solution in ANALYSIS phase"
  handler: TERMINATE
  metadata:
    constitutional_basis: "AGENT_CONSTITUTION.md#三"
```

### 4.2 QUICK_FIX（P1）

**触发条件**：
- 拼写错误、格式问题
- 单点防御性检查缺失

**处理流程**：
1. 标记 MINOR_FIX 请求
2. 调用 QUICK_FIX_CHANNEL
3. Implementer执行修正
4. 轻量验证（不增加iteration）

**示例**：
```yaml
rule:
  id: "STYLE-001"
  severity: "HIGH"
  phase: "IMPLEMENTATION"
  message: "Variable name 'usreName' contains typo"
  handler: QUICK_FIX
  metadata:
    quick_fix_type: "TYPE-A"
    max_fixes: 5
```

### 4.3 LOG_ONLY（P2）

**触发条件**：
- 性能警告（循环嵌套过深）
- 可维护性建议（函数过长）

**处理流程**：
1. 记录到 audit/rule_violations.jsonl
2. 不中断任务
3. 用于统计分析

**示例**：
```yaml
rule:
  id: "PERF-001"
  severity: "MEDIUM"
  phase: "IMPLEMENTATION"
  message: "Function exceeds 50 lines"
  handler: LOG_ONLY
  metadata:
    metric_threshold: 50
```

### 4.4 SOFT_HOOK（P3）

**触发条件**：
- 最佳实践建议
- 非强制性提示

**处理流程**：
1. 添加 soft_hook 标记
2. Agent可选择忽略
3. 记录到 soft_hooks.log

**示例**：
```yaml
rule:
  id: "PRACTICE-001"
  severity: "LOW"
  phase: "REVIEW"
  message: "Consider adding type hints"
  handler: SOFT_HOOK
  metadata:
    enforceable: false
    priority_boost: true  # 可在高质量模式下提升优先级
```

---

## 5. Soft Hooks 机制

### 5.1 设计目标

Soft Hooks 提供 **可选的软性拦截**，适用于：
- 最佳实践建议
- 团队约定（非强制）
- 未来可升级为硬性规则

### 5.2 Soft Hooks 规则定义

```yaml
rule:
  id: "PRACTICE-001"
  severity: "LOW"
  phase: "IMPLEMENTATION"
  message: "Consider adding docstring for public function"
  handler: SOFT_HOOK
  
  # Soft Hooks 特定配置
  soft_hooks:
    enabled: true
    can_be_ignored: true
    notify_on_ignore: false
    priority_boost_phase: "REVIEW"  # REVIEW阶段提升为P2
    
    # Soft Hooks拦截器
    interceptors:
      - type: "referrer"
        config:
          threshold: 3  # 3次重复建议升级为P1
```

### 5.3 Soft Hooks 生命周期

```
[SOFT_HOOK triggered]
        ↓
[Agent chooses: IGNORE / COMPLY]
        ↓
    [IGNORE] → [increment ignore_count]
        ↓
    [COMPLY] → [remove soft_hook]
        ↓
[ignore_count >= threshold?]
        ↓
    [YES] → [UPGRADE to P2 + LOG_ONLY]
        ↓
    [NO] → [keep as SOFT_HOOK]
```

---

## 6. Rule Engine MCP Tool 调用协议

### 6.1 注册规则（tools/call）

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "rule_engine",
    "arguments": {
      "action": "register",
      "rule": {
        "id": "JCODE-001",
        "version": "1.0.0",
        "severity": "HIGH",
        "category": "constitutional",
        "phase": "IMPLEMENTATION",
        "handler": "QUICK_FIX",
        "match": {
          "pattern": "def [a-z_][a-zA-Z0-9_]*\\(",
          "file_patterns": ["*.py"]
        },
        "message": "Function name must follow snake_case",
        "metadata": {
          "owner": "agentic-governance"
        }
      }
    }
  }
}
```

### 6.2 执行规则检查（tools/list）

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {
    "phase": "IMPLEMENTATION"
  }
}
```

响应：
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "rule_engine:JCODE-001",
        "description": "Check snake_case function naming",
        "inputSchema": {
          "type": "object",
          "properties": {
            "code": {"type": "string"},
            "file": {"type": "string"}
          }
        },
        "annotations": {
          "phase": "IMPLEMENTATION",
          "severity": "HIGH",
          "handler": "QUICK_FIX"
        }
      }
    ]
  }
}
```

### 6.3 违规通知（notifications/ops/priority）

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/ops/priority",
  "params": {
    "rule_id": "JCODE-001",
    "violation": {
      "location": "src/parser.py:42",
      "message": "Function 'parse_Data' violates snake_case rule",
      "suggestion": "Rename to 'parse_data'"
    },
    "priority": "P1",
    "handler": "QUICK_FIX"
  }
}
```

---

## 7. Python 集成示例

### 7.1 规则引擎客户端

```python
# jcode/rules/engine.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Priority(Enum):
    P0 = "TERMINATE"
    P1 = "QUICK_FIX"
    P2 = "LOG_ONLY"
    P3 = "SOFT_HOOK"

@dataclass
class Rule:
    id: str
    version: str
    severity: str
    category: str
    phase: str
    handler: str
    pattern: str
    message: str
    metadata: dict

class RuleEngineClient:
    def __init__(self, mcp_client):
        self.mcp = mcp_client
    
    async def register_rule(self, rule: Rule) -> dict:
        """注册规则到 Rule Engine"""
        return await self.mcp.call("tools/call", {
            "name": "rule_engine",
            "arguments": {
                "action": "register",
                "rule": {
                    "id": rule.id,
                    "version": rule.version,
                    "severity": rule.severity,
                    "category": rule.category,
                    "phase": rule.phase,
                    "handler": rule.handler,
                    "match": {"pattern": rule.pattern},
                    "message": rule.message,
                    "metadata": rule.metadata
                }
            }
        })
    
    async def check_violation(self, code: str, phase: str) -> list:
        """检查代码违规"""
        rules = await self.mcp.call("tools/list", {"phase": phase})
        violations = []
        
        for tool in rules["tools"]:
            # Extract rule metadata from annotations
            annotations = tool.get("annotations", {})
            handler = annotations.get("handler", "LOG_ONLY")
            
            # Check if code matches rule pattern
            if self._matches_pattern(code, tool["inputSchema"]):
                violations.append({
                    "rule_id": tool["name"],
                    "handler": handler,
                    "annotations": annotations
                })
        
        return violations
    
    def _determine_action(self, violations: list) -> str:
        """根据最高优先级确定处理动作"""
        if not violations:
            return "PASS"
        
        highest_priority = max(
            [Priority[v["annotations"].get("severity", "LOW")]
             for v in violations]
        )
        return highest_priority.value
```

### 7.2 规则使用示例

```python
# jcode/rules/constitutional_rules.py
from .engine import Rule, RuleEngineClient

async def load_constitutional_rules(client: RuleEngineClient):
    """加载宪法规则"""
    
    # Rule 1: Agent role boundaries
    await client.register_rule(Rule(
        id="CONSTITUTION-001",
        version="1.0.0",
        severity="CRITICAL",
        category="constitutional",
        phase="ANALYSIS",
        handler="QUICK_FIX",
        pattern=r"Analyzer.*suggest|Planner.*implement",
        message="Agent attempted to exceed role boundaries",
        metadata={"human_in_loop": True}
    ))
    
    # Rule 2: No iteration without increment
    await client.register_rule(Rule(
        id="CONSTITUTION-002",
        version="1.0.0",
        severity="CRITICAL",
        category="process",
        phase="REVIEW",
        handler="TERMINATE",
        pattern=r"iteration\s*=\s*(\d+)(?!\s*\+\s*\+)",
        message="Iteration counter not incremented",
        metadata{"constitutional_basis": "AGENT_CONSTITUTION.md#六"}
    ))

# jcode/planner.py
from .rules.engine import RuleEngineClient

async def generate_tasks(self, analysis: dict) -> dict:
    """生成任务并应用规则检查"""
    
    # Check forviolations in task definitions
    tasks_yaml = self._tasks_to_yaml()
    violations = await self.rule_engine.check_violation(tasks_yaml, "TASKS")
    
    action = self.rule_engine._determine_action(violations)
    
    if action == "TERMINATE":
        raise ConstitutionalViolation("Task generation violated宪法规则")
    elif action == "QUICK_FIX":
        # Apply quick fix
        tasks_yaml = self._apply_qui  k_fix(tasks_yaml, violations)
    
    return {"TASKS": tasks_yaml}
```

---

## 8. 审计日志格式

### 8.1 违规日志条目

```json
{
  "log_id": "RULE-20260224-001",
  "timestamp": "2026-02-24T10:30:00Z",
  "rule_id": "JCODE-001",
  "handler": "QUICK_FIX",
  "priority": "P1",
  "phase": "IMPLEMENTATION",
  "context": {
    "file": "src/parser.py",
    "line": 42,
    "agent": "Implementer"
  },
  "violation": {
    "message": "Function name 'parse_Data' violates snake_case",
    "suggestion": "Rename to 'parse_data'"
  },
  "quick_fix": {
    "applied": true,
    "change": "parse_Data → parse_data",
    "verified": true
  }
}
```

### 8.2 Soft Hooks 日志

```json
{
  "log_id": "SOFT_HOOK-20260224-001",
  "timestamp": "2026-02-24T10:45:00Z",
  "rule_id": "PRACTICE-001",
  "action": "IGNORED",
  "ignore_count": 1,
  "metadata": {
    "agent": "Implementer",
    "phase": "IMPLEMENTATION",
    "upgrade_threshold": 3
  }
}
```

---

## 9. 与其他协议的关系

| 协议 | 关系 |
|------|------|
| `AGENT_CONSTITUTION.md` | Rule Engine 实现宪法规则的强制执行 |
| `QUICK_FIX_CHANNEL.md` | P1规则触发 QUICK_FIX 流程 |
| `HUMAN_INTERFACE.md` | P0规则强制人类介入 |
| `OUTPUT_FORMAT_GUIDELINES.md` | 违规日志使用统一JSON格式 |

---

## 10. Rule Engine 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                    OpenCode Superpowers                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Context Lock │  │  Rule Engine │  │  Audit Log   │  │
│  │   (MCP)      │  │   (MCP)      │  │   (MCP)      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│            │             │             │                │
│            └─────────────┼─────────────┘                │
│                          │                              │
│                   ┌──────▼───────┐                      │
│                   │   JCodemix   │                      │
│                   │   Agent      │                      │
│                   │   System     │                      │
│                   └──────────────┘                      │
│                                                         │
└─────────────────────────────────────────────────────────┘

JCode通过Rule Engine MCP Tool:
1. 注册预定义规则集（宪法规则、快速修正规则）
2. 在特定阶段触发规则检查
3. 根据违规处理策略执行 TERMINATE/QUICK_FIX/LOG_ONLY
4. 接收审计日志用于统计分析
```

---

## 封印语

> 规则是系统的骨架，  
> Rule Engine是规则的肌肉。  
>   
> 没有规则，系统混乱；  
> 没有Rule Engine，规则僵死。  
>   
> 规则必须运行，  
> 因为代码即法律。

---

**STATUS**: DRAFT (v0.1)  
**NEXT**: Review by CONDUCTOR + Human Admin  
**APPROVED**: pending
