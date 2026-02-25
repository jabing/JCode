# SUPERPOWERS_EXTENSION — MCP Tool Registration & JCode Agent Tools

> Status: **DESIGN DRAFT**  
> Scope: MCP Superpowers extension specification  
> Purpose: Define JCode 6-Agent tools as MCP registerable tools

---

## 0. Extension Overview

JCode extends the Superpowers capabilities via **MCP (Model Context Protocol)** by exposing 6 Agent tools. These tools implement the constitutional governance layer on top of OMO's core capabilities.

**Key Design Principles**:
- ** Stateless Tools**: Each tool call is independent, state managed via `context_lock_id`
- ** Atomic Operations**: Each tool performs one phase of the governance workflow
- ** Explicit Error Signaling**: Failure conditions encoded in output schema
- ** Audit Trail**: All tool calls generate structured audit log entries

```
┌─────────────────────────────────────────────────────────────┐
│              MCP Superpowers Extension                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Superpowers Core (OMO):                              │  │
│  │  - Context Lock (statemgmt)                           │  │
│  │  - Rule Engine (policy enforcement)                   │  │
│  │  - Incremental Build (change application)             │  │
│  │  - Audit Log (tracing)                                │  │
│  │  - UI (human interaction)                             │  │
│  └───────────────────────────────────────────────────────┘  │
│                      ↕ MCP Protocol                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  JCode Agent Tools (6registerable):                   │  │
│  │  - jcode.analyze  (Analyst-司马迁)                    │  │
│  │  - jcode.plan     (Planner-商鞅)                       │  │
│  │  - jcode.implement(Implementer-鲁班)                  │  │
│  │  - jcode.review   (Reviewer-包拯)                     │  │
│  │  - jcode.test     (Tester-张衡)                       │  │
│  │  - jcode.conductor(Conductor-韩非子)                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. MCP Tool JSON Schema

All JCode Agent tools use the **MCP Tool Schema** format (per modelcontextprotocol.io):

```json
{
  "name": "jcode.<agent>",
  "description": "JCode <Agent Name> tool implementing constitutional governance phase",
  "inputSchema": {
    "type": "object",
    "properties": {
      "context_lock_id": {
        "type": "string",
        "description": "OMO Context Lock ID for state isolation"
      },
      "input_data": {
        "type": "object",
        "description": "Phase-specific input payload"
      },
      "mode": {
        "type": "string",
        "enum": ["full", "light", "safe", "fast", "custom"],
        "description": "Execution mode selector"
      }
    },
    "required": ["context_lock_id", "input_data", "mode"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "section": {
        "type": "string",
        "description": "Output section marker (e.g., [ANALYSIS])"
      },
      "payload": {
        "type": "object",
        "description": "Phase-specific output payload"
      },
      "error": {
        "type": "object",
        "description": "Error info if tool fails",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["NON-VERIFIABLE", "RULE_VIOLATION", "EVIDENCE_UNAVAILABLE", "ITERATION_OVERFLOW", "STRUCTURAL_VIOLATION"]
          },
          "message": { "type": "string" },
          "action": { "type": "string", "enum": ["HUMAN_INTERVENTION", "RETRY", "STOP", "CONTINUE"] }
        }
      }
    },
    "required": ["section", "payload"]
  }
}
```

---

## 2. JCode Agent Tools Definition

### 2.1 `jcode.analyze` - Problem Analysis

**Agent**: Analyst (司马迁)  
**Purpose**: Problem verifiability assessment, NFRs, risk identification  
**Input**:
```json
{
  "context_lock_id": "string",
  "input_data": {
    "problem_statement": "string",
    "user_requirements": "array of strings"
  },
  "mode": "string"
}
```

**Output**:
```json
{
  "section": "[ANALYSIS]",
  "payload": {
    "verifiability": "HARD | SOFT | NON-VERIFIABLE",
    "nfrs": {
      "performance": "string",
      "maintainability": "string",
      "security": "string",
      "compatibility": "string"
    },
    "risks": ["string"],
    "unknowns": ["string"]
  }
}
```

**Failure Condition**: `verifiability = "NON-VERIFIABLE"` → `error.type = "NON-VERIFIABLE"`, `error.action = "HUMAN_INTERVENTION"`

---

### 2.2 `jcode.plan` - Task Planning

**Agent**: Planner (商鞅)  
**Purpose**: Atomically verifiable task generation  
**Input**:
```json
{
  "context_lock_id": "string",
  "input_data": {
    "analysis": "[ANALYSIS] output JSON"
  },
  "mode": "string"
}
```

**Output**:
```json
{
  "section": "[TASKS]",
  "payload": {
    "tasks": [
      {
        "todo": "string (atomic task)",
        "done_when": "string (verification condition)",
        "verify_by": "string (evidence source)"
      }
    ],
    "dependencies": [["task_id", "task_id"]]
  }
}
```

**Failure Condition**: Any task `done_when` not verifiable → `error.type = "NON-VERIFIABLE"`

---

### 2.3 `jcode.implement` - Code Implementation

**Agent**: Implementer (鲁班)  
**Purpose**: Authorized code generation only  
**Input**:
```json
{
  "context_lock_id": "string",
  "input_data": {
    "tasks": "[TASKS] output JSON",
    "om_rules": ["string (rule IDs)"],
    "iteration": "integer"
  },
  "mode": "string"
}
```

**Output**:
```json
{
  "section": "[IMPLEMENTATION]",
  "payload": {
    "artifacts": {
      "files": ["string (file paths)"],
      "diff": "unified diff format string",
      "metadata": {
        "iteration": "integer",
        "changes_count": "integer"
      }
    }
  }
}
```

**Failure Condition**: Implements beyond `tasks` → `error.type = "RULE_VIOLATION"`, `error.action = "STOP"`

---

### 2.4 `jcode.review` - Compliance Review

**Agent**: Reviewer (包拯)  
**Purpose**:二元 APPROVED | REJECTED judgment  
**Input**:
```json
{
  "context_lock_id": "string",
  "input_data": {
    "tasks": "[TASKS] output JSON",
    "implementation": "[IMPLEMENTATION] output JSON",
    "quick_fix_eligible": "boolean"
  },
  "mode": "string"
}
```

**Output**:
```json
{
  "section": "[REVIEW]",
  "payload": {
    "result": "APPROVED | REJECTED",
    "issues": [
      {
        "task_ref": "string",
        "severity": "MAJOR | MINOR",
        "description": "string"
      }
    ],
    "quick_fix_trigger": "string | null (MINOR_FIX rule ID)"
  }
}
```

**Failure Condition**: Any `MAJOR` issue → `result = "REJECTED"`, `error.action = "RETRY"`

---

### 2.5 `jcode.test` - Evidence Verification

**Agent**: Tester (张衡)  
**Purpose**: Evidence-based PASSED | FAILED judgment  
**Input**:
```json
{
  "context_lock_id": "string",
  "input_data": {
    "tasks": "[TASKS] output JSON",
    "implementation": "[IMPLEMENTATION] output JSON",
    "verify_by_clauses": ["string (done_when clauses)"]
  },
  "mode": "string"
}
```

**Output**:
```json
{
  "section": "[TEST]",
  "payload": {
    "result": "PASSED | FAILED | EVIDENCE_UNAVAILABLE",
    "evidence": {
      "test_output": "string",
      "metrics": {"object"},
      "screenshots": ["string (paths)"]
    },
    "failed_clauses": ["string"]
  }
}
```

**Failure Condition**: Any `verify_by_clause` fails → `result = "FAILED"`, `error.action = "RETRY"`

---

### 2.6 `jcode.conductor` - Final Arbitration

**Agent**: Conductor (韩非子)  
**Purpose**: DELIVER | ITERATE | STOP decision  
**Input**:
```json
{
  "context_lock_id": "string",
  "input_data": {
    "review_result": "APPROVED | REJECTED",
    "test_result": "PASSED | FAILED | EVIDENCE_UNAVAILABLE",
    "iteration_count": "integer",
    "max_iterations": "integer"
  },
  "mode": "string"
}
```

**Output**:
```json
{
  "section": "[FINAL]",
  "payload": {
    "decision": "DELIVER | ITERATE | STOP",
    "reason": "string (rule triggered)",
    "next_iteration": "integer",
    "deliverables": {
      "files": ["string"],
      "audit_log": "string (path)"
    }
  }
}
```

**Failure Conditions**:
- `review_result = "REJECTED"` or `test_result ≠ "PASSED"` → `decision = "ITERATE"`
- `iteration_count >= max_iterations` → `decision = "STOP"`, `error.action = "HUMAN_INTERVENTION"`
- System violation → `decision = "STOP"`, `error.action = "STOP"`

---

## 3. Tool Registration Flow

### 3.1 OMO-side Registration

OMO loads JCode tools via MCP configuration:

```yaml
# .omo/config.yaml
mcp:
  servers:
    jcode-governance:
      command: "python"
      args: ["-m", "jcode.mcp.server"]
      env:
        OMO_SESSION_ID: "${OMO_SESSION_ID}"
        JCODE_CONFIG: "/path/to/jcode/config.yaml"
      tools:
        - name: "jcode.analyze"
          description: "JCode Analyst tool for problem analysis"
        - name: "jcode.plan"
          description: "JCode Planner tool for task planning"
        - name: "jcode.implement"
          description: "JCode Implementer tool for code generation"
        - name: "jcode.review"
          description: "JCode Reviewer tool for compliance review"
        - name: "jcode.test"
          description: "JCode Tester tool for evidence verification"
        - name: "jcode.conductor"
          description: "JCode Conductor tool for final arbitration"
