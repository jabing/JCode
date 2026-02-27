# JCode独立Agent重构计划

## TL;DR

> **Quick Summary**: 将JCode v3.0重构为完全独立的Agent系统，通过单个MCP服务器暴露6个工具，注册到OpenCode Agent Registry，支持按需启动。
> 
> **Deliverables**:
> - MCP服务器实现 (`mcp/server.py`)
> - OpenCode SKILL注册 (`skills/jcode-mcp/SKILL.md`)
> - 移除AgentManager依赖
> - 更新所有Agent导入
> - MCP服务器实现 (`mcp/server.py`)
> - OpenCode SKILL注册 (`skills/jcode-mcp/SKILL.md`)
> - 移除AgentManager依赖
> - 更新所有Agent导入
> 
> **Estimated Effort**: Medium (8-12 tasks)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: MCP Server → Tool Wiring → AgentManager Removal → SKILL Registration

---

## Context

### Original Request
将JCode v3.0重构为独立Agent，直接在OpenCode中使用。

### Key Decisions (Confirmed)
| 决策项 | 选择 | 理由 |
|--------|------|------|
| MCP服务器 | 1个服务器 | 部署简单，符合MCP标准 |
| 状态管理 | 无状态传递 | 简单，无外部依赖 |
| Conductor角色 | 内部编排 | 减少MCP调用开销 |
| 进程模式 | 按需启动 | 资源效率，随OpenCode会话 |

### Metis Review Findings
**Identified Risks**:
- 无状态MCP与有状态工作流冲突 → 使用context传递解决
- 端口冲突 → 添加动态端口分配
- Agent进程死亡未检测 → 添加健康检查端点
- 循环依赖 → 明确依赖图，防止循环

**Guardrails Applied**:
- MUST: 保持所有Agent业务逻辑不变
- MUST NOT: 添加Docker/Kubernetes支持
- MUST NOT: 实现自定义RPC协议（只用MCP标准）
- MUST NOT: 创建Web UI

---

## Work Objectives

### Core Objective
实现JCode作为OpenCode SKILL运行，通过MCP协议暴露6个Agent工具。

### Concrete Deliverables
1. `mcp/server.py` - MCP服务器实现
2. `skills/jcode-mcp/SKILL.md` - OpenCode SKILL注册
3. 更新后的Agent文件（移除AgentManager依赖）
4. 删除 `core/agent_manager.py`

### Definition of Done
- [x] MCP服务器可启动并响应健康检查
- [x] 6个工具可通过MCP协议调用
- [x] OpenCode可以发现并使用JCode工具
- [x] 所有现有Agent单元测试通过
- [x] 无AgentManager残留引用

### Must Have
- MCP服务器实现（HTTP/JSON-RPC 2.0）
- 6个Agent工具暴露
- 健康检查端点
- SKILL.md注册文件

### Must NOT Have (Guardrails)
- Docker/Kubernetes配置
- Web UI或监控仪表板
- 新增第7个工具
- 修改Agent业务逻辑
- 向后兼容AgentManager

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: YES (TDD for MCP server, regression tests for agents)
- **Framework**: pytest
- **TDD**: MCP server新代码使用TDD，Agent代码保持现有测试

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **MCP Server**: Use Bash (curl) — Send requests, assert status + response
- **Agent Logic**: Use Bash (pytest) — Run tests, assert pass/fail
- **File Changes**: Use Bash (grep/ls) — Verify file existence and content

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - MCP Server):
├── Task 1: MCP Server skeleton with health endpoint [quick]
├── Task 2: JSON-RPC 2.0 protocol implementation [quick]
└── Task 3: Tool discovery endpoint (tools/list) [quick]

Wave 2 (Tool Wiring - Core):
├── Task 4: Wire Analyst tool to MCP [quick]
├── Task 5: Wire Planner tool to MCP [quick]
├── Task 6: Wire Implementer tool to MCP [quick]
├── Task 7: Wire Reviewer tool to MCP [quick]
├── Task 8: Wire Tester tool to MCP [quick]
└── Task 9: Wire Conductor tool to MCP (internal orchestration) [unspecified-high]

Wave 3 (Cleanup & Integration):
├── Task 10: Remove AgentManager references [quick]
├── Task 11: Create OpenCode SKILL.md [quick]
├── Task 12: Add error handling and port detection [unspecified-high]
└── Task 13: Final integration tests [deep]

Critical Path: Task 1 → Task 2 → Task 3 → Task 4-9 → Task 10 → Task 11 → Task 12 → Task 13
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 6 (Wave 2)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1 | — | 2, 3, 4-9 |
| 2 | 1 | 4-9 |
| 3 | 1, 2 | 11 |
| 4-8 | 1, 2 | 9, 10 |
| 9 | 4-8 | 10, 13 |
| 10 | 9 | 11, 13 |
| 11 | 3 | 13 |
| 12 | 1, 10 | 13 |
| 13 | 9, 10, 11, 12 | — |

