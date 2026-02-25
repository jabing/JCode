# QUICK_FIX_CHANNEL — 快速修正通道协议

> Status: **ACTIVE**  
> Scope: Local correction mechanisms for minor issues  
> Purpose: Reduce iteration overhead for small, well-scoped fixes

---

## 0. 协议定位

本协议定义 **快速修正通道**，允许在特定条件下进行局部修正，而非触发全流程迭代。

核心原则：
> **小问题用小通道，大问题走大流程。**

目标：
- 减少"因小失大"的迭代开销
- 保持系统安全性的同时提高效率
- 明确快速修正的边界条件

---

## 1. 快速修正 vs 完整迭代

### 1.1 适用条件对比

| 特征 | 快速修正通道 | 完整迭代 |
|---|---|---|
| **问题范围** | 单一、隔离、无副作用 | 多处、关联、有依赖 |
| **影响层级** | 仅影响当前阶段 | 影响多个阶段 |
| **TASKS变化** | 无需修改TASKS | 需要重新规划TASKS |
| **审查要求** | 单点验证 | 全流程验证 |
| **iteration** | 不增加 | +1 |

### 1.2 快速修正的边界

**允许快速修正的情况**：
- ✅ 拼写错误/格式问题
- ✅ 单一变量的值修正
- ✅ 明确遗漏的null检查（TASKS已暗示）
- ✅ 注释/文档的补充
- ✅ 测试用例的输入数据修正

**禁止快速修正的情况**：
- ❌ 需要新增逻辑分支
- ❌ 需要修改接口签名
- ❌ 需要新增依赖
- ❌ 影响多个模块的修改
- ❌ TASKS中未提及的功能

---

## 2. 快速修正流程

### 2.1 触发条件

快速修正通道可在以下阶段触发：

| 阶段 | 触发方式 | 适用修正类型 |
|---|---|---|
| REVIEW REJECTED | Reviewer标记为`MINOR_FIX` | 实现层小问题 |
| TEST FAILED | Tester标记为`QUICK_FIXABLE` | 测试数据/环境问题 |
| POST-DELIVERY | 人类请求`HOTFIX` | 紧急小修复 |

### 2.2 流程图

```
[REVIEW] → REJECTED: MINOR_FIX
        ↓
[QUICK_FIX_REQUEST]
  - 问题类型: {type}
  - 影响范围: {scope}
  - 修正建议: {suggestion}
        ↓
[ELIGIBILITY_CHECK]
  - 符合边界条件? → YES → [QUICK_FIX_EXECUTE]
  - 符合边界条件? → NO  → [NORMAL_ITERATION]
        ↓
[QUICK_FIX_EXECUTE]
  - Implementer执行修正
  - 记录修正内容
        ↓
[QUICK_VERIFY]
  - 验证修正是否解决问题
  - 确认无副作用
        ↓
[QUICK_FIX_COMPLETE]
  - iteration不变
  - 记录快速修正日志
        ↓
[REVIEW] (仅验证修正点)
```

---

## 3. 修正类型定义

### 3.1 TYPE-A: 笔误修正 (TYPO_FIX)

**定义**：拼写错误、命名不一致、格式问题

**示例**：
- 变量名拼写错误：`usreName` → `userName`
- 注释格式不规范
- 字符串内容错误

**验证方式**：diff检查

**最大修正量**：5处/次

---

### 3.2 TYPE-B: 单点防御 (SINGLE_GUARD)

**定义**：添加单一防御性检查，无需修改逻辑结构

**示例**：
```python
# 修正前
def process(data):
    return data.strip()

# 修正后（添加null检查）
def process(data):
    if data is None:
        return None
    return data.strip()
```

**验证方式**：单元测试

**最大修正量**：1处/次

---

### 3.3 TYPE-C: 测试适配 (TEST_ADAPT)

**定义**：修正测试用例的输入/预期，不修改被测代码

**示例**：
- 测试数据格式错误
- 预期值与实际业务规则不符
- 测试环境配置问题

**验证方式**：测试执行

**最大修正量**：3个测试用例/次

---

### 3.4 TYPE-D: 文档补充 (DOC_ENHANCE)

