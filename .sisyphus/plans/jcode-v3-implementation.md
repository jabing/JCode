# JCode v3.0 Implementation Plan - OpenCode/Superpowers Extension Layer

## TL;DR

> **Quick Summary**: Implement JCode v3.0 as OpenCode/Superpowers governance extension layer,> 
> **Deliverables**:
> - Core modules (`core/`) - Agent management, MCP client, Rule engine, Audit logger, Switch manager
> - API layer (`api/`) - FastAPI REST endpoints for MCP tool registration
> - CLI tools (`cli/`) - Command-line interface
 Configuration management
> - Configuration (`config/`) - YAML configuration files
> - Dependencies (`requirements.txt`, `pyproject.toml`)

> **Estimated Effort**: Large (15-20 tasks)
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: core → api → cli → config → integration tests

---

## Context

### Original Request
Implement JCode v3.0 as OpenCode/Superpowers governance extension layer based on completed design documents in `governance/`.

### Design Phase Completion
- ✅ 7 new governance documents (4,523 lines)
- ✅ MCP Tool definitions for all 10 tools
- ✅ 4-level switch mechanism design
- ✅ AGENTS.md updates

### Implementation Approach
- **Language**: Python 3.8+
- **Framework**: FastAPI for REST API
- **CLI**: Click + Typer
- **MCP**: mcp Python SDK
- **Configuration**: YAML

---

## Work Objectives

### Core Objective
Implement production-ready JCode v3.0 with full MCP integration, 4-level switch mechanism, and audit logging.

### Concrete Deliverables
1. `core/__init__.py` - Core module initialization
2. `core/agent_manager.py` - Agent lifecycle management
3. `core/mcp_client.py` - MCP protocol client
4. `core/rule_engine.py` - Rule execution engine
5. `core/audit_logger.py` - Audit logging system
6. `core/switch_manager.py` - 4-level switch mechanism
7. `core/context_lock.py` - Context lock integration
8. `core/incremental_build.py` - Incremental build integration
9. `api/__init__.py` - API module initialization
10. `api/main.py` - FastAPI application
11. `api/routes/` - REST endpoints
12. `api/models/` - Pydantic models
13. `cli/__init__.py` - CLI module initialization
14. `cli/commands.py` - CLI commands
15. `cli/config.py` - Configuration management
16. `config/jcode_config.yaml` - Default configuration
17. `requirements.txt` - Python dependencies
18. `pyproject.toml` - Project metadata

### Definition of Done
- [ ] All core modules implemented and tested
- [ ] API endpoints functional
- [ ] CLI commands working
- [ ] Configuration loading correctly
- [ ] All unit tests passing

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - Project Setup):
├── Task 1: Create project structure and config files [quick]
├── Task 2: Create requirements.txt and pyproject.toml [quick]
├── Task 3: Create core/__init__.py with base classes [quick]

Wave 2 (Core Modules - Sequential but logical):
├── Task 4: Implement core/switch_manager.py [unspecified-high]
├── Task 5: Implement core/audit_logger.py [unspecified-high]
├── Task 6: Implement core/rule_engine.py [unspecified-high]
├── Task 7: Implement core/context_lock.py [unspecified-high]
├── Task 8: Implement core/incremental_build.py [unspecified-high]
├── Task 9: Implement core/mcp_client.py [unspecified-high]
├── Task 10: Implement core/agent_manager.py [unspecified-high]

Wave 3 (API Layer):
├── Task 11: Create api/models/ with Pydantic schemas [quick]
├── Task 12: Implement api/routes/ with REST endpoints [unspecified-high]
├── Task 13: Implement api/main.py FastAPI app [unspecified-high]

Wave 4 (CLI Layer):
├── Task 14: Implement cli/config.py [quick]
├── Task 15: Implement cli/commands.py [unspecified-high]

Wave 5 (Integration & Verification):
├── Task 16: Create integration tests [unspecified-high]
├── Task 17: Create documentation [quick]
└── Task 18: Final verification [oracle]

Critical Path: Task 1 → Task 4-10 → Task 11-13 → Task 14-15 → Task 16-18
Parallel Speedup: ~50% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1 | — | 2, 3 |
| 2 | 1 | — |
| 3 | 1 | 4-10 |
| 4 | 3 | 10 |
| 5 | 3, 4 | 10 |
| 6 | 3, 4, 5 | 10 |
| 7 | 3, 6 | 10 |
| 8 | 3, 6 | 10 |
| 9 | 3 | 10 | 10 |
| 10 | 3, 4, 5, 6, 7, 8, 9 | 11-15 |
| 11 | 10 | 12, 13 |
| 12 | 10, 11 | 13 |
| 13 | 10, 11, 12 | 16-18 |
| 14 | 10 | 15 |
| 15 | 10, 14 | 16-18 |
| 16 | 13, 15 | 17, 18 |
| 17 | 16 | 18 |
| 18 | 16, 17 | — |

