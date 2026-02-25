# INCREMENTAL_BUILD — MCP Tool for OpenCode Incremental Build Capability

> Status: **DRAFT**  
> Scope: MCP Tool interface for incremental modification workflow  
> Purpose: Enable AI agents to perform file-level edits with human-first merge strategy

---

## 0. Protocol Positioning

This document defines the **Incremental Build MCP Tool** interface for OpenCode Superpowers, enabling AI agents to perform targeted file modifications while preserving human changes and enabling rollback.

### 0.1 Core Principles

> **Human-first, AI-assist. Human changes always take priority over AI changes.**

- **Preserve human changes**: Never overwrite human edits without explicit approval
- **Atomic modifications**: Each task operates on a single logical unit (file/block/statement)
- **rollable changes**: Every modification must support rollback to previous state
- **transparent diff**: All changes must be representable in unified diff format

---

## 1. Incremental Build Workflow

### 1.1 Task-to-Code Flow

```
[TASKS] 
  ↓
[ANALYZE_DEPENDENCIES] (optional, for impact analysis)
  ↓
[GENERATE_DIFF] (MCP Tool: incremental_build/generate_diff)
  ↓
[REVIEW_DIFF] (human or automated)
  ↓
[APPLY_IF_APPROVED] (MCP Tool: incremental_build/apply_patch)
  ↓
[VERIFY] (unit test / lint / integration test)
```

### 1.2 Impact Analysis Flow

```
[FILE_CHANGE_REQUEST]
  ↓
[DEPENDENCY_CHECK]
  ↓
├─→ [NO_DEPENDENCIES] → [SAFE_TO_APPLY]
├─→ [DIRECT_DEPENDENCIES] → [REQUEST_HUMAN_REVIEW]
└─→ [TRANSITIVE_DEPENDENCIES] → [REQUEST_HALTED]
```

---

## 2. Diff Generation Protocol

### 2.1 Granularity Levels

| Level | Scope | Use Case | Example |
|-------|-------|----------|---------|
| **line** | Single line change | Fix typo, add single statement | `def foo():` → `def foo(bar=True):` |
| **block** | Function/class/module | Add method, refactor function | Add `__init__` to class |
| **file** | Entire file | New file, complete rewrite | Create `utils.py` |

### 2.2 Diff Format Specification

**MUST use unified diff format (Git style):**

```
--- a/path/to/file.py
+++ b/path/to/file.py
@@ line_offset line_count @@ section_header
- old_line_content
+ new_line_content
  unchanged_line
```

**Requirements:**
- Always include file path prefix (`a/` for original, `b/` for modified)
- Include line number context (`@@ -old_start old_count +new_start new_count @@`)
- Include section header (function name, class name, etc.)
- Preserve original whitespace and line endings

### 2.3 Diff Generation Request

**MCP Tool:** `incremental_build/generate_diff`

**Request Schema:**
```json
{
  "tool_name": "incremental_build/generate_diff",
  "tool_args": {
    "file_path": "src/utils.py",
    "original_content": "def process(data):\n    return data.strip()",
    "proposed_content": "def process(data):\n    if data is None:\n        return None\n    return data.strip()",
    "granularity": "line|block|file",
    "context_lines": 3
  }
}
```

**Response Schema:**
```json
{
  "success": true,
  "diff": "--- a/src/utils.py\n+++ b/src/utils.py\n@@ -1,2 +1,4 @@\n def process(data):\n+    if data is None:\n+        return None\n-    return data.strip()\n+    return data.strip()",
  "impacts": [
    {
      "type": "function_signature",
      "id": "process",
      "file": "src/utils.py",
      "line": 1
    }
  ],
  "roll_forward_ready": true
}
```

---

## 3. Code Merge Strategy

### 3.1 Human-First Principle

> **If a human has modified the same file since the last AI operation, HUMAN CHANGES PREVAIL.**

### 3.2 Merge Triage Flow

```
[APPLY_REQUEST]
  ↓
[CHECK_HUMAN_CHANGES]
  ↓
├─→ [NO_HUMAN_CHANGES] → [AUTO_MERGE]
├─→ [HUMAN_CHANGES_DIFF_CELL] → [REQUEST_HUMAN_REVIEW]
└─→ [HUMAN_CHANGES_DIFF_FILE] → [REQUEST_HUMAN_REVIEW_WITH_DIFF]
```

### 3.3Merge Conflict Resolution Matrix