**定义**：补充注释、更新README、添加类型注解

**示例**：
- 添加函数文档字符串
- 补充参数说明
- 更新变更日志

**验证方式**：人工检查

**最大修正量**：10行/次

---

## 4. 快速修正请求格式

### 4.1 REVIEW阶段的快速修正请求

```
[REVIEW]
REJECTED: MINOR_FIX

Quick Fix Request:
  Type: {TYPE-A/B/C/D}
  Location: {file}:{line}
  Issue: {问题描述}
  Fix: {修正内容}
  Scope: {影响范围评估}
  
Verification: {验证方式}
```

**示例**：
```
[REVIEW]
REJECTED: MINOR_FIX

Quick Fix Request:
  Type: TYPE-A
  Location: src/utils.py:42
  Issue: 变量名拼写错误 "usreName"
  Fix: 改为 "userName"
  Scope: 仅影响变量名，无逻辑变化
  
Verification: diff检查，确认仅变量名变化
```

### 4.2 TEST阶段的快速修正请求

```
[TEST]
TEST FAILED: QUICK_FIXABLE

Quick Fix Request:
  Type: TYPE-C
  Test Case: {test_name}
  Issue: {问题描述}
  Fix: {修正内容}
  Impact: {仅影响测试，不影响被测代码}
```

---

## 5. 快速修正执行协议

### 5.1 Implementer执行规则

当收到`QUICK_FIX_REQUEST`时，Implementer必须：

1. **验证适用性**：确认修正类型符合边界条件
2. **限制范围**：仅修正指定位置，不做额外修改
3. **记录变更**：在`[IMPLEMENTATION]`后附加`[QUICK_FIX_LOG]`

```
[IMPLEMENTATION]
{修正后的代码}

[QUICK_FIX_LOG]
Type: TYPE-A
Change: 变量名 usreName → userName (line 42)
Reason: REVIEW REJECTED: MINOR_FIX
Impact: 无逻辑变化
```

### 5.2 验证规则

快速修正后的验证必须：

1. **聚焦验证**：仅验证修正点，不需全面回归
2. **副作用检查**：确认无意外影响
3. **日志记录**：记录快速修正的完整信息

---

## 6. 快速修正的限制

### 6.1 频率限制

| 时间窗口 | 最大次数 | 超出后处理 |
|---|---|---|
| 单次任务 | 3次 | 强制进入完整迭代 |
| 单个阶段 | 2次 | 强制进入完整迭代 |
| 连续任务 | 5次 | 触发任务质量审查 |

### 6.2 累积限制

**快速修正累积效应规则**：
- 若同一文件的快速修正累计 > 3次 → 需要完整迭代重新审视
- 若同一模块的快速修正累计 > 5次 → 触发重构建议

---

## 7. 与其他协议的关系

| 协议 | 关系 |
|---|---|
| `AGENT_CONSTITUTION` | 快速修正不得违反宪法边界 |
| `EDGE_CASES` | 边界场景不适用快速修正 |
| `HUMAN_INTERFACE` | 紧急HOTFIX可通过快速通道 |
| `OUTPUT_FORMAT_GUIDELINES` | 快速修正日志使用增强格式 |

---

## 8. 审计与追溯

### 8.1 快速修正日志存储

位置：`audit/quick_fixes.jsonl`

格式：
```json
{
  "fix_id": "QF-{timestamp}-{seq}",
  "type": "TYPE-A",
  "trigger": "REVIEW_REJECTED",
  "location": "src/utils.py:42",
  "change": "变量名拼写修正",
  "iteration_before": 2,
  "iteration_after": 2,
  "timestamp": "2026-02-24T10:30:00Z"
}
```

### 8.2 统计指标

系统应跟踪：
- 快速修正成功率
- 快速修正平均耗时
- 快速修正转完整迭代率
- 按类型的修正频率分布

---

## 封印语

> 快速修正是效率工具，不是偷懒通道。
>
> 用得对，事半功倍；
> 用得错，债台高筑。
>
> 宁可多一次迭代，不可多一处隐患。

---

**END OF QUICK_FIX_CHANNEL**
