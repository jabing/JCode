# AGENTS.md — governance/

**Generated:** 2026-02-24
**Scope:** System-level governance, constitutional law, termination authority
**Status:** SEALED / IMMUTABLE

## OVERVIEW
Defines the non-negotiable rules that all Agents and CONDUCTOR must obey; system safety comes from explicit prohibitions, not permissions.

## WHERE TO LOOK

| File | Purpose | When to Read |
|---|---|---|
| AGENT_CONSTITUTION.md | Role boundaries, permissions, failure signals | Before any Agent implementation |
| CONDUCTOR.md | Final arbitration protocol, STOP conditions | When designing termination logic |
| HUMAN_INTERFACE.md | Human intervention points, audit requirements | When defining human interaction flows |
| EDGE_CASES.md | State machines for edge cases | When handling NON-VERIFIABLE/overflow/violation |
| QUICK_FIX_CHANNEL.md | Fast correction for minor issues | When enabling local fixes without full iteration |
| OUTPUT_FORMAT_GUIDELINES.md | Format templates and validation | When implementing human-readable outputs |
| OMO_INTEGRATION.md | Oh-my-opencode integration architecture | When implementing OpenCode extension |
| CONTEXT_LOCK.md | Context Lock MCP tool interface | When integrating with OMO context management |
| RULE_ENGINE.md | Rule Engine MCP tool specification | When defining governance rules |
| INCREMENTAL_BUILD.md | Incremental build MCP tool | When implementing file-level edits |
| AUDIT_LOG_SPEC.md | Unified audit log specification | When designing logging infrastructure |
| SUPERPOWERS_EXTENSION.md | MCP tool registration & agent tools | When registering JCode tools |
| JCODE_SWITCH.md | Enablement switch mechanism | When configuring JCode governance |

## CONVENTIONS

**Constitutional Supremacy**
- Any rule in this directory overrides all other documentation
- Changes require explicit SEALED revision mark
- Ambiguity defaults to the most restrictive interpretation

**Persona Anchors**
- Analyst = 司马迁 (records truth, no solutions)
- Planner = 商鞅 (defines law, not execution)
- Implementer = 鲁班 (builds only what is authorized)
- Reviewer = 包拯 (binary judgment, no advice)
- Tester = 张衡 (evidence only, no speculation)
- CONDUCTOR = 韩非子 (terminates when rules demand)

**Power Flow (Strictly Unidirectional)**
```
ANALYSIS → TASKS → IMPLEMENTATION → REVIEW → TEST → CONDUCTOR
```
- No upstream writes
- No cross-layer appeals
- Violation = immediate STRUCTURAL VIOLATION

**Switch Mechanism (4-Level Enablement)**
- JCode governance layer is optional (configurable via `jcode.enabled`)
- Mode switch: `full|light|safe|fast|custom` controls governance intensity
- Agent-level switch: individually enable/disable each Agent
## ANTI-PATTERNS

**Role Drift**
- Analyst suggesting solutions
- Planner prescribing implementation steps
- Implementer "improving" beyond TASKS
- Reviewer providing code examples
- Tester explaining failure causes
- CONDUCTOR participating in content

**Process Violations**
- Skipping REVIEW or TEST
- Proceeding without evidence
- Iteration without increment counter
- Negotiating STOP conditions

**Authority Erosion**
- "Emergency exceptions" to constitution
- Softening STOP due to sunk cost
- Allowing partial delivery on REJECTED

**Standalone Implementation Anti-Pattern**
- Implementing JCode governance logic outside OMO Superpowers
- JCode MUST be implemented as MCP tools registered to OMO
- Direct file system access without Context Lock = STRUCTURAL VIOLATION
- Bypassing Rule Engine = CONSTITUTIONAL BREACH
- See OMO_INTEGRATION.md §0 for integration architecture

---

> System security is not built on trust.
> It is built on the certainty that violations will be terminated.

**SEALED.**
