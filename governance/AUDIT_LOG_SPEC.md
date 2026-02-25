# AUDIT_LOG_SPEC — Unified Audit Log Specification

**Status:** PROPOSED
**Scope:** JCode Agent System v3.0 + OpenCode Superpowers Integration
**Purpose:** Define unified audit log format for seamless integration with OpenCode ecosystem

---

## 0. Specification Overview

### 0.1 Design Goals

This specification defines a **unified audit log format** that serves both:
1. **JCode Agent System** - Agent execution, human interventions, quick fixes, state transitions
2. **OpenCode Superpowers** - Tool calls, MCP server interactions, session management

**Core Principles:**
- **Immutability**: Append-only, never modify or delete
- **Interoperability**: Compatible with OpenCode audit log standards
- **Queryability**: Rich search and filtering capabilities
- **Integrity**: Tamper-evident with hash-based verification

### 0.2 Architecture Alignment

```
.jcode/                            # JCode-specific logs
├── audit/
│   ├── agent_executions.jsonl     # Agent activities
│   ├── human_interventions.jsonl  # Human operations (from HUMAN_INTERFACE.md)
│   ├── quick_fixes.jsonl          # Quick fix operations (from QUICK_FIX_CHANNEL.md)
│   └── edge_cases.jsonl           # State transitions (from EDGE_CASES.md)

.omo/                              # OpenCode Superpowers logs
├── audit/
│   ├── mcp_calls.jsonl            # MCP server interactions
│   ├── tool_invocations.jsonl    # Tool call records
│   └── sessions.jsonl             # Session lifecycle

.unified/                          # Unified storage (symlinked or aggregated)
└── audit.jsonl                    # Consolidated log stream (optional)
```

---

## 1. Unified Log Format

### 1.1 Base Log Entry Structure

All log entries MUST follow this base schema:

```json
{
  "log_id": "JCODE-{timestamp}-{seq}",
  "timestamp": "2026-02-24T10:30:00.123456Z",
  "actor_type": "AGENT | HUMAN | SYSTEM | MCP_SERVER",
  "actor_id": "analyst | human_admin | conductor | server_name",
  "action_type": "ANALYSIS_START | HUMAN_INTERVENTION | TOOL_CALL | STATE_TRANSITION",
  "context": {
    "task_id": "optional_task_id",
    "iteration": 2,
    "stage": "ANALYSIS | TASKS | IMPLEMENTATION | REVIEW | TEST",
    "session_id": "optional_session_id"
  },
  "details": {
    "specific_fields": "vary by action_type"
  },
  "integrity": {
    "content_hash": "sha256_hash_of_details_field",
    "signature": "optional_signature_for_human_operations"
  },
  "metadata": {
    "source_system": "JCODE | OMO",
    "log_version": "1.0",
    "correlation_id": "optional_correlation_with_omo_logs"
  }
}
```

### 1.2 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `log_id` | string | Yes | Unique identifier: `{SYSTEM}-{timestamp}-{seq}` |
| `timestamp` | string (ISO8601) | Yes | Microsecond precision UTC timestamp |
| `actor_type` | enum | Yes | AGENT, HUMAN, SYSTEM, MCP_SERVER |
| `actor_id` | string | Yes | Specific actor identifier |
| `action_type` | string | Yes | Action classification (see §1.3) |
| `context` | object | No | Shared contextual information |
| `details` | object | Yes | Action-specific payload (see §1.4) |
| `integrity` | object | Yes | Tamper-evidence fields |
| `metadata` | object | Yes | System and integration metadata |

### 1.3 Action Type Taxonomy

#### JCode-Specific Actions
- `ANALYSIS_START`, `ANALYSIS_COMPLETE`, `ANALYSIS_NON_VERIFIABLE`
- `TASKS_DEFINED`, `TASKS_REDEFINED`
- `IMPLEMENTATION_START`, `IMPLEMENTATION_COMPLETE`
- `REVIEW_APPROVED`, `REJECTED_MAJOR`, `REJECTED_MINOR`
- `TEST_PASSED`, `TEST_FAILED`, `TEST_QUICK_FIXABLE`
- `CONDUCTOR_STOP`, `CONDUCTOR_CONTINUE`