| Scenario | Resolution |
|----------|------------|
| Different files | Auto-merge |
| Same file, different lines | Auto-merge |
| Same file, adjacent lines | Auto-merge (if context matches) |
| Same file, overlapping lines | HUMAN_REVIEW_REQUIRED |
| Human deleted AI-added code | PRESERVE_HUMAN (skip AI change) |

### 3.4 Merge Request Format

**MCP Tool:** `incremental_build/apply_patch`

**Request Schema:**
```json
{
  "tool_name": "incremental_build/apply_patch",
  "tool_args": {
    "file_path": "src/utils.py",
    "diff": "--- a/src/utils.py\n+++ b/src/utils.py\n@@ -1,2 +1,4 @@\n def process(data):\n+    if data is None:\n+        return None\n-    return data.strip()\n+    return data.strip()",
    "merge_strategy": "auto|human_review|preserve_human",
    "human_changes_detected": true,
    "human_diff": "..."
  }
}
```

**Response Schema:**
```json
{
  "success": true,
  "merged_content": "def process(data):\n    if data is None:\n        return None\n    return data.strip()",
  "merge_log": {
    "ai_changes_applied": 2,
    "human_changes_preserved": true,
    "conflicts_resolved": "auto|hUMAN",
    "timestamp": "2026-02-24T10:30:00Z"
  }
}
```

---

## 4. Dependency Impact Analysis

### 4.1 Analysis Levels

| Level | Scope | Detection Method |
|-------|-------|-----------------|
| **direct** | Imports/exports in same module | AST parsing |
| **module** | Cross-file references | Symbol table |
| **test** | Test dependencies | Test discovery |
| **runtime** | Dynamic imports/reflection | Static analysis + annotation |

### 4.2 Impact Analysis Request

**MCP Tool:** `incremental_build/analyze_impacts`

**Request Schema:**
```json
{
  "tool_name": "incremental_build/analyze_impacts",
  "tool_args": {
    "file_path": "src/utils.py",
    "diff": "...",
    "analysis_depth": "direct|module|test|runtime"
  }
}
```

**Response Schema:**
```json
{
  "analysis": {
    "direct": {
      "affected": ["src/handlers.py"],
      "severity": "high",
      "notes": "Direct import: from utils import process"
    },
    "test": {
      "affected": ["tests/test_utils.py"],
      "severity": "medium",
      "notes": "Test function uses process()"
    }
  },
  "recommendation": "APPROVE|REVIEW_REQUIRED|BLOCKED",
  "blocking_issues": []
}
```

---

## 5. Rollback Mechanism

### 5.1 Rollback Levels

| Level | Scope | rollback_token required |
|-------|-------|------------------------|
| **task** | All files modified by current task |可以从TASKS元数据推导 |
| **file** | Single file to previous version | diff_id from GENERATE_DIFF |
| **code_block** | Specific function/class | function_name + file_path |

### 5.2 Rollback Token Format

Each `generate_diff` response includes a rollback token:

```json
{
  "diff_id": "DIFF-{task_id}-{file_hash}-{timestamp}",
  "version_timestamp": "2026-02-24T10:30:00Z",
  "original_hash": "sha256:abc123..."
}
```

### 5.3 Rollback Request

**MCP Tool:** `incremental_build/rollback`

**Request Schema:**
```json
{
  "tool_name": "incremental_build/rollback",
  "tool_args": {
    "rollback_target": {
      "type": "task|file|code_block",
      "id": "TASK-123"|"DIFF-123-abc..."|"src/utils.py:process"
    },
    "execute": true
  }
}
```

**Response Schema:**
```json
{
  "success": true,
  "rolled_back_to": {
    "version": "DIFF-123-abc...",
    "timestamp": "2026-02-24T10:25:00Z"
  },
  "files_affected": ["src/utils.py"],
  "execution_log": {
    "rollback_type": "task|file|code_block",
    "applied": true,
    "verification_passed": true
  }
}
```

---

## 6. OpenCode Integration

### 6.1 MCP Tool Registration

**Tool Definition (JSON Schema):**
```json
{
  "name": "incremental_build/generate_diff",
  "description": "Generate unified diff for proposed file changes",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {"type": "string"},
      "original_content": {"type": "string"},
      "proposed_content": {"type": "string"},
      "granularity": {"type": "string", "enum": ["line", "block", "file"]},
      "context_lines": {"type": "integer", "minimum": 0, "maximum": 10}
    },
    "required": ["file_path", "original_content", "proposed_content"]
  }
}
```

