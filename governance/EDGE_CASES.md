# EDGE_CASES — 边界场景处理协议

> Status: **ACTIVE**  
> Scope: System boundary conditions and state transitions  
> Purpose: Define complete state machines for edge cases

---

## 0. 协议定位

本协议定义 **所有边界场景的完整状态机与处理路径**。

核心原则：
> **任何边界场景都必须有明确的终止状态或恢复路径。**

禁止：
- 悬空状态（系统不知道下一步做什么）
- 无限循环（状态之间互相触发）
- 未定义恢复路径的STOP

---

## 1. 边界场景总览

| 场景标识 | 触发条件 | 严重程度 | 恢复路径 |
|---|---|---|---|
| `E001` | Architect-Only模式 | 中 | 人类确认 / 补充测试 |
| `E002` | FAST-CODER溢出 | 高 | 降级为普通模式 |
| `E003` | iteration > MAX | 高 | 人类介入 |
| `E004` | NON-VERIFIABLE任务 | 高 | 人类介入 |
| `E005` | STRUCTURAL VIOLATION | 严重 | 调查 / 终止 |
| `E006` | EVIDENCE_UNAVAILABLE | 中 | 人类确认 / 补充环境 |

---

## 2. 场景状态机定义

### E001: Architect-Only 模式

**触发条件**：任务类型为架构设计，无可执行产物

**状态转换图**：
```
[ANALYSIS] (识别为架构任务)
      ↓
[GENERATE_ARCHITECTURE]
      ↓
[TEST] → Tester声明 "EVIDENCE_UNAVAILABLE: Architect-Only"
      ↓
[E001_PENDING] ← 系统暂停
      ↓
+-----+-------------------------------------------+
|     |                                           |
| A   | B                                         | C
↓     ↓                                           ↓
[ACCEPT_WITHOUT_EVIDENCE]  [SUPPLY_TEST_ENV]  [DOWNGRADE_TO_REVIEW]
(需HUMAN_ADMIN)            (补充环境后重测)    (转为人工评审)
      ↓                     ↓                    ↓
[FINAL: DELIVERED]    [RETEST]              [MANUAL_REVIEW]
                                            ↓
                                      [FINAL: DELIVERED/STOPPED]
```

**状态说明**：
| 状态 | 含义 | 可转换到 |
|---|---|---|
| `E001_PENDING` | 等待人类决策 | ACCEPT / SUPPLY / DOWNGRADE |
| `ACCEPT_WITHOUT_EVIDENCE` | 无证据接受（管理员确认） | FINAL |
| `SUPPLY_TEST_ENV` | 补充测试环境 | RETEST |
| `DOWNGRADE_TO_REVIEW` | 降级为人工评审 | MANUAL_REVIEW |

**审计要求**：必须记录`[HUMAN_INTERVENTION]`

---

### E002: FAST-CODER 溢出

**触发条件**：FAST-CODER模式下TASKS不充分，无法继续

**状态转换图**：
```
[FAST_CODER_MODE]
      ↓
[IMPLEMENTATION] → 发现TASKS不充分
      ↓
[E002_OVERFLOW] ← 系统暂停
      ↓
+------------------+------------------+
|                  |                  |
A                  B                  C
↓                  ↓                  ↓
[DOWNGRADE_TO_NORMAL]  [STOP_AND_REPLAN]  [HUMAN_CLARIFY]
(降级为普通模式)      (停止并重新规划)    (人工澄清TASKS)
      ↓                  ↓                    ↓
[ANALYSIS]          [FINAL: STOPPED]     [TASKS更新]
(重新开始流程)                           ↓
                                    [IMPLEMENTATION]
```

**状态说明**：
| 状态 | 含义 | 可转换到 |
|---|---|---|
| `E002_OVERFLOW` | FAST-CODER无法继续 | DOWNGRADE / STOP / CLARIFY |
| `DOWNGRADE_TO_NORMAL` | 退出FAST-CODER模式 | ANALYSIS |
| `STOP_AND_REPLAN` | 终止当前任务 | FINAL |
| `HUMAN_CLARIFY` | 等待人类补充TASKS | TASKS更新后继续 |

**关键规则**：
- FAST-CODER不可自行推断TASKS
- 溢出后必须显式选择恢复路径
- 降级为普通模式后，iteration重置为0

---

### E003: 迭代溢出 (iteration > MAX)

**触发条件**：`iteration_counter > MAX_ITERATIONS`

**状态转换图**：
```
[iteration = MAX]
      ↓
[REVIEW/TEST] → REJECTED 或 FAILED
      ↓
[CONDUCTOR] → 检测到溢出
      ↓
[E003_OVERFLOW] ← 触发STOP，等待人类
      ↓
+------------------+------------------+
|                  |                  |
A                  B                  C
↓                  ↓                  ↓
[CONFIRM_STOP]  [EXTEND_ITERATIONS]  [ROLLBACK_RETRY]
(确认终止)      (延长迭代上限)       (回滚到指定迭代)
      ↓              ↓                    ↓
[FINAL: STOPPED]  [iteration += N]   [iteration = N]
                  ↓                  ↓
             [ANALYSIS]          [ANALYSIS]
             (从指定点重试)
```