#### Human Intervention Actions (HUMAN_INTERFACE.md)
- `HUMAN_INTERVENTION_DOWNGRADE_VERIFIABILITY`
- `HUMAN_INTERVENTION_EXTEND_ITERATIONS`
- `HUMAN_INTERVENTION_CONFIRM_STOP`
- `HUMAN_INTERVENTION_OVERRIDE_REVIEW`

#### Quick Fix Actions (QUICK_FIX_CHANNEL.md)
- `QUICK_FIX_REQUEST`
- `QUICK_FIX_EXECUTE`
- `QUICK_FIX_COMPLETE`
- `QUICK_FIX_VERIFY`

#### Edge Case Actions (EDGE_CASES.md)
- `STATE_TRANSITION_E001_ARCHITECT_ONLY`
- `STATE_TRANSITION_E002_FAST_CODER_OVERFLOW`
- `STATE_TRANSITION_E003_ITERATION_OVERFLOW`
- `STATE_TRANSITION_E004_NON_VERIFIABLE`
- `STATE_TRANSITION_E005_STRUCTURAL_VIOLATION`
- `STATE_TRANSITION_E006_EVIDENCE_UNAVAILABLE`

#### OpenCode Superpowers Actions
- `MCP_SERVER_CALL`
- `MCP_SERVER_RESPONSE`
- `TOOL_INVOCATION`
- `TOOL_RESULT`
- `SESSION_START`
- `SESSION_END`

### 1.4 Details Schema by Action Type

#### Agent Execution (e.g., ANALYSIS_COMPLETE)
```json
{
  "details": {
    "output": "[ANALYSIS] ...",
    "verifiability": "HARD | SOFT | NON",
    "risk_level": "LOW | MEDIUM | HIGH",
    "estimation": {
      "complexity": 3,
      "effort": "medium",
      "confidence": 0.85
    }
  }
}
```

#### Human Intervention
```json
{
  "details": {
    "operator_role": "HUMAN_ADMIN | HUMAN_REVIEWER | HUMAN_OBSERVER",
    "trigger_condition": "NON-VERIFIABLE | ITERATION_OVERFLOW | STRUCTURAL_VIOLATION",
    "action_taken": "DOWNGRADE_VERIFIABILITY | EXTEND_ITERATIONS",
    "affected_section": "ANALYSIS | TASKS | IMPLEMENTATION",
    "reason": "Business emergency, cannot obtain full test environment",
    "outcome": "TASK_CONTINUE | TASK_STOP | TASK_RERUN",
    "admin_code_hash": "sha256_hash_of_admin_code_if_used"
  }
}
```

#### Quick Fix
```json
{
  "details": {
    "fix_id": "QF-{timestamp}-{seq}",
    "type": "TYPE-A | TYPE-B | TYPE-C | TYPE-D",
    "trigger": "REVIEW_REJECTED | TEST_FAILED | POST_DELIVERY",
    "location": "src/utils.py:42",
    "change": "Variable name typo correction",
    "iteration_before": 2,
    "iteration_after": 2,
    "verification_method": "diff_check | unit_test | manual_review"
  }
}
```

#### Edge Case State Transition
```json
{
  "details": {
    "scenario_id": "E001 | E002 | E003 | E004 | E005 | E006",
    "state_from": "E001_PENDING",
    "state_to": "ACCEPT_WITHOUT_EVIDENCE",
    "trigger": "Human decision received",
    "decision_path": "A | B | C",
    "final_state": "DELIVERED | STOPPED | BLOCKED"
  }
}
```