**Available Tools:**
1. `incremental_build/generate_diff` - Generate diff from content pair
2. `incremental_build/apply_patch` - Apply diff with merge strategy
3. `incremental_build/analyze_impacts` - Analyze dependency impacts
4. `incremental_build/rollback` - Rollback to previous version

### 6.2 Integration Flow

```
[OpenCode Host]
    ↓
[MCP Client (JCode)]
    ↓
[MCP Server (Incremental Build Service)]
    ↓
├─→ File System (read/write)
├─→ Git Repository (diff storage)
├─→ Dependency Graph (analysis)
└─→ Audit Log (traceability)
```

---

## 7. Python Integration Example

### 7.1 Client-Side Integration

```python
from pathlib import Path
from jcode.incremental_build import IncrementalBuildClient

class MyAgent:
    def __init__(self):
        self.ib = IncrementalBuildClient(
            server_url="http://localhost:3001",
            api_key="..."
        )
    
    def modify_file(self, file_path: str, modify_func):
        """Modify file with incremental build protocol."""
        # 1. Read current content
        original = Path(file_path).read_text()
        
        # 2. Apply local modification
        proposed = modify_func(original)
        
        # 3. Generate diff
        diff_result = self.ib.generate_diff(
            file_path=file_path,
            original_content=original,
            proposed_content=proposed,
            granularity="line"
        )
        
        # 4. Analyze impacts
        impact_result = self.ib.analyze_impacts(
            file_path=file_path,
            diff=diff_result["diff"],
            analysis_depth="module"
        )
        
        # 5. Apply if no blocking issues
        if impact_result["recommendation"] == "BLOCKED":
            raise RuntimeError(f"Blocking issues: {impact_result['blocking_issues']}")
        
        merge_result = self.ib.apply_patch(
            file_path=file_path,
            diff=diff_result["diff"],
            merge_strategy="auto"
        )
        
        return merge_result
```

### 7.2 Server-Side Implementation (Skeleton)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import difflib
import hashlib
import json

app = FastAPI()

class DiffRequest(BaseModel):
    file_path: str
    original_content: str
    proposed_content: str
    granularity: Optional[str] = "line"
    context_lines: Optional[int] = 3

class MergeRequest(BaseModel):
    file_path: str
    diff: str
    merge_strategy: Optional[str] = "auto"
    human_changes_detected: Optional[bool] = False

@app.post("/incremental_build/generate_diff")
async def generate_diff(req: DiffRequest):
    """Generate unified diff."""
    # Generate unified diff
    original_lines = req.original_content.splitlines(keepends=True)
    proposed_lines = req.proposed_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        proposed_lines,
        fromfile=f"a/{req.file_path}",
        tofile=f"b/{req.file_path}",
        lineterm=""
    )
    
    diff_str = "".join(diff)
    
    # Generate rollback token
    token = generate_diff_token(req.file_path, req.original_content)
    
    return {
        "success": True,
        "diff": diff_str,
        "diff_id": token,
        "impacts": analyze_impacts_sync(req.file_path, diff_str),
        "roll_forward_ready": True
    }

@app.post("/incremental_build/apply_patch")
async def apply_patch(req: MergeRequest):
    """Apply patch with merge strategy."""
    # Parse diff
    patch_lines = req.diff.splitlines()
    
    # Apply merge strategy
    if req.merge_strategy == "human_review" and req.human_changes_detected:
        return {
            "success": False,
            "error": "HUMAN_CHANGES_DETECTED",
            "merge_log": {
                "conflict": True,
                "resolution_required": "human"
            }
        }
    
    # Apply patch (simplified)
    merged = apply_unified_diff(req.file_path, req.diff)
    
    return {
        "success": True,
        "merged_content": merged,
        "merge_log": {
            "ai_changes_applied": count_changes(req.diff),
            "human_changes_preserved": not req.human_changes_detected,
            "conflicts_resolved": "auto",
            "timestamp": get_current_timestamp()
        }
    }

def generate_diff_token(file_path: str, content: str) -> str:
    """Generate unique diff token for rollback."""
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
    return f"DIFF-{get_task_id()}-{content_hash}-{get_timestamp()}"
```

---

## 8. Configuration

### 8.1 MCP Server Configuration

```yaml
# .opencode/mcp-config.yaml
servers:
  incremental_build:
    command: python
    args: ["-m", "jcode.incremental_build.server"]
    env:
      - JCODE_DATA_DIR=.jcode/data
      - JCODE_AUDIT_DIR=.jcode/audit
    timeout: 30  # seconds
    capabilities:
      diff_generation: true
      merge_strategy: true
      impact_analysis: true
      rollback: true
