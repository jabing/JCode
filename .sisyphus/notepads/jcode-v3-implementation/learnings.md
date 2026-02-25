# Learnings - JCode v3 Implementation

## Task: Implement core/rule_engine.py

### Successful Patterns
1. **Dataclass Design**: Using `@dataclass` for Rule, ViolationResult, and SoftHookState provided clean, immutable data structures with automatic `__init__` and `__repr__` methods.

2. **Enum-Based Priority System**: Priority and Severity enums with string values provided type safety while maintaining JSON/YAML serialization compatibility.

3. **Regex Pattern Caching**: Compiled regex patterns stored in `self.compiled_patterns` dictionary for efficient repeated matching.

4. **Context Filtering**: Multi-layered filtering (file patterns, context filters, phase checking) before pattern matching improves performance.

5. **Soft Hooks State Tracking**: Separate state management for soft hooks with ignore counting and upgrade thresholds.

### Key Implementation Details

#### Priority Mapping
```python
SEVERITY_TO_PRIORITY = {
    Severity.CRITICAL: Priority.P0,
    Severity.HIGH: Priority.P1,
    Severity.MEDIUM: Priority.P2,
    Severity.LOW: Priority.P3,
}
```

#### Violation Handler Actions
- **P0 (TERMINATE)**: Raises `RuleExecutionError`, notifies human, logs audit, triggers rollback
- **P1 (QUICK_FIX)**: Marks for quick fix via QUICK_FIX_CHANNEL, no iteration penalty
- **P2 (LOG_ONLY)**: Logs to audit log without interrupting task
- **P3 (SOFT_HOOK)**: Optional warning, tracks ignore count, upgrades to P2 if threshold exceeded

#### Soft Hooks Upgrade Logic
```python
if state.ignore_count >= threshold and not state.upgraded:
    state.upgraded = True
    violation.priority = Priority.P2
    violation.handler = "LOG_ONLY"
```

### Conventions Established
1. All methods have docstrings with Args/Returns/Raises sections
2. Dataclasses use field(default_factory=list) for mutable default arguments
3. Exception hierarchy: RuleEngineError -> RuleParseError/RuleExecutionError
4. Timestamps use ISO 8601 format via `datetime.utcnow().isoformat()`
5. Rule IDs follow pattern: CATEGORY-### (e.g., CONSTITUTION-001)

### Testing Strategy
- Unit tests for each method
- Integration tests for full workflows
- Edge cases: empty context, malformed patterns, missing soft hooks config
- Verification of all 4 priority levels and handlers

### Dependencies
- `yaml`: PyYAML for YAML parsing
- `re`: Python regex for pattern matching
- `dataclasses`: For data structure definitions
- `enum`: For Priority and Severity enums
- `typing`: For type hints
- `datetime`: For timestamps

### File Statistics
- Lines: 561
- Classes: 4 (RuleEngine, Rule, ViolationResult, SoftHookState)
- Dataclasses: 5 (RuleMatch, SoftHooksConfig, Rule, ViolationResult, SoftHookState)
- Enums: 2 (Priority, Severity)
- Methods: 15 public methods

### Integration Points
- **Audit Logger**: P0/P2 violations log to audit log
- **Quick Fix Channel**: P1 violations trigger quick fix flow
- **Human Interface**: P0 violations force human intervention
- **Context Lock**: Rule execution respects context filters
- **MCP Tools**: Rule engine exposed as `rule_engine` MCP tool
# Learnings - Task 4: Implement core/switch_manager.py

## Pattern Matching for Glob Patterns

**Challenge**: Python's `fnmatch.fnmatch()` doesn't properly support `**` glob patterns (recursive directory matching).

**Solution**: Implemented custom pattern matching logic that:
1. Handles special case `**/config/**` to match any path containing `/config/`
2. Handles `**/prefix` patterns to match suffix anywhere in path
3. Handles `prefix/**` patterns to match prefix and all subdirectories
4. Handles `**` in the middle of patterns
5. Falls back to `fnmatch` for simple patterns without `**`

**Code Pattern**:
```python
if normalized_pattern == '**/config/**':
    if '/config/' in normalized_path or normalized_path.startswith('config/'):
        return True
elif normalized_pattern.startswith('**/'):
    suffix = normalized_pattern[3:]
    # Convert * to [^/]* and use regex
    suffix = suffix.replace('*', '[^/]*')
    if re.search(suffix, normalized_path):
        return True
```

## Configuration Priority Resolution

**Implementation**: Configuration merging follows strict priority order:
1. Default config (built-in)
2. OMO config (`.omo/config.yaml`)
3. User config (`~/.jcode/config.yaml`)
4. Project config (`.jcode/config.yaml`)
5. Specified config file (`config/jcode_config.yaml`)
6. Session overrides (runtime, highest priority)

**Key Design Decision**: Session overrides are stored separately and merged at resolution time, allowing them to be cleared without reloading the entire configuration.

## Dataclass Field Defaults

**Pattern**: Use `field(default_factory=dict)` for mutable default values in dataclasses to avoid shared mutable state issues:

```python
@dataclass
class SwitchManager:
    _config: Dict[str, Any] = field(default_factory=dict)
    _session_overrides: Dict[str, Any] = field(default_factory=dict)
```

## Configuration Validation

**Two-Level Validation**:
1. Runtime validation in `set()` method before applying changes
2. Post-load validation in `_validate_config()` and `_validate_agents()`

**Agent Constraints**:
- Cannot disable all required agents (analyst, planner, implementer, conductor)
- Cannot disable both reviewer and tester without enabling conductor

## Path Normalization

**Pattern**: Always normalize path separators to forward slashes (`/`) for cross-platform compatibility:

```python
normalized_path = str(file_path).replace('\', '/')
```

## YAML Configuration Loading

**Safe Loading**: Use `yaml.safe_load()` to avoid security issues with untrusted YAML files.

**Graceful Degradation**: Return `None` for missing or invalid config files instead of raising exceptions, allowing system to continue with defaults.