```

### 3.2 JCode-side Tool Handler

JCode MCP server implements tool dispatch:

```python
# jcode/mcp/server.py
from mcp.server import Server
from jcode.agents import Analyst, Planner, Implementer, Reviewer, Tester, Conductor

class JCodeMCPServer:
    def __init__(self):
        self.server = Server("jcode-governance")
        self._register_tools()
    
    def _register_tools(self):
        @self.server.tool()
        async def jcode_analyze(context_lock_id: str, input_data: dict, mode: str) -> dict:
            analyst = Analyst(mode=mode)
            result = analyst.analyze(problem_statement=input_data["problem_statement"])
            return {"section": "[ANALYSIS]", "payload": result}
        
        @self.server.tool()
        async def jcode_plan(context_lock_id: str, input_data: dict, mode: str) -> dict:
            planner = Planner(mode=mode)
            result = planner.plan(analysis=input_data["analysis"])
            return {"section": "[TASKS]", "payload": result}
        
        # ... (implement jcode.implement, jcode.review, jcode.test, jcode.conductor)

# Start server
if __name__ == "__main__":
    server = JCodeMCPServer()
    server.run()
```

---

## 4. Extension Examples

### 4.1 Complete Workflow Example

```python
# OMO invokes JCode tools via MCP
async def run_jcode_workflow(om_session_id: str, problem: str):
    context_lock_id = await om_client.context_lock.acquire(om_session_id)
    
    # Step 1: Analyze
    analysis_result = await om_client.mcp.call_tool(
        "jcode.analyze",
        {"context_lock_id": context_lock_id, "input_data": {"problem_statement": problem}, "mode": "full"}
    )
    
    if analysis_result["payload"]["verifiability"] == "NON-VERIFIABLE":
        await om_client.human_intervention.trigger("NON-VERIFIABLE", context_lock_id)
        return
    
    # Step 2: Plan
    tasks_result = await om_client.mcp.call_tool(
        "jcode.plan",
        {"context_lock_id": context_lock_id, "input_data": {"analysis": analysis_result}, "mode": "full"}
    )
    
    # Step 3: Implement
    implementation = await om_client.mcp.call_tool(
        "jcode.implement",
        {"context_lock_id": context_lock_id, "input_data": {"tasks": tasks_result, "iteration": 1}, "mode": "full"}
    )
    
    # Step 4: Review
    review_result = await om_client.mcp.call_tool(
        "jcode.review",
        {"context_lock_id": context_lock_id, "input_data": {"tasks": tasks_result, "implementation": implementation}, "mode": "full"}
    )
    
    if review_result["payload"]["result"] != "APPROVED":
        # Iterate or trigger intervention
        return
    
    # Step 5: Test
    test_result = await om_client.mcp.call_tool(
        "jcode.test",
        {"context_lock_id": context_lock_id, "input_data": {"tasks": tasks_result, "implementation": implementation}, "mode": "full"}
    )
    
    if test_result["payload"]["result"] != "PASSED":
        # Iterate or trigger intervention
        return
    
    # Step 6: Conductor
    final_decision = await om_client.mcp.call_tool(
        "jcode.conductor",
        {"context_lock_id": context_lock_id, "input_data": {"review_result": "APPROVED", "test_result": "PASSED", "iteration_count": 1, "max_iterations": 5}, "mode": "full"}
    )
    
    if final_decision["payload"]["decision"] == "DELIVER":
        await om_client.incremental_build.apply(implementation)
        await om_client.context_lock.release(context_lock_id)