#### MCP Server Call
```json
{
  "details": {
    "server_name": "filesystem",
    "method_name": "read_file",
    "parameters": {
      "path": "/path/to/file"
    },
    "call_id": "mcp_call_{uuid}",
    "request_size": 256
  }
}
```

#### Tool Invocation
```json
{
  "details": {
    "tool_name": "bash",
    "arguments": {
      "command": "git status"
    },
    "tool_id": "tool_{uuid}",
    "background": false
  }
}
```

---

## 2. Storage Architecture

### 2.1 Storage Locations

```
.jcode/audit/
├── agent_executions.jsonl          # All agent activities
├── human_interventions.jsonl       # Human operations (HUMAN_INTERFACE.md §4.2)
├── quick_fixes.jsonl               # Quick fix logs (QUICK_FIX_CHANNEL.md §8.1)
├── edge_cases.jsonl                # State transitions
└── index.json                      # Log index for fast lookup

.omo/audit/
├── mcp_calls.jsonl                 # MCP server interactions
├── tool_invocations.jsonl          # Tool call records
├── sessions.jsonl                  # Session lifecycle
└── index.json                      # OpenCode log index
```

**Storage Format:** JSON Lines (JSONL)
- One valid JSON object per line
- Append-only write pattern
- Line-based atomic writes

### 2.2 Index Structure

```json
{
  "version": "1.0",
  "last_log_id": "JCODE-20260224T103000000-12345",
  "last_timestamp": "2026-02-24T10:30:00.123456Z",
  "file_offsets": {
    "agent_executions.jsonl": {
      "line_count": 1024,
      "size_bytes": 512000,
      "earliest_timestamp": "2026-02-24T08:00:00Z",
      "latest_timestamp": "2026-02-24T10:30:00Z"
    }
  },
  "action_type_index": {
    "HUMAN_INTERVENTION": ["line:100-120", "line:250-255"],
    "QUICK_FIX": ["line:300-340"]
  },
  "task_index": {
    "task_001": ["line:10-50", "line:100-120", "line:200-250"]
  }
}
```

### 2.3 Log Rotation Strategy

**Rotation Triggers:**
1. **Size-based**: 100 MB per file
2. **Time-based**: Daily rotation at 00:00 UTC
3. **Count-based**: Maximum 10 rotated files per log type

**Rotation Naming:**
```
agent_executions.jsonl              # Current (active)
agent_executions.20260224.jsonl     # Rotated (YYYYMMDD)
agent_executions.20260223.jsonl     # Rotated
...
agent_executions.20260215.jsonl     # Oldest (10 days retention)
```

**Retention Policy:**
- Hot storage (SSD): 7 days
- Warm storage (compressed): 90 days
- Cold storage (archive): 365 days
- Archive format: `.gz` with index preserved

**Compression:**
```bash
# Rotate and compress
gzip -c agent_executions.20260224.jsonl > agent_executions.20260224.jsonl.gz
```

---

## 3. Query Interfaces

### 3.1 Core Query Functions