```

### 8.2 Agent Integration Settings

```yaml
# .jcode/config.yaml
incremental_build:
  default_granularity: "line"
  default_context_lines: 3
  merge_strategy: "human_first"
  rollback_enabled: true
  impact_analysis:
    depth: "module"
    auto_requests: ["BLOCKED"]
  logging:
    diff_storage: true
    audit_trail: true
```

---

## 9. Audit and Traceability

### 9.1 Diff Storage

**Storage Location:** `.jcode/data/diffs/`

**Format:** `DIFF-{task_id}-{file_hash}.unidiff`

### 9.2 Audit Log Entry

```json
{
  "log_id": "AUDIT-Idx-001",
  "timestamp": "2026-02-24T10:30:00Z",
  "actor_type": "agent", 
  "action_type": "incremental_build",
  "context": {
    "task_id": "TASK-123",
    "file_path": "src/utils.py",
    "diff_id": "DIFF-TASK-123-abc123..."
  },
  "details": {
    "action": "generate_diff|apply_patch|rollback",
    "granularity": "line",
    "lines_changed": 4
  },
  "integrity": {
    "diff_hash": "sha256:...",
    "file_hash_before": "sha256:...",
    "file_hash_after": "sha256:..."
  }
}
```

---

## 10. Validation Checklist

### 10.1 Diff Format Validation

- [ ] Uses `a/` and `b/` prefixes
- [ ] Includes `@@ -old_start count +new_start count @@` header
- [ ] Preserves original whitespace
- [ ] No trailing newline in file content

### 10.2 Merge Strategy Validation

- [ ] Human changes detected before applying
- [ ] Conflict resolution follows human-first原则
- [ ] Merge log includes timestamp and resolver

### 10.3 Rollback Validation

- [ ] Rollback token is unique and traceable
- [ ] Rollback operation is idempotent
- [ ] Verification test runs after rollback

---

## 11. Examples and Recipes

### 11.1 Add Function with Proper Diff

```python
# Original
def validate(data):
    return len(data) > 0

# Proposed
def validate(data):
    if data is None:
        return False
    return len(data) > 0

# Expected diff
"""
--- a/src/validator.py
+++ b/src/validator.py
@@ -1,2 +1,4 @@
-def validate(data):
-    return len(data) > 0
+def validate(data):
+    if data is None:
+        return False
+    return len(data) > 0
"""
```

### 11.2 Safe Rollback Sequence

```python
# 1. Generate diff with token
result = ib.generate_diff(...)
diff_id = result["diff_id"]

# 2. Apply patch
ib.apply_patch(diff=result["diff"])

# 3. If something goes wrong, rollback
ib.rollback(rollback_target={"type": "diff", "id": diff_id})
```

---

## 12. Anti-Patterns

### 12.1 Forbidden Operations

- ❌ **Full file rewrite** → Use block-level modifications
- ❌ **Overwrite human changes without review** → HUMAN_FIRST
- ❌ **Diff without rollback token** → UNTRACEABLE
- ❌ **Apply diff to different file than generated** → MISMATCH

### 12.2 Violation Detection

```python
def detect_violations(diff: str, file_path: str) -> list:
    """Detect potential violations in diff."""
    violations = []
    
    # Check for full file rewrite (line count change > 80%)
    lines = diff.splitlines()
    added = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
    total = added + removed
    
    if total > 0 and (added/total > 0.8 or removed/total > 0.8):
        violations.append("FULL_FILE_REWRITE_DETECTED")
    
    # Check for missing rollback token
    if "DIFF-" not in diff:
        violations.append("MISSING_ROLLBACK_TOKEN")
    
    return violations
```

---

## 13. Version History

| Version | Date | Changes |
|---------|------|---------|
| DRAFT | 2026-02-24 | Initial draft |

---

## 14. References

- **Git Diff Format:** https://www.gnu.org/software/diffutils/manual/html_node/Detailed-Unified.html
- **MCP Specification:** https://modelcontextprotocol.io/
- **Unified Diff Standard:** https://tools.ietf.org/html/draft-ribose-diff-unified-00
- **OpenCode Superpowers:** Internal documentation

---

> **END OF INCREMENTAL_BUILD**
> 
> Status: DRAFT
> Next: Submit to JCode governance review