```

### 4.2 Switch Mechanism Integration

```yaml
# jcode/config.yaml
tools:
  jcode.analyze:
    enabled: true
    modes: ["full", "light", "safe", "fast"]
    default_mode: "full"
  jcode.plan:
    enabled: true
    modes: ["full", "light", "safe"]
    default_mode: "full"
  jcode.implement:
    enabled: true
    modes: ["full", "light", "safe", "fast"]
    default_mode: "full"
  jcode.review:
    enabled: true
    modes: ["full", "light", "safe"]
    default_mode: "full"
  jcode.test:
    enabled: true
    modes: ["full", "light", "fast"]
    default_mode: "full"
  jcode.conductor:
    enabled: true
    modes: ["full", "light"]
    default_mode: "full"

# Mode constraints (enforced by JCode server)
modes:
  full:
    nfr_check: true
    manual_review: true
    max_iterations: 5
  light:
    nfr_check: false
    manual_review: true
    max_iterations: 3
  fast:
    nfr_check: false
    manual_review: false
    max_iterations: 2
  safe:
    nfr_check: true
    manual_review: true
    max_iterations: 5
    forced_human_intervention: true
```

---

## 5. Integration with OpenCode Superpowers

### 5.1 Context Lock Integration

JCode tools use OMO Context Lock via `context_lock_id` parameter:

| Tool | Context Lock Usage |
|------|-------------------|
| `jcode.analyze` | Read-only project structure |
| `jcode.plan` | Read project rules, write task state |
| `jcode.implement` | Lock files being modified |
| `jcode.review` | Read implementation artifacts |
| `jcode.test` | Lock execution environment |
| `jcode.conductor` | Release context lock on DELIVER |

### 5.2 Rule Engine Integration

JCode tools consult OMO Rule Engine via `om_rules` parameter:

- `jcode.implement`: Check `R001_no_skip_review`, `R002_test_required`
- `jcode.review`: Check `R003_nfr_required`, `R004_human_intervention_on_error`
- `jcode.test`: Check `R005_evidence_required`

Rule Engine response embedded in tool output payload.

---

## 6. Audit Log Integration

Each tool call generates audit log entry:

```json
{
  "timestamp": "2026-02-24T10:30:00Z",
  "om_session_id": "omo_session_abc123",
  "jcode_tool": "jcode.analyze",
  "context_lock_id": "cl_123456",
  "input": {...},
  "output": {...},
  "duration_ms": 1250,
  "agent": "analyst",
  "result": "SUCCESS",
  "error": null,
  "iteration": 1
}
```

**Storage**: `.omo/audit/jcode_tools.jsonl`

---

## 7. Error Handling

### 7.1 Error Propagation

| Error Type | Tool Response | OMO Action |
|------------|--------------|------------|
| NON-VERIFIABLE | `error.type`, `error.action = "HUMAN_INTERVENTION"` | Show UI dialog |
| RULE_VIOLATION | `error.type`, `error.action = "STOP"` | Terminate workflow |
| EVIDENCE_UNAVAILABLE | `error.type`, `error.action = "RETRY"` | Retry with different evidence source |
| ITERATION_OVERFLOW | `error.type`, `error.action = "HUMAN_INTERVENTION"` | Show延长/终止 dialog |
| STRUCTURAL_VIOLATION | `error.type`, `error.action = "STOP"` | Terminate + alert |

### 7.2 Fallback Behavior

When JCode tool fails:
1. OMO checks `error.action`
2. If `HUMAN_INTERVENTION`: Show interactive dialog to user
3. If `RETRY`: Retry with adapted inputs
4. If `STOP`: Terminate workflow, release context lock
5. If `CONTINUE`: Log warning, proceed with best effort

---

## 8. Testing

### 8.1 Tool Validation

```python
# test_jcode_tools.py
import pytest
from jcode.mcp.server import JCodeMCPServer