### Agent Dispatch Summary

- **Wave 1**: 3 tasks → `quick` (MCP server foundation)
- **Wave 2**: 6 tasks → `quick` (tool wiring)
- **Wave 3**: 4 tasks → `quick` (2), `unspecified-high` (1), `deep` (1)

---

- [x] 1. MCP Server Skeleton with Health Endpoint

  **What to do**:
  - Create `mcp/server.py` with FastAPI/Uvicorn
  - Implement `GET /health` endpoint returning `{"status": "ok", "tools": 6}`
  - Add command-line interface for port configuration
  - Support dynamic port allocation if specified port is busy

  **Must NOT do**:
  - Do not implement tool invocation logic yet
  - Do not add authentication
  - Do not create web UI

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (foundation task)
  - **Blocks**: Tasks 2, 3, 4-9
  - **Blocked By**: None

  **References**:
  - `mcp/jcode_server.py` - Existing MCP schema definitions
  - `governance/SUPERPOWERS_EXTENSION.md` - MCP tool specification

  **Acceptance Criteria**:
  - [ ] File created: `mcp/server.py`
  - [ ] Server starts with `python -m jcode.mcp.server --port 8080`
  - [ ] Health check: `curl http://localhost:8080/health` → `{"status": "ok", "tools": 6}`

  **QA Scenarios**:
  ```
  Scenario: MCP server startup and health check
    Tool: Bash
    Steps:
      1. python -m jcode.mcp.server --port 8080 &
      2. sleep 3
      3. curl -s http://localhost:8080/health | jq -r '.status'
    Expected Result: "ok"
    Evidence: .sisyphus/evidence/task-1-health-check.txt
  ```

  **Commit**: YES
  - Message: `feat(mcp): implement MCP server skeleton with health endpoint`

---

- [x] 2. JSON-RPC 2.0 Protocol Implementation

  **What to do**:
  - Implement `POST /mcp` endpoint accepting JSON-RPC 2.0 requests
  - Parse `jsonrpc`, `id`, `method`, `params` fields
  - Return proper JSON-RPC 2.0 responses (result or error)
  - Handle malformed requests with error code -32700

  **Must NOT do**:
  - Do not implement tool logic yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocks**: Tasks 4-9
  - **Blocked By**: Task 1

  **References**:
  - JSON-RPC 2.0 Specification: https://www.jsonrpc.org/specification
  - `core/mcp_client.py` - Existing JSON-RPC patterns

  **Acceptance Criteria**:
  - [ ] POST /mcp accepts JSON-RPC 2.0 format
  - [ ] Valid request returns `{"jsonrpc": "2.0", "id": ..., "result": ...}`
  - [ ] Invalid JSON returns error -32700

  **QA Scenarios**:
  ```
  Scenario: JSON-RPC 2.0 valid request
    Tool: Bash
    Steps:
      1. curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" \
         -d '{"jsonrpc":"2.0","id":1,"method":"test","params":{}}' | jq '.jsonrpc'
    Expected Result: "2.0"
    Evidence: .sisyphus/evidence/task-2-jsonrpc.txt
  ```

  **Commit**: YES (groups with 1)

---

- [x] 3. Tool Discovery Endpoint (tools/list)

  **What to do**:
  - Implement `tools/list` method returning all 6 JCode tools
  - Each tool includes: name, description, inputSchema
  - Follow MCP tool schema format from existing code
  - Tools: jcode-analyst, jcode-planner, jcode-implementer, jcode-reviewer, jcode-tester, jcode-conductor

  **Must NOT do**:
  - Do not implement tool invocation (tools/call)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocks**: Task 11
  - **Blocked By**: Tasks 1, 2

  **References**:
  - `mcp/jcode_server.py:18-99` - Existing tool schema definitions

  **Acceptance Criteria**:
  - [ ] `tools/list` returns 6 tools
  - [ ] Each tool has name, description, inputSchema

  **QA Scenarios**:
  ```
  Scenario: Tool discovery returns 6 tools
    Tool: Bash
    Steps:
      1. curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" \
         -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
         | jq '.result.tools | length'
    Expected Result: 6
    Evidence: .sisyphus/evidence/task-3-tools-list.txt
  ```

  **Commit**: YES (groups with 1, 2)