```python
# audit_log_interface.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

class AuditLogQuery:
    """Unified audit log query interface for JCode and OpenCode"""

    def __init__(self, audit_dir: Path):
        self.audit_dir = audit_dir

    def search(
        self,
        action_type: Optional[List[str]] = None,
        actor_type: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Generic search across all audit logs

        Args:
            action_type: Filter by action type (e.g., ['HUMAN_INTERVENTION', 'QUICK_FIX'])
            actor_type: Filter by actor type (e.g., ['HUMAN', 'AGENT'])
            start_time: Start timestamp (inclusive)
            end_time: End timestamp (exclusive)
            task_id: Filter by task_id
            session_id: Filter by session_id (OpenCode integration)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of matching log entries
        """
        pass

    def get_task_history(
        self,
        task_id: str,
        include_details: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get complete audit trail for a specific task

        Returns chronologically ordered log entries for the task
        """
        pass

    def get_human_interventions(
        self,
        operator_role: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        reason_contains: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query human intervention logs (HUMAN_INTERFACE.md)

        Args:
            operator_role: Filter by operator role (e.g., 'HUMAN_ADMIN')
            reason_contains: Text search in reason field
        """
        pass

    def get_quick_fixes(
        self,
        fix_type: Optional[str] = None,
        trigger: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query quick fix logs (QUICK_FIX_CHANNEL.md)

        Args:
            fix_type: Filter by TYPE-A, TYPE-B, TYPE-C, TYPE-D
            trigger: Filter by trigger condition
            file_path: Filter by affected file
        """
        pass

    def get_edge_case_transitions(
        self,
        scenario_id: Optional[str] = None,
        state_from: Optional[str] = None,
        state_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query edge case state transitions (EDGE_CASES.md)

        Args:
            scenario_id: Filter by scenario (E001-E006)
            state_from: Filter by source state
            state_to: Filter by destination state
        """
        pass

    def get_mcp_calls(
        self,
        server_name: Optional[str] = None,
        method_name: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query MCP server calls (OpenCode integration)

        Args:
            server_name: Filter by MCP server name
            method_name: Filter by method name
            session_id: Filter by session ID
        """
        pass

    def get_session_timeline(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get complete timeline for a session (agent + tool + MCP calls)

        Useful for OpenCode session audit
        """
        pass
```

### 3.2 Query Examples

#### Example 1: Find all human interventions by admin
```python
query = AuditLogQuery(Path(".jcode/audit"))

# Get all HUMAN_ADMIN interventions in last 24 hours
from datetime import datetime, timedelta

end_time = datetime.now(datetime.UTC)
start_time = end_time - timedelta(hours=24)

interventions = query.get_human_interventions(
    operator_role="HUMAN_ADMIN",
    start_time=start_time,
    end_time=end_time
)

for intervention in interventions:
    print(f"[{intervention['timestamp']}] {intervention['action_type']}")
    print(f"  Reason: {intervention['details']['reason']}")
    print(f"  Outcome: {intervention['details']['outcome']}")
```

#### Example 2: Get complete task history
```python
# Get full audit trail for task 'task_001'
history = query.get_task_history("task_001")

for entry in history:
    print(f"{entry['timestamp']} | {entry['actor_type']:12} | {entry['action_type']}")
```

**Output:**
```
2026-02-24T09:00:00Z | AGENT       | ANALYSIS_START
2026-02-24T09:05:30Z | AGENT       | ANALYSIS_COMPLETE
2026-02-24T09:06:00Z | AGENT       | TASKS_DEFINED
2026-02-24T09:10:00Z | AGENT       | IMPLEMENTATION_START
2026-02-24T09:30:00Z | AGENT       | IMPLEMENTATION_COMPLETE
2026-02-24T09:35:00Z | AGENT       | REVIEW_REJECTED_MAJOR
2026-02-24T09:40:00Z | HUMAN       | HUMAN_INTERVENTION_EXTEND_ITERATIONS
2026-02-24T09:45:00Z | AGENT       | TASKS_REDEFINED
2026-02-24T09:50:00Z | AGENT       | IMPLEMENTATION_COMPLETE
2026-02-24T09:55:00Z | AGENT       | REVIEW_APPROVED
2026-02-24T10:00:00Z | AGENT       | TEST_PASSED
2026-02-24T10:05:00Z | SYSTEM      | CONDUCTOR_CONTINUE
```

#### Example 3: Find quick fixes in a file
```python
# Find all quick fixes affecting src/utils.py
quick_fixes = query.get_quick_fixes(
    file_path="src/utils.py"
)

for fix in quick_fixes:
    print(f"{fix['details']['fix_id']}: {fix['details']['location']}")
    print(f"  Type: {fix['details']['type']}")
    print(f"  Change: {fix['details']['change']}")
```

