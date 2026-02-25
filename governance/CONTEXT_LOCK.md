# CONTEXT_LOCK — MCP Tool for Context Lock Interface

> Status: **DESIGN SPEC**  
> Scope: Context Lock memory storage, retrieval, and update protocol  
> Purpose: Define JCode integration with OMO Context Lock capability

---

## 0. Integration Context

JCode leverages OMO's Context Lock capability through MCP Tool `jcode.lock`.  
This tool provides **readonly access** to project state, enabling JCode Agents to  
understand the current context without modifying it.

```
┌─────────────────────────────────────────────────────┐
│          OpenCode (OMO) Context Lock                │
│  ┌─────────────────────────────────────────────┐    │
│  │  Memory Storage (.memory/)                  │    │
│  │  - project/                                 │    │
│  │  - keyfiles/                                │    │
│  │  - rules/                                   │    │
│  │  - history/                                 │    │
│  └─────────────────────────────────────────────┘    │
│                   ↕ MCP Tool                       │
│          jcode.lock (readonly access)              │
└─────────────────────────────────────────────────────┘
                    ↕
          ┌──────────────────────┐
          │   JCode Agents       │
          │  - Analyst (司马迁)   │
          │  - Planner (商鞅)     │
          │  - Reviewer (包拯)    │
          └──────────────────────┘
```

---

## 1. Memory Storage Structure

**Storage Location**: `.memory/` (project root)

```
.memory/
├── project/          # Project structure snapshot
│   ├── structure.json      # Directory tree, file counts, dependencies
│   └── manifest.json       # Package files (package.json, requirements.txt...)
├── keyfiles/         # Critical files considered for change detection
│   ├── architecture.md     # Design documents
│   ├── core-modules.json   # Module dependency graph
│   └── api-spec.json       # API definitions
├── rules/            # Active rule sets (from OMO Rule Engine)
│   ├── global.rules.yaml   # Project-wide rules
│   └── context.rules.yaml  # Context-specific rules
└── history/          # Session history for continuity
    ├── sessions.jsonl      # Session metadata
    └── context.log         # Context changes over time
```

---

## 2. Memory Types

### 2.1 Project Structure Memory
**Purpose**: Understand codebase layout and dependencies

**Fields**:
```json
{
  "root": "project root path",
  "directories": {
    "count": 42,
    "paths": ["src/", "tests/", "docs/"]
  },
  "files": {
    "count": 156,
    "by_extension": {".py": 89, ".js": 34, ".md": 23, "...": ...}
  },
  "dependencies": {
    "total": 12,
    "internal": 4,
    "external": 8
  }
}
```

### 2.2 Key Files Memory
**Purpose**: Track critical files that affect system behavior

**Fields**:
```json
{
  "files": [
    {
      "path": "src/auth/jwt.py",
      "role": "core-logic",
      "last_modified": "2026-02-24T10:30:00Z",
      "size_bytes": 2457,
      "imports": ["src/utils/crypto", "src/config.settings"]
    }
  ],
  "critical_patterns": ["**/auth/**", "**/config/**", "**/*migration*"]
}
```

### 2.3 Rule Set Memory
**Purpose**: Retrieve active rules from OMO Rule Engine

**Fields**:
```json
{
  "rules": [
    {
      "id": "R001_no_skip_review",
      "enabled": true,
      "severity": "P0",
      "description": "All implementations must pass Reviewer check",
      "applies_to": ["python", "javascript"]
    }
  ],
  "active_set": "full"  // full | light | safe | fast
}
```

### 2.4 Session History Memory
**Purpose**: Maintain continuity across JCode iterations

**Fields**:
```json
{
  "sessions": [
    {
      "session_id": "omo_session_abc123",
      "task": "Add authentication",
      "start": "2026-02-24T10:00:00Z",
      "end": "2026-02-24T10:30:00Z",
      "iteration": 1,
      "agents_used": ["analyst", "planner", "implementer"],
      "result": "ITERATION"
    }
  ]
}
```

---

## 3. Retrieval Protocol

### 3.1 Priority Levels

| Priority | Trigger | Data Fetched |
|----------|---------|--------------|
| `P0` | New session start | project/ + keyfiles/ + rules/ |
| `P1` | Task validation | session history + current project state |
| `P2` | Incremental updates | Only changed files (diff) |
| `P3` | Quick check | Minimal structure (file counts) |

### 3.2 Trigger Conditions

- **P0**: First `jcode.lock` call in session
- **P1**: After `jcode.analyze` returns VERIFIABLE
- **P2**: Between JCode iterations (same task)
- **P3**: Rule engine validation (no project context needed)

### 3.3 Response Format