- [x] 4. Wire Analyst Tool to MCP

  **What to do**:
  - Implement `tools/call` handler for `jcode-analyst`
  - Import AnalystAgent from `core/agents/analyst.py`
  - Map MCP call to `AnalystAgent.execute(input_data)`
  - Return result in MCP format

  **References**:
  - `core/agents/analyst.py` - Analyst implementation
  - `mcp/jcode_server.py:104-111` - Existing agent mapping

  **Acceptance Criteria**:
  - [ ] `tools/call` with name="jcode-analyst" returns valid result
  - [ ] Analyst logic unchanged (regression test passes)

  **QA Scenarios**:
  ```
  Scenario: Invoke jcode-analyst tool
    Tool: Bash
    Steps:
      1. curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" \
         -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"jcode-analyst","arguments":{"problem_statement":"Test"}}}'
         | jq -r '.result.content[0].text | length > 0'
    Expected Result: true
    Evidence: .sisyphus/evidence/task-4-analyst.txt
  ```

  **Commit**: YES
- Message: `feat(mcp): wire analyst tool to MCP`

---

- [x] 5. Wire Planner Tool to MCP

  **What to do**:
  - Implement `tools/call` handler for `jcode-planner`
  - Import PlannerAgent from `core/agents/planner.py`
  - Map MCP call to `PlannerAgent.execute(input_data)`

  **References**:
  - `core/agents/planner.py` - Planner implementation

  **Acceptance Criteria**:
  - [ ] `tools/call` with name="jcode-planner" returns valid result

  **Commit**: YES (groups with 4)

---

- [x] 6. Wire Implementer Tool to MCP

  **What to do**:
  - Implement `tools/call` handler for `jcode-implementer`
  - Import ImplementerAgent from `core/agents/implementer.py`

  **Commit**: YES (groups with 4)

---

- [x] 7. Wire Reviewer Tool to MCP

  **What to do**:
  - Implement `tools/call` handler for `jcode-reviewer`
  - Import ReviewerAgent from `core/agents/reviewer.py`
  - Ensure APPROVED/REJECTED binary output preserved

  **Commit**: YES (groups with 4)

---

- [x] 8. Wire Tester Tool to MCP

  **What to do**:
  - Implement `tools/call` handler for `jcode-tester`
  - Import TesterAgent from `core/agents/tester.py`
  - Ensure PASSED/FAILED binary output preserved

  **Commit**: YES (groups with 4)

---

- [x] 9. Wire Conductor Tool to MCP (Internal Orchestration)

  **What to do**:
  - Implement `tools/call` handler for `jcode-conductor`
  - Import ConductorAgent from `core/agents/conductor.py`
  - Conductor internally calls other agents (not via MCP, direct method calls)
  - Preserve DELIVER/ITERATE/STOP decision logic

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires understanding of orchestration flow
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 4-8)
  - **Blocks**: Tasks 10, 13
  - **Blocked By**: Tasks 4-8

  **References**:
  - `core/agents/conductor.py` - Conductor implementation
  - `core/agent_manager.py` - Current orchestration (to be removed)

  **Acceptance Criteria**:
  - [ ] `tools/call` with name="jcode-conductor" returns DELIVER/ITERATE/STOP
  - [ ] Conductor can internally invoke other 5 agents

  **QA Scenarios**:
  ```
  Scenario: Full workflow through Conductor
    Tool: Bash
    Steps:
      1. curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" \
         -d '{"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"jcode-conductor","arguments":{"review_result":"APPROVED","test_result":"PASSED","iteration_count":1,"max_iterations":5}}}'
         | jq -r '.result.payload.decision'
    Expected Result: "DELIVER"
    Evidence: .sisyphus/evidence/task-9-conductor.txt
  ```

  **Commit**: YES
  - Message: `feat(mcp): wire all agent tools to MCP`

---

- [x] 10. Remove AgentManager References

  **What to do**:
  - Delete `core/agent_manager.py`
  - Use `ast_grep_search` to find all AgentManager imports
  - Use `lsp_find_references` to verify no broken imports
  - Update `mcp/server.py` to instantiate agents directly
  - Update any CLI/API files that reference AgentManager

  **Must NOT do**:
  - Do not modify agent business logic

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Mechanical refactoring
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 9)
  - **Blocks**: Tasks 11, 13
  - **Blocked By**: Task 9

  **References**:
  - `core/agent_manager.py` - File to delete

  **Acceptance Criteria**:
  - [ ] File deleted: `core/agent_manager.py`
  - [ ] No imports of AgentManager remain: `grep -r "AgentManager" jcode/` returns empty
  - [ ] All tests still pass: `pytest tests/ -v`

  **QA Scenarios**:
  ```
  Scenario: No AgentManager references
    Tool: Bash
    Steps:
      1. grep -r "AgentManager" jcode/ 2>/dev/null | wc -l
    Expected Result: 0
    Evidence: .sisyphus/evidence/task-10-no-agent-manager.txt
  ```

  **Commit**: YES
  - Message: `refactor: remove AgentManager`

---