#### Example 4: Query edge case transitions
```python
# Find all iteration overflow scenarios (E003)
overflows = query.get_edge_case_transitions(
    scenario_id="E003"
)

for entry in overflows:
    print(f"{entry['timestamp']}: {entry['details']['state_from']} → {entry['details']['state_to']}")
    print(f"  Decision path: {entry['details']['decision_path']}")
```

#### Example 5: Unified session audit (OpenCode integration)
```python
# Get complete session timeline including agent, tools, and MCP calls
timeline = query.get_session_timeline("session_abc123")

# Group by type for summary
from collections import Counter

counts = Counter(entry['actor_type'] for entry in timeline)
print("Session breakdown:")
    print(f"  {actor}: {count}")

# Correlate agent actions with tool calls
agent_actions = [e for e in timeline if e['actor_type'] == 'AGENT']
tool_calls = [e for e in timeline if e['actor_type'] == 'SYSTEM' and 'tool' in e['action_type']]

print(f"\nAgent actions: {len(agent_actions)}")
print(f"Tool invocations: {len(tool_calls)}")
```

---

## 4. Integration with OpenCode Audit Log

### 4.1 OpenCode Audit Log Compatibility

OpenCode Superpowers uses MCP (Model Context Protocol) for tool invocation logging. The JCode audit log format extends the MCP log structure:

**MCP Standard Log Entry:**
```json
{
  "timestamp": "2026-02-24T10:30:00.123456Z",
  "level": "info",
  "message": "Tool call executed",
  "method": "read_file",
  "server": "filesystem",
  "session_id": "ses_abc123"
}
```

**JCode Extended Format (MCP Integration):**
```json
{
  "log_id": "JCODE-20260224T103000123-001",
  "timestamp": "2026-02-24T10:30:00.123456Z",
  "actor_type": "MCP_SERVER",
  "actor_id": "filesystem",
  "action_type": "MCP_SERVER_CALL",
  "context": {
    "session_id": "ses_abc123",
    "mcp_call_id": "call_xyz789"
  },
  "details": {
    "method_name": "read_file",
    "parameters": {
      "path": "/path/to/file"
    }
  },
  "integrity": {
    "content_hash": "abc123..."
  },
  "metadata": {
    "source_system": "OMO",
    "log_version": "1.0",
    "correlation_id": "JCODE-task_001"
  }
}
```

### 4.2 Correlation ID Mapping

JCode logs can be correlated with OpenCode logs using:

1. **task_id ↔ session_id**: When JCode task uses OpenCode tools
2. **correlation_id**: Explicit cross-system correlation in metadata
3. **timestamp-based**: Temporal correlation within same time window

```python
# Find OpenCode tool calls for a JCode task
task_history = query.get_task_history("task_001")
task_start = min(entry['timestamp'] for entry in task_history)
task_end = max(entry['timestamp'] for entry in task_history)

# Query OpenCode logs in same time window
omo_calls = query.get_mcp_calls(
    start_time=task_start,
    end_time=task_end
)

print(f"Task involved {len(omo_calls)} MCP server calls")
```

### 4.3 Unified Audit View

For comprehensive audit reporting, combine JCode and OpenCode logs:

```python
def generate_unified_audit_report(task_id: str) -> Dict:
    """Generate unified audit report combining JCode and OpenCode logs"""

    # Get JCode logs
    jcode_logs = query.get_task_history(task_id)

    # Determine time window
    start_time = min(entry['timestamp'] for entry in jcode_logs)
    end_time = max(entry['timestamp'] for entry in jcode_logs)

    # Get OpenCode logs in same window
    omo_logs = query.search(
        start_time=start_time,
        end_time=end_time,
        actor_type=['MCP_SERVER', 'SYSTEM']
    )

    # Merge and sort
    unified = sorted(
        jcode_logs + omo_logs,
        key=lambda x: x['timestamp']
    )

    # Generate statistics
    stats = {
        'total_entries': len(unified),
        'by_actor': Counter(e['actor_type'] for e in unified),
        'by_action': Counter(e['action_type'] for e in unified),
        'human_interventions': len([e for e in unified if e['actor_type'] == 'HUMAN']),
        'quick_fixes': len([e for e in unified if 'QUICK_FIX' in e['action_type']]),
        'mcp_calls': len([e for e in unified if e['actor_type'] == 'MCP_SERVER'])
    }

    return {
        'task_id': task_id,
        'time_range': (start_time, end_time),
        'timeline': unified,
        'statistics': stats
    }
```