---

## TODOs

- [ ] 1. Create project structure and config files

  **What to do**:
  - Create directory structure: `core/`, `api/`, `api/routes/`, `api/models/`, `cli/`, `config/`
  - Create `config/jcode_config.yaml` with default configuration
  - Create empty `__init__.py` files for Python packages

  **References**:
  - `governance/JCODE_SWITCH.md` - Switch configuration format
  - `governance/OMO_INTEGRATION.md` - OMO configuration extension

  **Acceptance Criteria**:
  - [ ] All directories created
  - [ ] config/jcode_config.yaml exists with valid YAML
  - [ ] All __init__.py files exist

  **QA Scenarios**:
  ```
  Scenario: Verify project structure
    Tool: Bash
    Steps:
      1. ls -la core/ api/ cli/ config/
      2. cat config/jcode_config.yaml
    Expected Result: All directories and files exist
  ```

  **Commit**: YES
  - Message: `feat: create project structure and configuration`
  - Files: All new directories and files

---

- [ ] 2. Create requirements.txt and pyproject.toml

  **What to do**:
  - Create `requirements.txt` with all Python dependencies
  - Create `pyproject.toml` with project metadata
  - Include: mcp, fastapi, uvicorn, pydantic, pyyaml, click, typer

  **References**:
  - `governance/OMO_INTEGRATION.md` - MCP dependencies
  - `governance/SUPERPOWERS_EXTENSION.md` - Tool definitions

  **Acceptance Criteria**:
  - [ ] requirements.txt exists with all dependencies
  - [ ] pyproject.toml exists with valid TOML
  - [ ] Dependencies can be installed with pip

  **QA Scenarios**:
  ```
  Scenario: Verify dependencies
    Tool: Bash
    Steps:
      1. cat requirements.txt
      2. pip install -r requirements.txt (dry-run or verify syntax)
    Expected Result: All dependencies valid
  ```

  **Commit**: YES (groups with 1)

---

- [ ] 3. Create core/__init__.py with base classes

  **What to do**:
  - Create `core/__init__.py` with module exports
  - Define base classes: JCodeError, AgentRole, TaskResult
  - Define constants and enums

  **References**:
  - `governance/AGENT_CONSTITUTION.md` - Role definitions
  - `governance/OMO_INTEGRATION.md` - Integration architecture

  **Acceptance Criteria**:
  - [ ] core/__init__.py exists
  - [ ] Base classes defined
  - [ ] Module can be imported

  **QA Scenarios**:
  ```
  Scenario: Verify module imports
    Tool: Bash
    Steps:
      1. python -c "from core import JCodeError, AgentRole"
    Expected Result: Import succeeds
  ```

  **Commit**: YES (groups with 1, 2)

---

- [ ] 4. Implement core/switch_manager.py

  **What to do**:
  - Implement SwitchManager class
  - Implement 4-level switch hierarchy:
    - Level 1: Global (enabled/disabled)
    - Level 2: Mode (full/light/safe/fast/custom)
    - Level 3: Agent-level (per-agent enablement)
    - Level 4: Rule-level (per-rule configuration)
  - Implement priority resolution (session > project > user > OMO > default)
  - Implement forced enablement scenarios
  - Implement configuration loading from YAML

  **References**:
  - `governance/JCODE_SWITCH.md` - Full switch mechanism design
  - `config/jcode_config.yaml` - Configuration format

  **Acceptance Criteria**:
  - [ ] SwitchManager class implemented
  - [ ] All 4 levels working
  - [ ] Priority resolution correct
  - [ ] Forced enablement scenarios handled
  - [ ] YAML configuration loading

  **QA Scenarios**:
  ```
  Scenario: Verify switch levels
    Tool: Bash
    Steps:
      1. python -c "from core.switch_manager import SwitchManager; sm = SwitchManager(); print(sm.enabled)"
    Expected Result: Switch manager initializes correctly
  ```

  **Commit**: YES

---

- [ ] 5. Implement core/audit_logger.py

  **What to do**:
  - Implement AuditLogger class
  - Implement JSON Lines format logging
  - Implement log fields: log_id, timestamp, actor_type, action_type, context, details, integrity
  - Implement query interfaces: search(), get_task_history(), get_human_interventions()
  - Implement log rotation (size-based and time-based)
  - Implement storage location: .jcode/audit/

  **References**:
  - `governance/AUDIT_LOG_SPEC.md` - Full audit log specification

  **Acceptance Criteria**:
  - [ ] AuditLogger class implemented
  - [ ] JSON Lines format working
  - [ ] All required fields logged
  - [ ] Query interfaces working
  - [ ] Log rotation working

  **Commit**: YES

