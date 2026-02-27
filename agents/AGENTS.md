# JCode Agent System - MCP-Based Governance

> **Status:** v3.0 COMPLETE  
> **Type:** Standalone MCP Agent System  
> **Protocol:** JSON-RPC 2.0 over HTTP (MCP Standard)  
> **Integration:** OpenCode Agent Registry + MCP Tool Calling  
> **Generated:** 2026-02-27

---

## What Makes JCode Different

JCode is **NOT** a traditional agent system. It's a **MCP-native governance layer**:

- ✅ 6 specialized agents exposed as **MCP tools**
- ✅ Communicates via **JSON-RPC 2.0** protocol
- ✅ Discovered by OpenCode through **MCP tool discovery**
- ✅ Each agent is a **stateless tool invocation**, not a persistent process
- ✅ Runs on-demand via `python -m mcp.server`

---

## MCP Architecture

### Tool Discovery

OpenCode discovers JCode agents through the MCP `tools/list` method:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

Returns 6 tools:
- `analyze` - Problem analysis and risk assessment
- `plan` - Task decomposition and planning  
- `implement` - Code implementation
- `review` - Code review (APPROVED/REJECTED)
- `test` - Test verification (PASSED/FAILED)
- `conductor` - Final arbitration (DELIVER/ITERATE/STOP)

### Tool Invocation

Each agent is invoked via the MCP `tools/call` method:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "analyze",
    "arguments": {
      "context_lock_id": "session-123",
      "input_data": {"problem_statement": "..."},
      "mode": "full"
    }
  }
}
```

### Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": "Analysis complete: [ANALYSIS]\n\nVerifiability: HARD\nAction: CONTINUE"
    }]
  }
}
```

---

## 6 MCP Tools = 6 Agents

| MCP Tool | Agent Name | Role | Output |
|----------|------------|------|--------|
| `analyze` | @jcode-analyst | 问题侦察官 (司马迁) | Analysis + Risk assessment |
| `plan` | @jcode-planner | 法令制定官 (商鞅) | Verifiable task list |
| `implement` | @jcode-implementer | 执行工匠 (鲁班) | Code changes |
| `review` | @jcode-reviewer | 否决官 (包拯) | APPROVED / REJECTED |
| `test` | @jcode-tester | 证据官 (张衡) | PASSED / FAILED |
| `conductor` | @jcode-conductor | 终局裁决 (韩非子) | DELIVER / ITERATE / STOP |

### Primary Agent (@jcode)

The `@jcode` agent is a **workflow orchestrator** that internally chains the 6 MCP tool calls:

```
User Request
    ↓
@jcode (Orchestrator)
    ↓
tools/call analyze → tools/call plan → tools/call implement
    ↓
tools/call review → tools/call test → tools/call conductor
    ↓
Final Result
```

---

## MCP Server

### Start the Server

```bash
python -m mcp.server --port 8080
```

### Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Health check + tool count |
| `POST /mcp` | JSON-RPC 2.0 endpoint for tool discovery and invocation |

### Configuration

The MCP server is registered in OpenCode via `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "jcode": {
      "type": "local",
      "command": ["python", "-m", "mcp.server", "--port", "8080"],
      "environment": {
        "PYTHONPATH": "/path/to/jcode"
      },
      "enabled": true
    }
  }
}
```

---

## Agent Workflow (MCP Chain)

```
┌─────────────────────────────────────────────────────────────┐
│  User: @jcode 实现一个用户登录功能                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  @jcode (Primary Agent)                                      │
│  └─ Calls: POST /mcp {method: "tools/call", params: {name: "analyze"}} │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Server → AnalystAgent.execute()                         │
│  Returns: {verifiability: "HARD", action: "CONTINUE"}         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  @jcode calls: tools/call plan → PlannerAgent                │
│  Returns: {tasks: [...], action: "CONTINUE"}                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
            [ ... continues through all 6 tools ... ]
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Final: tools/call conductor → ConductorAgent                │
│  Returns: {decision: "DELIVER"}                              │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
jcode/
├── mcp/
│   ├── server.py              # MCP HTTP server (FastAPI + JSON-RPC 2.0)
│   └── jcode_server.py        # Tool definitions and discovery
├── core/agents/               # Agent implementations (called by MCP server)
│   ├── analyst.py             # analyze tool implementation
│   ├── planner.py             # plan tool implementation
│   ├── implementer.py         # implement tool implementation
│   ├── reviewer.py            # review tool implementation
│   ├── tester.py              # test tool implementation
│   └── conductor.py           # conductor tool implementation
├── config/agents/             # OpenCode Agent configurations
│   ├── jcode.md               # Primary orchestrator agent
│   ├── jcode-analyst.md       # Subagent: calls MCP analyze tool
│   ├── jcode-planner.md       # Subagent: calls MCP plan tool
│   ├── jcode-implementer.md   # Subagent: calls MCP implement tool
│   ├── jcode-reviewer.md      # Subagent: calls MCP review tool
│   ├── jcode-tester.md        # Subagent: calls MCP test tool
│   └── jcode-conductor.md     # Subagent: calls MCP conductor tool
├── skills/jcode-mcp/
│   └── SKILL.md               # OpenCode SKILL registration (MCP endpoint)
├── install.py                 # One-click installation
└── agents/
    └── AGENTS.md              # This file
```

---

## Usage

### Full Workflow (via @jcode)

```
@jcode 实现一个用户登录功能，支持邮箱和手机号验证
```

JCode automatically chains 6 MCP tool calls:
1. `analyze` - Analyze requirements
2. `plan` - Create verifiable tasks
3. `implement` - Write code
4. `review` - Code review
5. `test` - Run tests
6. `conductor` - Make final decision

### Individual Tool Calls

You can also call individual MCP tools directly:

```
/jcode-mcp analyze "评估这个需求的可行性"
/jcode-mcp review "审查这段代码"
/jcode-mcp test "运行测试"
```

Or use the agent shortcuts:

```
@jcode-analyst 分析这个需求的复杂度
@jcode-reviewer 检查这段代码的质量
```

---

## Why MCP?

1. **Standard Protocol** - Uses industry-standard JSON-RPC 2.0
2. **Tool Discovery** - OpenCode auto-discovers available tools
3. **Stateless** - Each invocation is independent, no process management
4. **Composable** - Agents can be called individually or chained
5. **Language Agnostic** - Could be implemented in any language

---

## Installation

```bash
cd jcode
python install.py --global
```

This installs:
- 7 Agent configs to `~/.config/opencode/agent/`
- MCP server registration to `~/.config/opencode/opencode.json`

---

## History

### v3.0 (Current)
- ✅ **MCP-native architecture** - 6 agents as MCP tools
- ✅ **JSON-RPC 2.0 protocol** - Standard MCP communication
- ✅ **Standalone system** - No OMO dependency
- ✅ **@jcode Primary Agent** - Workflow orchestration
- ✅ **One-click installation**

### v2.x
- Design phase, OMO-dependent

### v1.x
- Prototype phase

---

**JCode: MCP-native governance for OpenCode.**