---

## 5. Integrity and Verification

### 5.1 Content Hash Calculation

```python
import hashlib
import json

def calculate_details_hash(details: Dict) -> str:
    """Calculate SHA-256 hash of details field for integrity verification"""

    # Canonicalize JSON: sorted keys, no extra whitespace
    details_json = json.dumps(details, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(details_json.encode()).hexdigest()
```

### 5.2 Log Entry Verification

```python
def verify_log_integrity(entry: Dict) -> bool:
    """Verify log entry integrity by checking hash"""

    calculated_hash = calculate_details_hash(entry['details'])
    stored_hash = entry['integrity']['content_hash']

    return calculated_hash == stored_hash
```

### 5.3 Tamper Detection

```python
def detect_tampering(log_file: Path) -> List[int]:
    """Detect tampered log entries (returns line numbers of suspicious entries)"""

    suspicious = []

    with open(log_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            entry = json.loads(line)

            if not verify_log_integrity(entry):
                suspicious.append(line_num)

    return suspicious
```

### 5.4 Chain Hashing (Advanced)

For additional security, each log entry can include hash of previous entry:

```json
{
  "integrity": {
    "content_hash": "sha256_of_current_details",
    "prev_entry_hash": "sha256_of_previous_full_entry",
    "chain_valid": true
  }
}
```

This creates a verifiable blockchain-like structure preventing deletion or reordering.

---

## 6. Performance Considerations

### 6.1 Index Updates

Index should be updated after each log write:

```python
def update_index(log_file: Path, new_entry: Dict):
    """Update index atomically with new log entry"""

    index_file = log_file.parent / "index.json"

    with open(index_file, 'r') as f:
        index = json.load(f)

    # Update offsets
    file_offsets = index['file_offsets'].setdefault(log_file.name, {})
    file_offsets['line_count'] = file_offsets.get('line_count', 0) + 1
    file_offsets['latest_timestamp'] = new_entry['timestamp']

    # Update action type index
    action_idx = index['action_type_index'].setdefault(new_entry['action_type'], [])
    action_idx.append(f"line:{file_offsets['line_count']}")

    # Atomic write
    temp_index = index_file.with_suffix('.tmp')
    with open(temp_index, 'w') as f:
        json.dump(index, f, indent=2)
    temp_index.replace(index_file)
```

### 6.2 Query Optimization

For large log files, use memory-mapped files and line offsets:

```python
import mmap

def fast_line_read(log_file: Path, line_num: int) -> Dict:
    """Read specific line by number using line offset index"""

    with open(log_file, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), 0)

        # Find line position (simplified - use index in production)
        position = mm.find(b'\n', 0, None)  # First newline
        for _ in range(line_num - 1):
            position = mm.find(b'\n', position + 1)

        start = position + 1
        end = mm.find(b'\n', start)

        line = mm[start:end].decode('utf-8')
        mm.close()

        return json.loads(line)
```

### 6.3 Caching

Cache frequent queries in memory:

```python
from functools import lru_cache

class AuditLogQuery:
    @lru_cache(maxsize=128)
    def get_task_history(self, task_id: str) -> List[Dict]:
        """Cached task history lookup"""
        return self._load_task_history_uncached(task_id)
```

---

## 7. Migration and Compatibility

### 7.1 Legacy Log Format Migration

If JCode v2.x used different log format, provide migration:

```python
def migrate_legacy_logs(legacy_file: Path, output_file: Path):
    """Migrate JCode v2.x logs to v3.0 format"""

    migrated = []

    with open(legacy_file, 'r') as f:
        for line in f:
            legacy = json.loads(line)

            # Map legacy fields to new format
            entry = {
                'log_id': f"JCODE-{legacy['timestamp']}-MIGRATED",
                'timestamp': legacy['timestamp'],
                'actor_type': 'AGENT',  # Assume agent for legacy
                'actor_id': legacy.get('agent', 'unknown'),
                'action_type': legacy.get('action', 'UNKNOWN'),
                'context': {
                    'task_id': legacy.get('task_id'),
                    'iteration': legacy.get('iteration', 0)
                },
                'details': legacy.get('data', {}),
                'integrity': {
                    'content_hash': calculate_details_hash(legacy.get('data', {})),
                    'migrated': True
                },
                'metadata': {
                    'source_system': 'JCODE_LEGACY',
                    'log_version': '1.0',
                    'migration_date': datetime.now(datetime.UTC).isoformat()
                }
            }

            migrated.append(entry)

    # Write migrated logs
    with open(output_file, 'w') as f:
        for entry in migrated:
            f.write(json.dumps(entry) + '\n')
```

### 7.2 Backward Compatibility

JCode v3.0 can read and query v2.x logs:

```python
class AuditLogQuery:
    def __init__(self, audit_dir: Path, legacy_dir: Optional[Path] = None):
        self.audit_dir = audit_dir
        self.legacy_dir = legacy_dir

    def search(self, **kwargs):
        results = []

        # Search current format logs
        results.extend(self._search_current(**kwargs))

        # Search legacy logs if available
        if self.legacy_dir:
            results.extend(self._search_legacy(**kwargs))

        # Sort and deduplicate
        return sorted(set(results), key=lambda x: x['timestamp'])
```

---

## 8. Compliance and Governance

### 8.1 Data Privacy

Logs may contain sensitive information:
- Human operator identities (IP, admin codes - hashed only)
- File paths (project structure)
- Code snippets (implementation details)

**Sanitization Guidelines:**
- Hash admin codes before storage (as shown in §1.4)
- Redact sensitive data from `details` field if needed
- Implement access control on audit directory

### 8.2 Audit Retention Requirements

Based on governance documents:

| Log Type | Retention (HUMAN_INTERFACE.md) | JCode Specification |
|----------|------------------------------|---------------------|
| Human interventions | Permanent | 365 days (cold storage) |
| Quick fixes | Not specified | 365 days (cold storage) |
| Edge cases | Not specified | 90 days (warm storage) |
| Agent executions | Not specified | 7 days (hot) + 90 days (warm) |

**Recommendation:** Archive human interventions permanently for compliance.

### 8.3 Access Control

Audit logs should be:
- Readable by: Admin users, auditors
- Writeable by: JCode system only (append-only)
- Immutable: No delete/modify operations

```python
import os

def set_audit_permissions(audit_dir: Path):
    """Set appropriate filesystem permissions"""

    # Directory: rwxr-x---
    os.chmod(audit_dir, 0o750)

    # Log files: rw-r-----
    for log_file in audit_dir.glob("*.jsonl"):
        os.chmod(log_file, 0o640)
```

---

## 9. Implementation Checklist

- [ ] Implement `AuditLogQuery` class with all query methods
- [ ] Implement log rotation trigger (size/time)
- [ ] Implement index update on each write
- [ ] Implement hash calculation and verification
- [ ] Implement migration tool for v2.x logs
- [ ] Implement access control permissions
- [ ] Create unit tests for all query functions
- [ ] Create integration tests with OpenCode MCP logs
- [ ] Performance benchmark (query speed for 1M entries)
- [ ] Documentation for API reference

---