---

- [ ] 6. Implement core/rule_engine.py

  **What to do**:
  - Implement RuleEngine class
  - Implement YAML rule syntax parsing
  - Implement rule priorities: P0 (terminate), P1 (quick fix), P2 (log only), P3 (soft warning)
  - Implement rule execution timing (IMPLEMENTATION/REVIEW phases)
  - Implement violation handlers: TERMINATE, QUICK_FIX, LOG_ONLY, SOFT_HOOK
  - Implement Soft Hooks mechanism
  - Implement rule registration and execution

  **References**:
  - `governance/RULE_ENGINE.md` - Full rule engine specification
  - `governance/AGENT_CONSTITUTION.md` - Constitutional rules

  **Acceptance Criteria**:
  - [ ] RuleEngine class implemented
  - [ ] YAML parsing working
  - [ ] All priorities working
  - [ ] Violation handlers working
  - [ ] Soft Hooks mechanism

  **Commit**: YES

---

- [ ] 7. Implement core/context_lock.py

  **What to do**:
  - Implement ContextLock class
  - Implement lock operations: acquire, refresh, release, query
  - Implement memory storage structure (.memory/ directory)
  - Implement memory types: project, keyfiles, rules, history
  - Implement retrieval protocol with priority levels
  - Implement MCP tool interface: jcode.lock

  **References**:
  - `governance/CONTEXT_LOCK.md` - Full context lock specification

  **Acceptance Criteria**:
  - [ ] ContextLock class implemented
  - [ ] All lock operations working
  - [ ] Memory storage working
  - [ ] MCP tool interface ready

  **Commit**: YES

---

- [ ] 8. Implement core/incremental_build.py

  **What to do**:
  - Implement IncrementalBuild class
  - Implement diff generation (line/block/file level)
  - Implement unified diff format
  - Implement code merge strategy (human-first principle)
  - Implement dependency impact analysis
  - Implement rollback mechanism (task/file/code_block level)
  - Implement MCP tool interface: incremental_build

  **References**:
  - `governance/INCREMENTAL_BUILD.md` - Full incremental build specification

  **Acceptance Criteria**:
  - [ ] IncrementalBuild class implemented
  - [ ] Diff generation working
  - [ ] Merge strategy working
  - [ ] Rollback mechanism working
  - [ ] MCP tool interface ready

  **Commit**: YES

---

- [ ] 9. Implement core/mcp_client.py

  **What to do**:
  - Implement MCPClient class
  - Implement JSON-RPC 2.0 protocol
  - Implement tool registration
  - Implement tool invocation
  - Implement error handling
  - Implement connection management
  - Register all 10 MCP tools:
    - jcode.analyze, jcode.plan, jcode.implement, jcode.review, jcode.test, jcode.conductor
    - jcode.lock, rule_engine, incremental_build, audit_log

  **References**:
  - `governance/SUPERPOWERS_EXTENSION.md` - MCP tool definitions
  - `governance/OMO_INTEGRATION.md` - Integration architecture

  **Acceptance Criteria**:
  - [ ] MCPClient class implemented
  - [ ] JSON-RPC working
  - [ ] All 10 tools registered
  - [ ] Error handling working

  **Commit**: YES

---

- [ ] 10. Implement core/agent_manager.py

  **What to do**:
  - Implement AgentManager class
  - Implement 6 Agent lifecycle:
    - Analyst (司马迁): analyze()
    - Planner (商鞅): plan()
    - Implementer (鲁班): implement()
    - Reviewer (包拯): review()
    - Tester (张衡): test()
    - Conductor (韩非子): conductor()
  - Implement agent dispatch based on task type
  - Implement iteration counter
  - Implement MAX_ITERATIONS enforcement
  - Implement power flow: ANALYSIS → TASKS → IMPLEMENTATION → REVIEW → TEST → CONDUCTOR

  **References**:
  - `governance/AGENT_CONSTITUTION.md` - Agent definitions
  - `governance/CONDUCTOR.md` - Conductor protocol
  - `agents/*.md` - Individual agent specifications

  **Acceptance Criteria**:
  - [ ] AgentManager class implemented
  - [ ] All 6 agents working
  - [ ] Agent dispatch correct
  - [ ] Iteration enforcement working
  - [ ] Power flow correct

  **Commit**: YES

---

- [ ] 11. Create api/models/ with Pydantic schemas

  **What to do**:
  - Create `api/models/__init__.py`
  - Create `api/models/requests.py` - Request schemas
  - Create `api/models/responses.py` - Response schemas
  - Define schemas for all 10 MCP tools
  - Define error response schemas

  **References**:
  - `governance/SUPERPOWERS_EXTENSION.md` - Tool input/output schemas

  **Acceptance Criteria**:
  - [ ] All model files created
  - [ ] All request/response schemas defined
  - [ ] Pydantic validation working

  **Commit**: YES