@pytest.fixture
def server():
    return JCodeMCPServer()

def test_jcode_analyze_schema(server):
    tool = server.server.get_tool("jcode.analyze")
    assert tool.name == "jcode.analyze"
    assert "context_lock_id" in tool.inputSchema["properties"]
    assert "verifiability" in tool.outputSchema["properties"]["payload"]["properties"]

def test_jcode_conductor_stop_condition(server):
    result = server._handle_conductor(
        review_result="REJECTED",
        test_result="FAILED",
        iteration_count=5,
        max_iterations=5
    )
    assert result["payload"]["decision"] == "STOP"
    assert result["error"]["action"] == "HUMAN_INTERVENTION"
```

---

## 9. Future Extensions

### 9.1 Planned Enhancements

- **Async Tool Calls**: Support async tool execution for parallel phases
- **Tool Chaining**: Pre-define tool sequences as " workflows"
- **Custom Tools**: Allow user-defined tools via `jcode.custom_tool`
- **Tool Metrics**: Expose tool performance metrics via `jcode.metrics`

### 9.2 Optional integrations

- **Multi-Session Lock**: Support cross-session context sharing
- **Distributed Tools**: Scale JCode tools across multiple instances
- **Tool Versioning**: Support multiple tool versions via `tool_version` parameter

---

> **MCP enables language-agnostic integration.**
> **JCode provides governance via constitutional constraints.**

**END OF SUPERPOWERS_EXTENSION**
