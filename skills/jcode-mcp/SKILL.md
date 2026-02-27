---
name: jcode-mcp
description: |
  JCode MCP Server - 6 agent governance tools exposed via MCP protocol.
  Each agent is an MCP tool: analyze, plan, implement, review, test, conductor
version: "3.0.0"
tools:
  - name: analyze
    description: Problem analysis and risk assessment (JCode Analyst Agent)
  - name: plan
    description: Task decomposition and planning (JCode Planner Agent)
  - name: implement
    description: Code implementation (JCode Implementer Agent)
  - name: review
    description: Code review returning APPROVED/REJECTED (JCode Reviewer Agent)
  - name: test
    description: Test verification returning PASSED/FAILED (JCode Tester Agent)
  - name: conductor
    description: Final arbitration returning DELIVER/ITERATE/STOP (JCode Conductor Agent)
mcp:
  command: python -m mcp.server
  args: ["--port", "8080"]
---

# JCode MCP Server

**JCode v3.0** is a **Model Context Protocol (MCP)** server that exposes 6 governance agents as tools.

## What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open protocol that standardizes how applications provide context to LLMs. JCode implements MCP to expose its 6 governance agents as discoverable tools.

## Architecture

```
OpenCode
    ↓ POST /mcp {jsonrpc: "2.0", method: "tools/list"}
MCP Server (mcp/server.py)
    ↓ Returns 6 tools: analyze, plan, implement, review, test, conductor
    ↓ POST /mcp {method: "tools/call", params: {name: "analyze"}}
Agent Implementation (core/agents/*.py)
    ↓ Executes business logic
    ↓ Returns structured result
```

## MCP Tools

| Tool | Agent | Input | Output |
|------|-------|-------|--------|
| `analyze` | Analyst | `problem_statement`, `requirements` | Analysis + risk assessment |
| `plan` | Planner | `analysis_result`, `constraints` | Verifiable task list |
| `implement` | Implementer | `tasks`, `analysis_result` | Code changes |
| `review` | Reviewer | `tasks`, `implementation` | `APPROVED` / `REJECTED` |
| `test` | Tester | `verify_by`, `implementation` | `PASSED` / `FAILED` |
| `conductor` | Conductor | `review_result`, `test_result`, `iteration` | `DELIVER` / `ITERATE` / `STOP` |

## Protocol Details

### Tool Discovery

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "analyze",
        "description": "Problem analysis and risk assessment",
        "inputSchema": {...}
      },
      ...
    ]
  }
}
```

### Tool Invocation

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "analyze",
      "arguments": {
        "context_lock_id": "session-123",
        "input_data": {
          "problem_statement": "Implement user login"
        },
        "mode": "full"
      }
    }
  }'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": "Analysis complete: [ANALYSIS]..."
    }]
  }
}
```

## Error Codes

Standard JSON-RPC 2.0 error codes:

| Code | Meaning |
|------|---------|
| `-32700` | Parse error |
| `-32600` | Invalid request |
| `-32601` | Method not found |
| `-32602` | Invalid params |
| `-32603` | Internal error |

## Usage

### Start MCP Server

```bash
python -m mcp.server --port 8080
```

### Via OpenCode Agent

```
@jcode-analyst 分析这个需求的复杂度
@jcode-reviewer 审查这段代码
```

### Direct MCP Tool Call

```
/jcode-mcp analyze "评估这个需求的可行性"
/jcode-mcp review "检查这段代码"
```

## Parameters

All tools accept:

| Parameter | Type | Description |
|-----------|------|-------------|
| `context_lock_id` | string | Session identifier |
| `input_data` | object | Tool-specific input |
| `mode` | string | Execution mode: `full`, `light`, `safe`, `fast`, `custom` |

## Integration

The MCP server is registered in OpenCode via:

```json
{
  "mcp": {
    "jcode": {
      "type": "local",
      "command": ["python", "-m", "mcp.server", "--port", "8080"],
      "environment": {"PYTHONPATH": "/path/to/jcode"},
      "enabled": true
    }
  }
}
```

---

**JCode MCP Server: Governance as a Tool.**