**状态说明**：
| 状态 | 含义 | 可转换到 |
|---|---|---|
| `E003_OVERFLOW` | 迭代溢出，已触发STOP | CONFIRM / EXTEND / ROLLBACK |
| `CONFIRM_STOP` | 确认终止 | FINAL |
| `EXTEND_ITERATIONS` | 延长上限（需管理员） | 继续迭代 |
| `ROLLBACK_RETRY` | 回滚重试 | 从指定迭代重新开始 |

**审计要求**：
- 必须记录每次迭代失败的原因
- 延长迭代需要管理员确认码
- 回滚重试需要记录回滚点

---

### E004: NON-VERIFIABLE 任务

**触发条件**：Analyst判定任务为NON-VERIFIABLE

**状态转换图**：
```
[ANALYSIS] → Verifiability = NON-VERIFIABLE
      ↓
[E004_BLOCKED] ← 系统暂停
      ↓
+------------------+------------------+
|                  |                  |
A                  B                  C
↓                  ↓                  ↓
[REDEFINE_TASK]  [ABANDON_TASK]  [DOWNGRADE_VERIFIABILITY]
(重新定义任务)    (放弃任务)        (降级为SOFT，需管理员)
      ↓              ↓                    ↓
[ANALYSIS]       [FINAL: STOPPED]   [Verifiability = SOFT]
(重新分析)                          ↓
                               [TASKS]
```

**降级规则**：
- NON-VERIFIABLE → SOFT-VERIFIABLE 需要：
  1. HUMAN_ADMIN权限
  2. 明确的验收checklist
  3. 审计记录

---

### E005: STRUCTURAL VIOLATION

**触发条件**：检测到角色越权、流程跳过、输入非法等宪法违规

**状态转换图**：
```
[任意阶段] → 检测到VIOLATION
      ↓
[E005_CRITICAL] ← 立即暂停
      ↓
+------------------+
|                  |
A                  B
↓                  ↓
[INVESTIGATE]  [EMERGENCY_STOP]
(调查原因)      (紧急终止)
      ↓              ↓
[REPORT]       [FINAL: STOPPED]
(生成报告)
      ↓
[HUMAN_DECISION]
(人类决定是否恢复)
      ↓
[RESUME / ABORT]
```

**状态说明**：
| 状态 | 含义 | 可转换到 |
|---|---|---|
| `E005_CRITICAL` | 严重违规，系统冻结 | INVESTIGATE / EMERGENCY_STOP |
| `INVESTIGATE` | 调查违规原因 | REPORT |
| `EMERGENCY_STOP` | 无需调查，直接终止 | FINAL |
| `HUMAN_DECISION` | 等待人类决策 | RESUME / ABORT |

**关键规则**：
- E005不可自动恢复，必须人类介入
- 即使是HUMAN_ADMIN也不可跳过调查
- 调查报告必须包含：违规点、触发规则、影响范围

---

### E006: EVIDENCE_UNAVAILABLE

**触发条件**：Tester无法获取证据（非Architect-Only场景）

**状态转换图**：
```
[TEST] → 无法获取证据
      ↓
[E006_PENDING] ← 系统暂停
      ↓
+------------------+------------------+
|                  |                  |
A                  B                  C
↓                  ↓                  ↓
[SUPPLY_ENV]    [ACCEPT_RISK]      [CHANGE_VERIFY_METHOD]
(补充测试环境)  (接受风险，需管理员)  (更换验证方法)
      ↓              ↓                    ↓
[RETEST]        [REVIEW_OVERRIDE]   [TASKS更新]
      ↓              ↓                    ↓
[TEST_PASSED]   [FINAL: DELIVERED]   [TEST]
  或
[TEST_FAILED]
```

---

## 3. 状态机通用规则

### 3.1 状态命名规范

- `{场景ID}_PENDING`：等待决策的暂停状态
- `{场景ID}_OVERFLOW`：资源/能力溢出状态
- `{场景ID}_CRITICAL`：严重错误，需要人工介入
- `{场景ID}_BLOCKED`：前置条件未满足，无法继续

### 3.2 状态转换约束

1. **所有PENDING状态必须有时限**（默认24小时，可配置）
2. **超时未处理 → 自动升级为CRITICAL**
3. **任何状态都应有到FINAL的路径**（直接或间接）

### 3.3 审计日志格式

```
{
  "event_id": "{场景ID}-{时间戳}",
  "state_from": "PREV_STATE",
  "state_to": "NEXT_STATE",
  "trigger": "触发条件",
  "actor": "SYSTEM | HUMAN_{ROLE}",
  "timestamp": "ISO8601",
  "context": { ... }
}
```

---

## 4. 与其他协议的关系

| 协议 | 关系 |
|---|---|
| `AGENT_CONSTITUTION` | 边界场景不得违反宪法 |
| `CONDUCTOR` | CONDUCTOR负责触发E003 |
| `HUMAN_INTERFACE` | 所有人类介入点通过此协议定义 |

---

## 封印语

> 边界不是系统的例外，
> 边界是系统完整性的一部分。
>
> 没有边界处理的系统，
> 只能在理想世界中运行。

---

**END OF EDGE_CASES**