---

- [ ] 12. Implement api/routes/ with REST endpoints

  **What to do**:
  - Create `api/routes/__init__.py`
  - Create `api/routes/agents.py` - Agent endpoints
  - Create `api/routes/tools.py` - MCP tool endpoints
  - Create `api/routes/config.py` - Configuration endpoints
  - Implement REST endpoints for all 10 MCP tools
  - Implement configuration management endpoints

  **References**:
  - `governance/OMO_INTEGRATION.md` - API design
  - `governance/SUPERPOWERS_EXTENSION.md` - Tool endpoints

  **Acceptance Criteria**:
  - [ ] All route files created
  - [ ] All endpoints implemented
  - [ ] OpenAPI schema generated

  **Commit**: YES

---

- [ ] 13. Implement api/main.py FastAPI app

  **What to do**:
  - Create `api/main.py` with FastAPI application
  - Configure CORS middleware
  - Include all routers
  - Configure exception handlers
  - Add health check endpoint
  - Add OpenAPI documentation

  **References**:
  - `governance/OMO_INTEGRATION.md` - API architecture

  **Acceptance Criteria**:
  - [ ] FastAPI app created
  - [ ] All routers included
  - [ ] Exception handling working
  - [ ] Health check working
  - [ ] OpenAPI docs generated

  **Commit**: YES

---

- [ ] 14. Implement cli/config.py

  **What to do**:
  - Create `cli/config.py` with configuration management
  - Implement configuration loading from YAML
  - Implement configuration validation
  - Implement configuration update
  - Implement switch configuration helpers

  **References**:
  - `governance/JCODE_SWITCH.md` - Configuration format

  **Acceptance Criteria**:
  - [ ] Config loading working
  - [ ] Validation working
  - [ ] Update working
  - [ ] Switch helpers working

  **Commit**: YES

---

- [ ] 15. Implement cli/commands.py

  **What to do**:
  - Create `cli/commands.py` with Click commands
  - Implement main CLI entry point
  - Implement agent commands: analyze, plan, implement, review, test, conductor
  - Implement config commands: show, set, enable, disable
  - Implement switch commands: mode, agent, rule

  **References**:
  - `governance/JCODE_SWITCH.md` - CLI command format

  **Acceptance Criteria**:
  - [ ] All commands implemented
  - [ ] Agent commands working
  - [ ] Config commands working
  - [ ] Switch commands working

  **Commit**: YES

---

- [ ] 16. Create integration tests

  **What to do**:
  - Create `tests/` directory
  - Create `tests/test_switch_manager.py`
  - Create `tests/test_audit_logger.py`
  - Create `tests/test_rule_engine.py`
  - Create `tests/test_agent_manager.py`
  - Create `tests/test_api.py`

  **References**:
  - All governance documents

  **Acceptance Criteria**:
  - [ ] All test files created
  - [ ] Tests passing

  **Commit**: YES

---

- [ ] 17. Create documentation

  **What to do**:
  - Create `README.md` with project overview
  - Create `docs/installation.md` with installation guide
  - Create `docs/api.md` with API documentation
  - Create `docs/cli.md` with CLI documentation
  - Create `docs/configuration.md` with configuration guide

  **References**:
  - All governance documents

  **Acceptance Criteria**:
  - [ ] All docs created
  - [ ] Documentation accurate

  **Commit**: YES

---

- [ ] 18. Final verification

  **What to do**:
  - Run all tests
  - Verify all imports work
  - Verify API starts
  - Verify CLI works
  - Generate final report

  **References**:
  - All implementation files

  **Acceptance Criteria**:
  - [ ] All tests passing
  - [ ] API functional
  - [ ] CLI functional
  - [ ] No import errors

  **Commit**: NO

---

## Commit Strategy

- **1-3**: `feat: create project structure and core foundation`
- **4-10**: `feat: implement core modules`
- **11-13**: `feat: implement API layer`
- **14-15**: `feat: implement CLI layer`
- **16-17**: `test: add integration tests and documentation`
- **18**: `chore: final verification`

---

## Success Criteria

### Verification Commands
```bash
# Verify project structure
ls -la core/ api/ cli/ config/

# Verify dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start API
uvicorn api.main:app --reload

# Test CLI
python -m cli --help
```

### Final Checklist
- [ ] All core modules implemented
- [ ] All API endpoints functional
- [ ] All CLI commands working
- [ ] Configuration loading correctly
- [ ] All tests passing
- [ ] Documentation complete