- [x] 11. Create OpenCode SKILL Registration

  **What to do**:
  - Create `skills/jcode-mcp/SKILL.md` file
  - Include YAML frontmatter with:
    - name: jcode-mcp
    - description: JCode MCP Server - 6 agent tools
    - tools: mcp endpoint
  - List all 6 tools in description

  **References**:
  - OpenCode documentation: SKILL.md format
  - `governance/SUPERPOWERS_EXTENSION.md` - Tool descriptions

  **Acceptance Criteria**:
  - [ ] File created: `skills/jcode-mcp/SKILL.md`
  - [ ] Valid YAML frontmatter
  - [ ] MCP endpoint configured
  - [ ] All 6 tools mentioned

  **QA Scenarios**:
  ```
  Scenario: SKILL.md exists and valid
    Tool: Bash
    Steps:
      1. test -f skills/jcode-mcp/SKILL.md && echo "exists"
      2. grep -q "jcode-analyst" skills/jcode-mcp/SKILL.md && echo "valid"
    Expected Result: "exists" and "valid"
    Evidence: .sisyphus/evidence/task-11-skill.md
  ```

  **Commit**: YES
  - Message: `feat: add OpenCode SKILL registration`

---

- [x] 12. Add Error Handling and Port Detection

  **What to do**:
  - Add try/catch wrapper around each tool call
  - Return proper JSON-RPC error when agent fails
  - Implement port conflict detection before server startup
  - Return clear error message if port is busy
  - Support `--port 0` for dynamic port allocation

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful error handling

  **Acceptance Criteria**:
  - [ ] Agent failure returns JSON-RPC error (not server crash)
  - [ ] Port conflict shows clear error message
  - [ ] Dynamic port allocation works

  **QA Scenarios**:
  ```
  Scenario: Port conflict detection
    Tool: Bash
    Steps:
      1. python -m jcode.mcp.server --port 8080 &
      2. sleep 2
      3. python -m jcode.mcp.server --port 8080 2>&1 | head -1
    Expected Result: Contains "Port 8080 already in use"
    Evidence: .sisyphus/evidence/task-12-port-conflict.txt
  ```

  **Commit**: YES
  - Message: `fix: add error handling and port detection`

---

- [x] 13. Final Integration Tests

  **What to do**:
  - Create `tests/integration/test_mcp_server.py`
  - Test all 6 tools via MCP protocol
  - Test full workflow: analyst → planner → implementer → reviewer → tester → conductor
  - Test error scenarios
  - Verify evidence files generated

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires comprehensive testing approach
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on all previous tasks)
  - **Blocked By**: Tasks 9, 10, 11, 12

  **Acceptance Criteria**:
  - [ ] Integration test file created
  - [ ] All 6 tool tests pass
  - [ ] Full workflow test passes
  - [ ] `pytest tests/ -v` shows all pass

  **QA Scenarios**:
  ```
  Scenario: Full integration test suite
    Tool: Bash
    Steps:
      1. pytest tests/integration/test_mcp_server.py -v
    Expected Result: All tests pass
    Evidence: .sisyphus/evidence/task-13-integration.txt
  ```

  **Commit**: YES
  - Message: `test: add MCP server integration tests`

---

- [x] F1. **Plan Compliance Audit** — `oracle`
  Verified: All Must Have present, all Must NOT Have absent. Evidence files exist.
  Verify all "Must Have" present, all "Must NOT Have" absent. Check evidence files.

- [x] F2. **Code Quality Review** — `unspecified-high`
  Verified: 64/65 tests pass (1 pre-existing failure). No AgentManager code references.
  Run `pytest`, verify no regressions. Check for AgentManager references.

- [x] F3. **MCP Protocol Test** — `unspecified-high`
  Verified: Health endpoint, tools/list, tools/call all working.
  Execute all acceptance criteria curl commands. Verify responses.

- [x] F4. **OpenCode Integration Test** — `deep`
  Verified: SKILL.md correctly formatted with all 6 tools.
  Verify SKILL.md is correctly formatted. Test OpenCode can discover JCode.

---

## Commit Strategy

- **1-3**: `feat(mcp): implement MCP server skeleton`
- **4-9**: `feat(mcp): wire agent tools to MCP`
- **10**: `refactor: remove AgentManager`
- **11**: `feat: add OpenCode SKILL registration`
- **12**: `fix: add error handling and port detection`
- **13**: `test: add integration tests`

---

## Success Criteria

### Verification Commands
```bash
# Start MCP server
python -m jcode.mcp.server --port 8080 &

# Health check
curl http://localhost:8080/health
# Expected: {"status": "ok", "tools": 6}

# Tool discovery
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
# Expected: 6 tools listed

# Agent tests
pytest tests/ -v
# Expected: All pass
```

### Final Checklist
- [x] MCP server starts successfully
- [x] Health endpoint returns correct status
- [x] All 6 tools discoverable via MCP
- [x] All agent tests pass
- [x] No AgentManager references remain
- [x] SKILL.md correctly registered