## Appendix A: Full JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "JCode Audit Log Entry",
  "type": "object",
  "required": ["log_id", "timestamp", "actor_type", "actor_id", "action_type", "details", "integrity", "metadata"],
  "properties": {
    "log_id": {
      "type": "string",
      "pattern": "^(JCODE|OMO)-\\d{8}T\\d{6}\\d{6}-\\d+$"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "actor_type": {
      "type": "string",
      "enum": ["AGENT", "HUMAN", "SYSTEM", "MCP_SERVER"]
    },
    "actor_id": {
      "type": "string"
    },
    "action_type": {
      "type": "string"
    },
    "context": {
      "type": "object",
      "properties": {
        "task_id": {"type": "string"},
        "iteration": {"type": "integer"},
        "stage": {"type": "string"},
        "session_id": {"type": "string"}
      }
    },
    "details": {
      "type": "object"
    },
    "integrity": {
      "type": "object",
      "required": ["content_hash"],
      "properties": {
        "content_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "signature": {"type": "string"}
      }
    },
    "metadata": {
      "type": "object",
      "required": ["source_system", "log_version"],
      "properties": {
        "source_system": {"type": "string", "enum": ["JCODE", "OMO"]},
        "log_version": {"type": "string"},
        "correlation_id": {"type": "string"}
      }
    }
  }
}
```

---

## Appendix B: Example Complete Log Stream

```jsonl
{"log_id":"JCODE-20260224T090000000-00001","timestamp":"2026-02-24T09:00:00.000000Z","actor_type":"AGENT","actor_id":"analyst","action_type":"ANALYSIS_START","context":{"task_id":"task_001","stage":"ANALYSIS"},"details":{"task_description":"Implement user authentication"},"integrity":{"content_hash":"abc123..."},"metadata":{"source_system":"JCODE","log_version":"1.0"}}
{"log_id":"JCODE-20260224T090530000-00002","timestamp":"2026-02-24T09:05:30.000000Z","actor_type":"AGENT","actor_id":"analyst","action_type":"ANALYSIS_COMPLETE","context":{"task_id":"task_001","stage":"ANALYSIS"},"details":{"verifiability":"HARD","risk_level":"MEDIUM"},"integrity":{"content_hash":"def456..."},"metadata":{"source_system":"JCODE","log_version":"1.0"}}
{"log_id":"JCODE-20260224T094000000-00003","timestamp":"2026-02-24T09:40:00.000000Z","actor_type":"HUMAN","actor_id":"human_admin","action_type":"HUMAN_INTERVENTION_EXTEND_ITERATIONS","context":{"task_id":"task_001","iteration":1,"stage":"REVIEW"},"details":{"operator_role":"HUMAN_ADMIN","trigger_condition":"ITERATION_OVERFLOW","reason":"Almost there, just need one more iteration","admin_code_hash":"7ef890..."},"integrity":{"content_hash":"ghi789..."},"metadata":{"source_system":"JCODE","log_version":"1.0"}}
{"log_id":"JCODE-20260224T100000000-00004","timestamp":"2026-02-24T10:00:00.000000Z","actor_type":"SYSTEM","actor_id":"conductor","action_type":"CONDUCTOR_CONTINUE","context":{"task_id":"task_001","iteration":2,"stage":"TEST"},"details":{"decision":"APPROVE_CONTINUE","evidence_sufficient":true},"integrity":{"content_hash":"jkl012..."},"metadata":{"source_system":"JCODE","log_version":"1.0"}}
{"log_id":"OMO-20260224T100500000-00005","timestamp":"2026-02-24T10:05:00.000000Z","actor_type":"MCP_SERVER","actor_id":"filesystem","action_type":"MCP_SERVER_CALL","context":{"session_id":"ses_abc123","mcp_call_id":"call_xyz789"},"details":{"method_name":"write_file","parameters":{"path":"auth.py"}},"integrity":{"content_hash":"mno345..."},"metadata":{"source_system":"OMO","log_version":"1.0","correlation_id":"JCODE-task_001"}}
```

---

**END OF AUDIT_LOG_SPEC**
