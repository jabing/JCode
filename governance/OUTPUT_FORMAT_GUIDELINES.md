# OUTPUT_FORMAT_GUIDELINES — 输出格式指南

> Status: **RECOMMENDED**  
> Scope: All Agent output formats  
> Purpose: Provide optional enhancements for human readability while maintaining machine parsability

---

## 0. 协议定位

本文档定义 **可选的输出格式增强**，用于改善人类可读性，同时保持机器可解析性。

核心原则：
> **格式是容器，内容才是核心。可选增强不应破坏强制性约束。**

---

## 1. 基础格式 vs 增强格式

### 1.1 基础格式（强制）

每个Agent必须且只能输出其指定的section：

| Agent | 必须输出 | 格式 |
|---|---|---|
| Analyst | `[ANALYSIS]` | 结构化章节 |
| Planner | `[TASKS]` | TODO/Done when/Verify by 列表 |
| Implementer | `[IMPLEMENTATION]` | 代码/配置产物 |
| Reviewer | `[REVIEW]` | APPROVED/REJECTED |
| Tester | `[TEST]` | PASSED/FAILED |
| CONDUCTOR | `[FINAL]` | DELIVERED/STOPPED |

### 1.2 增强格式（可选）

在人类审核场景中，可以添加以下**可选段落**：

| 可选段落 | 用途 | 示例 |
|---|---|---|
| `[CONTEXT]` | 决策背景/上下文 | 为何选择这个实现路径 |
| `[SUMMARY]` | 一句话总结 | 变更摘要（≤50字符） |
| `[HUMAN_NOTE]` | 人类可读注释 | 需要人工注意的事项 |

---

## 2. 增强格式使用规则

### 2.1 位置规则

可选段落**必须**放在强制段落之后：

```
[IMPLEMENTATION]
<强制内容>

[CONTEXT]（可选）
<上下文说明>
```

### 2.2 长度限制

| 段落 | 最大长度 | 原因 |
|---|---|---|
| `[CONTEXT]` | 200字符 | 简洁说明，不是文档 |
| `[SUMMARY]` | 50字符 | 一句话摘要 |
| `[HUMAN_NOTE]` | 100字符 | 重点标注 |

### 2.3 内容约束

**禁止**：
- 解释性长文本
- 辩解或情绪化表达
- 替代IMPLEMENTATION内容的描述

**允许**：
- "选择X因为约束Y"（事实陈述）
- "变更：修复null检查"（变更摘要）
- "注意：此API有速率限制"（重要警告）

---

## 3. 各Agent的增强建议

### 3.1 Implementer

```
[IMPLEMENTATION]
def process_data(data):
    if data is None:
        return None
    return data.strip()

[CONTEXT]（可选）
仅添加null检查，未修改其他逻辑。原始行为保持不变。

[SUMMARY]（可选）
添加null检查防御
```

### 3.2 Reviewer

```
[REVIEW]
APPROVED

[CONTEXT]（可选）
实现严格匹配TASKS定义。未发现越权行为。
```

### 3.3 Tester

```
[TEST]
TEST PASSED

[HUMAN_NOTE]（可选）
注意：测试仅覆盖正常路径，边界情况在TASKS中未定义。
```

---

## 4. 机器解析优先级

当增强格式与机器解析冲突时：

1. **强制段落优先**：解析器必须先提取强制段落
2. **可选段落忽略**：解析器可以忽略可选段落
3. **向后兼容**：增强格式不得破坏现有解析逻辑

---

## 5. 使用场景建议

| 场景 | 推荐增强 | 原因 |
|---|---|---|
| 自动化CI/CD | 无 | 机器解析优先 |
| 人类代码审查 | `[CONTEXT]` + `[SUMMARY]` | 理解上下文 |
| 敏感操作 | `[HUMAN_NOTE]` | 提醒人工确认 |
| 跨团队协作 | `[SUMMARY]` | 快速沟通 |
| 快速修正 | `[QUICK_FIX_LOG]` | 追踪小修改 |
| 学习/培训 | `[CONTEXT]` | 帮助理解决策 |

---

## 6. 场景化模板库

### 6.1 场景：首次功能实现

**Analyst输出**：
```
[ANALYSIS]
### 🎯 Problem Understanding
- 实现用户登录功能，支持用户名/密码认证

### ⚠️ Constraints & Environment
- 后端: Python 3.10+
- 数据库: PostgreSQL

### 💣 Risks & Failure Paths
- 密码明文存储风险
- 暴力破解风险

### 📊 Non-Functional Requirements
- Performance: 登录响应 < 500ms
- Security: 密码必须加密存储
- Maintainability: 遵循PEP8

### ❓ Unknowns & Ambiguities
- 是否需要记住我功能？

### 🔎 Verifiability Classification
- HARD-VERIFIABLE
```

**Planner输出**：
```
[TASKS]
- TODO: 实现密码哈希函数
  Done when: 密码可加密存储和验证
  Verify by: 单元测试通过

- TODO: 实现登录API端点
  Done when: POST /login 返回正确响应
  Verify by: API测试通过

- TODO: 添加登录失败计数
  Done when: 失败5次后锁定15分钟
  Verify by: 边界测试通过
```

