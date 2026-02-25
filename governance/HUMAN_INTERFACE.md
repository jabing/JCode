# HUMAN_INTERFACE — 人机协作接口协议

> Status: **ACTIVE**  
> Scope: Human intervention points, permissions, and audit requirements  
> Purpose: Define when and how humans can interact with the agent system

---

## 0. 协议定位

本协议定义 **人类在Agent系统中的介入权限、时机与方式**。

核心原则：
> **人类是最终裁决者，但介入必须有据可查。**

任何人类干预必须：
1. 记录介入原因
2. 明确权限范围
3. 留存审计日志

---

## 1. 人类角色定义

| 角色标识 | 权限范围 | 校验方式 |
|---|---|---|
| `HUMAN_ADMIN` | 完全权限，可覆盖任何Agent决策 | 管理员确认码 + 身份验证 |
| `HUMAN_REVIEWER` | 可修正ANALYSIS和TASKS，不可修改实现 | 角色声明 + 审计记录 |
| `HUMAN_OBSERVER` | 只读权限，可添加注释 | 身份声明 |

---

## 2. 介入时机与触发条件

### 2.1 强制介入点（系统暂停，等待人类）

| 触发条件 | 来源 | 人类操作选项 |
|---|---|---|
| `NON-VERIFIABLE` 任务 | Analyst判定 | 重新定义 / 放弃任务 / 强制降级为SOFT-VERIFIABLE |
| `iteration > MAX_ITERATIONS` | CONDUCTOR触发 | 延长迭代 / 终止任务 / 回滚到指定迭代 |
| `STRUCTURAL VIOLATION` | 宪法违规 | 调查原因 / 跳过（需管理员） / 终止 |
| `EVIDENCE_UNAVAILABLE` | Tester无法取证（如Architect-Only模式） | 接受无证据交付 / 补充测试环境 / 终止 |

### 2.2 可选介入点（人类可主动介入）

| 时机 | 介入方式 | 审计要求 |
|---|---|---|
| ANALYSIS完成后 | 添加约束、澄清需求 | 必须记录修改内容 |
| TASKS定义后 | 调整任务边界、增删任务 | 必须说明原因 |
| REVIEW REJECTED后 | 强制APPROVE（仅管理员） | 必须记录豁免理由 |
| 任意时刻 | 添加`[HUMAN_NOTE]`注释 | 自动记录时间戳和身份 |

---

## 3. 人类操作协议

### 3.1 介入操作格式

人类介入必须使用以下格式：

```
[HUMAN_INTERVENTION]
Timestamp: {ISO8601时间}
Operator: {角色标识}
Action: {操作类型}
Reason: {介入原因}
Content: {具体修改或指令}
```

**示例**：
```
[HUMAN_INTERVENTION]
Timestamp: 2026-02-24T10:30:00Z
Operator: HUMAN_ADMIN
Action: DOWNGRADE_VERIFIABILITY
Reason: 业务紧急，无法获得完整测试环境
Content: 将任务"性能优化"从HARD-VERIFIABLE降级为SOFT-VERIFIABLE，验收标准改为人工检查
```

### 3.2 权限校验

#### 管理员确认码机制

涉及`HUMAN_ADMIN`权限的操作必须提供确认码：

```
[HUMAN_INTERVENTION]
...
AdminCode: {config.ini中的confirm_code}
...
```

系统必须：
1. 校验确认码与配置一致
2. 记录操作者身份（如IP、时间）
3. 生成不可篡改的审计记录

---

## 4. 审计日志要求

### 4.1 必须记录的字段

| 字段 | 说明 | 示例 |
|---|---|---|
| `timestamp` | 介入时间 | 2026-02-24T10:30:00Z |
| `operator_role` | 操作者角色 | HUMAN_ADMIN |
| `trigger_condition` | 触发条件 | NON-VERIFIABLE |
| `action_taken` | 执行的操作 | DOWNGRADE_VERIFIABILITY |
| `affected_section` | 影响的流程段 | ANALYSIS |
| `reason` | 介入原因 | 业务紧急 |
| `outcome` | 结果 | 任务继续执行 |

### 4.2 审计日志存储

- 格式：JSON Lines（每行一条记录）
- 位置：`audit/human_interventions.jsonl`
- 不可变性：追加写入，禁止修改或删除
- 保留策略：永久保留

---

## 5. 典型场景处理流程

### 5.1 NON-VERIFIABLE任务处理

```
Analyst输出 NON-VERIFIABLE
        ↓
系统暂停，等待人类介入
        ↓
人类选择：
  A) 重新定义任务（修改ANALYSIS）
  B) 放弃任务（CONDUCTOR输出STOP）
  C) 强制降级为SOFT-VERIFIABLE（需HUMAN_ADMIN）
        ↓
记录[HUMAN_INTERVENTION]
        ↓
流程继续或终止
```

### 5.2 迭代溢出处理

```
iteration > MAX_ITERATIONS
        ↓
CONDUCTOR触发STOP
        ↓
系统暂停，等待人类介入
        ↓
人类选择：
  A) 终止任务（确认STOP）
  B) 延长迭代（指定新的MAX，需HUMAN_ADMIN）
  C) 回滚重试（指定回滚到第N次迭代）
        ↓
记录[HUMAN_INTERVENTION]
        ↓
执行人类决策
```

### 5.3 Architect-Only模式证据缺失

```
Tester声明"无法提供证据"（Architect-Only模式）
        ↓
系统标记 EVIDENCE_UNAVAILABLE
        ↓
通知人类（可选：自动或手动）
        ↓
人类选择：
  A) 接受无证据交付（架构设计文档，需HUMAN_ADMIN）
  B) 补充测试环境后重新TEST
  C) 降级为设计评审（转为人工REVIEW）
        ↓
记录[HUMAN_INTERVENTION]
        ↓
流程继续
```

---

## 6. 人机协作的原则边界

### 6.1 人类可以做的

- 修改ANALYSIS和TASKS（添加约束、澄清歧义）
- 覆盖REVIEW结果（需管理员权限）
- 延长或终止迭代
- 添加上下文注释（[HUMAN_NOTE]）
- 调整验证标准（需说明理由）

### 6.2 人类不可以做的

- 跳过REVIEW或TEST阶段（即使管理员也不可）
- 修改IMPLEMENTATION内容（应通过重新迭代）
- 删除或修改审计日志
- 在未说明原因的情况下覆盖系统决策

> **系统安全来自透明，而非信任。**

---

## 7. 与CONDUCTOR的关系

- CONDUCTOR是**自动化裁决层**
- 人类是**最终裁决层**
- 人类可覆盖CONDUCTOR的STOP决策，但必须记录原因
- 人类不可绕过CONDUCTOR直接修改流程状态

---

## 封印语

> 人机协作的本质是：
> **让机器做机器擅长的事，让人类做只有人类能承担的责任。**
>
> 介入不是特权，而是需要被记录的决策。

---

**END OF HUMAN_INTERFACE**