```json
{
  "lock_id": "omo_context_lock_xyz789",
  "timestamp": "2026-02-24T10:30:00Z",
  "ttl_seconds": 3600,
  "content": {
    "project": {"files": 156, "directories": 42, ...},
    "keyfiles": [{"path": "src/auth/jwt.py", ...}],
    "rules": [{"id": "R001...", "enabled": true, ...}],
    "history": [{"session_id": "...", ...}]
  },
  "stale_if": "2026-02-24T11:30:00Z"  // Cache expiration
}
```

---

## 4. Update Strategy

**JCode does NOT update Context Lock directly.**  
Lock updates are handled by OMO's built-in incremental build capability.

**JCode can request updates via**:
1. `jcode.implement` → OMO applies changes → OMO updates Context Lock
2. Manual updates via OMO client interface

**JCode must verify**:
```json
{
  "verify_command": "git diff --stat HEAD~1",
  "verify_after": "jcode.conductor decision=DELIVER",
  "verify_on": ["file_creation", "file_modification", "file_deletion"]
}
```

---

## 5. Integration with OpenCode Context Lock

### 5.1 MCP Tool Definition

**Tool Name**: `jcode.lock`  
**Interface**: `jcode_client.call_tool("jcode.lock", {...})`

**Input Schema**:
```json
{
  "lock_id": {
    "type": "string",
    "description": "Context Lock ID from OMO session context"
  },
  "priority": {
    "type": "string",
    "enum": ["P0", "P1", "P2", "P3"],
    "default": "P0"
  },
  "fields": {
    "type": "array",
    "items": {"type": "string", "enum": ["project", "keyfiles", "rules", "history"]},
    "default": ["project", "keyfiles", "rules", "history"]
  }
}
```

**Output Schema**:
```json
{
  "lock_id": "string",
  "timestamp": "string",
  "ttl_seconds": "integer",
  "content": "object (memory content based on fields parameter)",
  "stale_if": "string (ISO 8601 timestamp)"
}
```

### 5.2 Python Integration Example

```python
from opencode import JCodeClient

# Initialize client
client = JCodeClient(context_lock_id="omo_session_abc123")

# P0: Full context on session start
lock_data = client.call_tool(
    "jcode.lock",
    {
        "lock_id": client.context_lock_id,
        "priority": "P0",
        "fields": ["project", "keyfiles", "rules", "history"]
    }
)

print(f"Lock TTL: {lock_data['ttl_seconds']} seconds")
print(f"Project files: {lock_data['content']['project']['files']['count']}")

# P3: Quick structure check
quick_lock = client.call_tool(
    "jcode.lock",
    {
        "lock_id": client.context_lock_id,
        "priority": "P3",
        "fields": ["project"]
    }
)

# Verify file count changed
if quick_lock['content']['project']['files']['count'] != previous_count:
    print("Project structure changed, need full refresh")
```

### 5.3 Agent Integration Points

| Agent | Memory Type | Trigger |
|-------|-------------|---------|
| **Analyst** | project + keyfiles | First call, P0 priority |
| **Planner** | project + rules | After verifiability check |
| **Implementer** | rules only | Rule validation before implementation |
| **Reviewer** | history + rules | Verify no repeated issues |
| **Tester** | keyfiles + history | Identify affected test files |
| **Conductor** | history only | Check iteration count |

---

## 6. Error Handling

| Error | HTTP Status | JCode Response |
|-------|-------------|----------------|
| `LOCK_NOT_FOUND` | 404 | Stop execution, return `verifiability: NON-VERIFIABLE` |
| `LOCK_EXPIRED` | 410 | Refresh lock with P0 priority |
| `LOCK_STALE` | 200 + header | Log warning, proceed with P2 refresh |
| `LOCK_CONFLICT` | 409 | Report to CONDUCTOR for decision |

---

## 7. Performance Guidelines

- **Cache Duration**: `ttl_seconds` from response header
- **Max Response Size**: 1MB (compressed)
- **Timeout**: 5 seconds network + 1 second processing
- **Concurrent Calls**: Maximum 1 lock call per Agent per task

---

## 8. Verification

| Check | Method |
|-------|--------|
| Lock Validity | `stale_if > current_timestamp` |
| Content Completeness | Verify all requested `fields` present |
| Cache HIT | `X-Cache: HIT` header |
| Staleness | `X-Stale: true` header |

---

## 9. Future Extensions

- **Incremental Updates**: Delta-only responses for P2 priority
- **Lock Versioning**: Version number for content change tracking
- **Lock Expansion**: Runtime context expansion via OMO SDK

---

> **JCode: Readonly Context Consumer**  
> **OMO: Logic of Truth, Logic of Action, Logic of Evolution**

---

**END OF CONTEXT_LOCK**