**Implementer输出**：
```
[IMPLEMENTATION]
import bcrypt
from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    # 验证逻辑...
    return {'status': 'success'}

[CONTEXT]
使用bcrypt进行密码哈希，选择原因是其内置salt和自适应成本因子。

[SUMMARY]
实现用户登录API + bcrypt密码加密
```

---

### 6.2 场景：快速修正

**Reviewer输出**：
```
[REVIEW]
REJECTED: MINOR_FIX

Quick Fix Request:
  Type: TYPE-A
  Location: auth/login.py:15
  Issue: 变量名 "passwrod" 拼写错误
  Fix: 改为 "password"
  Scope: 仅影响变量名
  
Verification: diff检查
```

**Implementer输出（快速修正后）**：
```
[IMPLEMENTATION]
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')  # 修正拼写
    # ...

[QUICK_FIX_LOG]
Type: TYPE-A
Change: 变量名 passwrod → password (line 15)
Reason: REVIEW REJECTED: MINOR_FIX
Impact: 无逻辑变化

[SUMMARY]
修正变量名拼写错误
```

---

### 6.3 场景：测试失败

**Tester输出**：
```
[TEST]
TEST FAILED:
- Input: {"username": "test", "password": ""}
- Expected: 返回400错误
- Actual: 返回500错误
- Location: auth/login.py:20

[HUMAN_NOTE]
空密码未做前置校验，直接进入数据库查询导致异常。
建议在API入口添加参数验证。
```

---

### 6.4 场景：边界情况处理

**Tester输出（Architect-Only模式）**：
```
[TEST]
EVIDENCE_UNAVAILABLE: Architect-Only

Reason: 任务为架构设计文档，无可执行代码产物

Suggested Action:
- 转为人工评审
- 或补充示例代码后重新测试
```

---

### 6.5 场景：迭代溢出

**CONDUCTOR输出**：
```
[FINAL]
STOP

Reason: iteration (5) > MAX_ITERATIONS (5)

Trigger: CONDUCTOR.md 第133行规则

Action Required:
- 人类介入选择：终止 / 延长迭代 / 回滚重试
- 参考: governance/HUMAN_INTERFACE.md 第5.2节

[HUMAN_NOTE]
连续5次迭代失败，建议检查TASKS定义是否合理。
```

---

### 6.6 场景：人类介入

**人类操作**：
```
[HUMAN_INTERVENTION]
Timestamp: 2026-02-24T10:30:00Z
Operator: HUMAN_ADMIN
Action: EXTEND_ITERATIONS
Reason: 任务复杂度评估不足，原MAX=5过少
Content: 将MAX_ITERATIONS从5延长到8
AdminCode: ********
```

---

## 7. 格式验证工具

### 7.1 必须验证项

| 检查项 | 规则 | 错误级别 |
|---|---|---|
| Section存在性 | 必须包含指定的[SECTION] | ERROR |
| Section唯一性 | 每个[SECTION]只能出现一次 | ERROR |
| Section顺序 | 可选段落在强制段落之后 | WARNING |
| 长度限制 | CONTEXT≤200, SUMMARY≤50, HUMAN_NOTE≤100 | WARNING |

### 7.2 验证脚本示例

```python
import re
from typing import Dict, List, Tuple

def validate_agent_output(output: str, agent: str) -> Tuple[bool, List[str]]:
    """验证Agent输出格式"""
    errors = []
    
    # 定义必须的section
    required_sections = {
        'Analyst': ['ANALYSIS'],
        'Planner': ['TASKS'],
        'Implementer': ['IMPLEMENTATION'],
        'Reviewer': ['REVIEW'],
        'Tester': ['TEST'],
        'CONDUCTOR': ['FINAL']
    }
    
    # 定义可选section及其长度限制
    optional_sections = {
        'CONTEXT': 200,
        'SUMMARY': 50,
        'HUMAN_NOTE': 100,
        'QUICK_FIX_LOG': None
    }
    
    # 提取所有section
    sections = re.findall(r'\[(\w+)\]', output)
    
    # 检查必须section
    for req in required_sections.get(agent, []):
        if req not in sections:
            errors.append(f"ERROR: Missing required section [{req}]")
    
    # 检查section顺序（可选段落必须在强制段落之后）
    required_idx = min(
        sections.index(s) for s in required_sections.get(agent, []) 
        if s in sections
    )
    for opt in optional_sections:
        if opt in sections:
            if sections.index(opt) < required_idx:
                errors.append(f"WARNING: [{opt}] should come after required section")
    
    # 检查长度限制
    for section, limit in optional_sections.items():
        if limit and f'[{section}]' in output:
            # 提取section内容
            pattern = rf'\[{section}\](.*?)(?=\[|$)'
            match = re.search(pattern, output, re.DOTALL)
            if match and len(match.group(1).strip()) > limit:
                errors.append(f"WARNING: [{section}] exceeds {limit} characters")
    
    return len([e for e in errors if e.startswith('ERROR')]) == 0, errors
```

---

## 封印语

> 格式的目的是传递信息，而非展示技巧。
>
> 增强是为了理解，不是为了装饰。

---

**END OF OUTPUT_FORMAT_GUIDELINES**
