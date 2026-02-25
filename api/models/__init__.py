"""
API Models - JCode v3.0

Pydantic schemas for all MCP tools (10 JCode Agent tools + 4 Superpowers tools).
Provides request/response models for API layer integration.

Author: JCode v3.0 Implementation
Status: IMPLEMENTATION
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# Enums
# ============================================================================

class MCPErrorType(str, Enum):
    """MCP Error types as defined in SUPERPOWERS_EXTENSION.md"""
    NON_VERIFIABLE = "NON-VERIFIABLE"
    RULE_VIOLATION = "RULE_VIOLATION"
    EVIDENCE_UNAVAILABLE = "EVIDENCE_UNAVAILABLE"
    ITERATION_OVERFLOW = "ITERATION_OVERFLOW"
    STRUCTURAL_VIOLATION = "STRUCTURAL_VIOLATION"


class MCPErrorAction(str, Enum):
    """MCP Error actions"""
    HUMAN_INTERVENTION = "HUMAN_INTERVENTION"
    RETRY = "RETRY"
    STOP = "STOP"
    CONTINUE = "CONTINUE"


class MCPExecutionMode(str, Enum):
    """Execution modes for MCP tools"""
    FULL = "full"
    LIGHT = "light"
    SAFE = "safe"
    FAST = "fast"
    CUSTOM = "custom"


class VerifiabilityLevel(str, Enum):
    """Verifiability levels for analysis"""
    HARD = "HARD"
    SOFT = "SOFT"
    NON_VERIFIABLE = "NON-VERIFIABLE"


class ReviewResult(str, Enum):
    """Review judgment results"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TestResult(str, Enum):
    """Test verification results"""
    PASSED = "PASSED"
    FAILED = "FAILED"
    EVIDENCE_UNAVAILABLE = "EVIDENCE_UNAVAILABLE"


class ConductorDecision(str, Enum):
    """Final arbitration decisions"""
    DELIVER = "DELIVER"
    ITERATE = "ITERATE"
    STOP = "STOP"


class IssueSeverity(str, Enum):
    """Issue severity levels"""
    MAJOR = "MAJOR"
    MINOR = "MINOR"


class LockAction(str, Enum):
    """Context lock actions"""
    ACQUIRE = "acquire"
    RELEASE = "release"
    EXTEND = "extend"
    CHECK = "check"


class RuleAction(str, Enum):
    """Rule engine actions"""
    EXECUTE = "execute"
    CHECK = "check"
    QUERY = "query"
    VALIDATE = "validate"


class BuildAction(str, Enum):
    """Incremental build actions"""
    GENERATE_DIFF = "generate_diff"
    APPLY = "apply"
    ROLLBACK = "rollback"
    STATUS = "status"


class AuditAction(str, Enum):
    """Audit log actions"""
    WRITE = "write"
    QUERY = "query"
    SEARCH = "search"
    HISTORY = "history"
    INTERVENTIONS = "interventions"


# ============================================================================
# Common Models
# ============================================================================

class ToolRequest(BaseModel):
    """Base request model for all MCP tools"""
    tool_id: str = Field(..., description="Tool identifier")
    context_lock_id: str = Field(..., description="OMO Context Lock ID for state isolation")
    session_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    mode: MCPExecutionMode = Field(default=MCPExecutionMode.FULL, description="Execution mode")


class ToolResponse(BaseModel):
    """Base response model for all MCP tools"""
    tool_id: str = Field(..., description="Tool identifier")
    context_lock_id: str = Field(..., description="OMO Context Lock ID")
    session_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    section: str = Field(..., description="Output section marker (e.g., [ANALYSIS])")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific output payload")
    duration_ms: Optional[int] = Field(None, description="Execution duration in milliseconds")


class MCPError(BaseModel):
    """MCP Error structure"""
    type: Optional[MCPErrorType] = Field(None, description="Error type")
    message: Optional[str] = Field(None, description="Error message")
    action: Optional[MCPErrorAction] = Field(None, description="Recommended action")

    def is_present(self) -> bool:
        """Check if error has any content"""
        return self.type is not None or self.message is not None


class ErrorResponse(BaseModel):
    """Error response wrapper"""
    tool_id: str = Field(..., description="Tool identifier")
    context_lock_id: str = Field(..., description="OMO Context Lock ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    error: MCPError = Field(..., description="Error details")


# ============================================================================
# JCode Agent Tool Models
# ============================================================================

# --- jcode.analyze (Analyst - 司马迁) ---

class AnalyzeRequest(ToolRequest):
    """Request for jcode.analyze tool"""
    tool_id: str = Field(default="jcode.analyze", init=False)
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data containing problem_statement and user_requirements"
    )

    @field_validator('input_data')
    @classmethod
    def validate_input_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required fields are present"""
        if 'problem_statement' not in v:
            raise ValueError("input_data must contain 'problem_statement'")
        return v


class NFRs(BaseModel):
    """Non-functional requirements"""
    performance: Optional[str] = Field(None, description="Performance requirements")
    maintainability: Optional[str] = Field(None, description="Maintainability requirements")
    security: Optional[str] = Field(None, description="Security requirements")
    compatibility: Optional[str] = Field(None, description="Compatibility requirements")
    observability: Optional[str] = Field(None, description="Observability requirements")


class AnalyzePayload(BaseModel):
    """Payload for jcode.analyze response"""
    verifiability: VerifiabilityLevel = Field(..., description="Verifiability assessment")
    nfrs: NFRs = Field(default_factory=NFRs, description="Non-functional requirements")
    risks: List[str] = Field(default_factory=list, description="Identified risks")
    unknowns: List[str] = Field(default_factory=list, description="Unknown factors")


class AnalyzeResponse(ToolResponse):
    """Response from jcode.analyze tool"""
    tool_id: str = Field(default="jcode.analyze", init=False)
    section: str = Field(default="[ANALYSIS]", init=False)
    payload: AnalyzePayload
    error: Optional[MCPError] = Field(None, description="Error if analysis failed")


# --- jcode.plan (Planner - 商鞅) ---

class PlanRequest(ToolRequest):
    """Request for jcode.plan tool"""
    tool_id: str = Field(default="jcode.plan", init=False)
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data containing analysis output"
    )

    @field_validator('input_data')
    @classmethod
    def validate_input_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required fields are present"""
        if 'analysis' not in v:
            raise ValueError("input_data must contain 'analysis'")
        return v


class Task(BaseModel):
    """Atomic task definition"""
    todo: str = Field(..., description="Atomic task description")
    done_when: str = Field(..., description="Verification condition")
    verify_by: str = Field(..., description="Evidence source")


class PlanPayload(BaseModel):
    """Payload for jcode.plan response"""
    tasks: List[Task] = Field(default_factory=list, description="Atomic tasks")
    dependencies: List[List[str]] = Field(default_factory=list, description="Task dependencies")


class PlanResponse(ToolResponse):
    """Response from jcode.plan tool"""
    tool_id: str = Field(default="jcode.plan", init=False)
    section: str = Field(default="[TASKS]", init=False)
    payload: PlanPayload
    error: Optional[MCPError] = Field(None, description="Error if planning failed")


# --- jcode.implement (Implementer - 鲁班) ---

class ImplementRequest(ToolRequest):
    """Request for jcode.implement tool"""
    tool_id: str = Field(default="jcode.implement", init=False)
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data containing tasks, om_rules, and iteration"
    )

    @field_validator('input_data')
    @classmethod
    def validate_input_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required fields are present"""
        if 'tasks' not in v:
            raise ValueError("input_data must contain 'tasks'")
        if 'iteration' not in v:
            raise ValueError("input_data must contain 'iteration'")
        return v


class ImplementationMetadata(BaseModel):
    """Implementation metadata"""
    iteration: int = Field(..., description="Iteration number")
    changes_count: int = Field(default=0, description="Number of changes made")


class Artifacts(BaseModel):
    """Implementation artifacts"""
    files: List[str] = Field(default_factory=list, description="Modified file paths")
    diff: str = Field(default="", description="Unified diff format string")
    metadata: ImplementationMetadata = Field(default_factory=ImplementationMetadata, description="Metadata")


class ImplementPayload(BaseModel):
    """Payload for jcode.implement response"""
    artifacts: Artifacts = Field(default_factory=Artifacts, description="Generated artifacts")


class ImplementResponse(ToolResponse):
    """Response from jcode.implement tool"""
    tool_id: str = Field(default="jcode.implement", init=False)
    section: str = Field(default="[IMPLEMENTATION]", init=False)
    payload: ImplementPayload
    error: Optional[MCPError] = Field(None, description="Error if implementation failed")


# --- jcode.review (Reviewer - 包拯) ---

class ReviewRequest(ToolRequest):
    """Request for jcode.review tool"""
    tool_id: str = Field(default="jcode.review", init=False)
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data containing tasks, implementation, and quick_fix_eligible"
    )

    @field_validator('input_data')
    @classmethod
    def validate_input_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required fields are present"""
        if 'tasks' not in v:
            raise ValueError("input_data must contain 'tasks'")
        if 'implementation' not in v:
            raise ValueError("input_data must contain 'implementation'")
        return v


class ReviewIssue(BaseModel):
    """Review issue"""
    task_ref: str = Field(..., description="Task reference")
    severity: IssueSeverity = Field(..., description="Issue severity")
    description: str = Field(..., description="Issue description")


class ReviewPayload(BaseModel):
    """Payload for jcode.review response"""
    result: ReviewResult = Field(..., description="Review judgment (APPROVED/REJECTED)")
    issues: List[ReviewIssue] = Field(default_factory=list, description="Identified issues")
    quick_fix_trigger: Optional[str] = Field(None, description="Minor fix rule ID if applicable")


class ReviewResponse(ToolResponse):
    """Response from jcode.review tool"""
    tool_id: str = Field(default="jcode.review", init=False)
    section: str = Field(default="[REVIEW]", init=False)
    payload: ReviewPayload
    error: Optional[MCPError] = Field(None, description="Error if review failed")


# --- jcode.test (Tester - 张衡) ---

class TestRequest(ToolRequest):
    """Request for jcode.test tool"""
    tool_id: str = Field(default="jcode.test", init=False)
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data containing tasks, implementation, and verify_by_clauses"
    )

    @field_validator('input_data')
    @classmethod
    def validate_input_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required fields are present"""
        if 'tasks' not in v:
            raise ValueError("input_data must contain 'tasks'")
        if 'implementation' not in v:
            raise ValueError("input_data must contain 'implementation'")
        return v


class TestEvidence(BaseModel):
    """Test evidence"""
    test_output: str = Field(default="", description="Test output")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Test metrics")
    screenshots: List[str] = Field(default_factory=list, description="Screenshot paths")


class TestPayload(BaseModel):
    """Payload for jcode.test response"""
    result: TestResult = Field(..., description="Test judgment (PASSED/FAILED/EVIDENCE_UNAVAILABLE)")
    evidence: TestEvidence = Field(default_factory=TestEvidence, description="Test evidence")
    failed_clauses: List[str] = Field(default_factory=list, description="Failed verification clauses")


class TestResponse(ToolResponse):
    """Response from jcode.test tool"""
    tool_id: str = Field(default="jcode.test", init=False)
    section: str = Field(default="[TEST]", init=False)
    payload: TestPayload
    error: Optional[MCPError] = Field(None, description="Error if testing failed")


# --- jcode.conductor (Conductor - 韩非子) ---

class ConductorRequest(ToolRequest):
    """Request for jcode.conductor tool"""
    tool_id: str = Field(default="jcode.conductor", init=False)
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data containing review_result, test_result, iteration_count, max_iterations"
    )

    @field_validator('input_data')
    @classmethod
    def validate_input_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required fields are present"""
        if 'review_result' not in v:
            raise ValueError("input_data must contain 'review_result'")
        if 'test_result' not in v:
            raise ValueError("input_data must contain 'test_result'")
        if 'iteration_count' not in v:
            raise ValueError("input_data must contain 'iteration_count'")
        if 'max_iterations' not in v:
            raise ValueError("input_data must contain 'max_iterations'")
        return v


class Deliverables(BaseModel):
    """Final deliverables"""
    files: List[str] = Field(default_factory=list, description="Delivered file paths")
    audit_log: str = Field(default="", description="Audit log path")


class ConductorPayload(BaseModel):
    """Payload for jcode.conductor response"""
    decision: ConductorDecision = Field(..., description="Final decision (DELIVER/ITERATE/STOP)")
    reason: str = Field(..., description="Reason for decision")
    next_iteration: Optional[int] = Field(None, description="Next iteration number if ITERATE")
    deliverables: Deliverables = Field(default_factory=Deliverables, description="Deliverables if DELIVER")


class ConductorResponse(ToolResponse):
    """Response from jcode.conductor tool"""
    tool_id: str = Field(default="jcode.conductor", init=False)
    section: str = Field(default="[FINAL]", init=False)
    payload: ConductorPayload
    error: Optional[MCPError] = Field(None, description="Error if arbitration failed")


# --- jcode.lock (Context Lock) ---

class LockRequest(ToolRequest):
    """Request for jcode.lock tool"""
    tool_id: str = Field(default="jcode.lock", init=False)
    action: LockAction = Field(..., description="Lock action (acquire/release/extend/check)")
    resource_paths: List[str] = Field(default_factory=list, description="Resource paths to lock")
    timeout_seconds: Optional[int] = Field(None, description="Timeout in seconds")


class LockInfo(BaseModel):
    """Lock information"""
    lock_id: str = Field(..., description="Lock identifier")
    owner: str = Field(..., description="Lock owner")
    acquired_at: datetime = Field(..., description="Acquisition timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    resource_paths: List[str] = Field(default_factory=list, description="Locked resource paths")


class LockPayload(BaseModel):
    """Payload for jcode.lock response"""
    lock_id: Optional[str] = Field(None, description="Lock ID if acquired")
    acquired: bool = Field(..., description="Whether lock was acquired/released successfully")
    lock_info: Optional[LockInfo] = Field(None, description="Lock information")
    resources_locked: List[str] = Field(default_factory=list, description="Locked resources")


class LockResponse(ToolResponse):
    """Response from jcode.lock tool"""
    tool_id: str = Field(default="jcode.lock", init=False)
    section: str = Field(default="[LOCK]", init=False)
    payload: LockPayload
    error: Optional[MCPError] = Field(None, description="Error if lock operation failed")


# ============================================================================
# Superpowers Tool Models
# ============================================================================

# --- rule_engine ---

class RuleEngineRequest(ToolRequest):
    """Request for rule_engine tool"""
    tool_id: str = Field(default="rule_engine", init=False)
    action: RuleAction = Field(..., description="Rule engine action")
    rules: List[str] = Field(default_factory=list, description="Rule IDs to execute/check")
    context: Dict[str, Any] = Field(default_factory=dict, description="Rule execution context")
    check_mode: bool = Field(default=False, description="Check mode (dry-run)")


class RuleResult(BaseModel):
    """Individual rule result"""
    rule_id: str = Field(..., description="Rule identifier")
    passed: bool = Field(..., description="Whether rule passed")
    message: str = Field(..., description="Rule result message")
    severity: Optional[IssueSeverity] = Field(None, description="Issue severity if failed")


class RuleEnginePayload(BaseModel):
    """Payload for rule_engine response"""
    results: List[RuleResult] = Field(default_factory=list, description="Rule execution results")
    all_passed: bool = Field(..., description="Whether all rules passed")
    violations: List[str] = Field(default_factory=list, description="Violated rule IDs")


class RuleEngineResponse(ToolResponse):
    """Response from rule_engine tool"""
    tool_id: str = Field(default="rule_engine", init=False)
    section: str = Field(default="[RULE_ENGINE]", init=False)
    payload: RuleEnginePayload
    error: Optional[MCPError] = Field(None, description="Error if rule execution failed")


# --- incremental_build ---

class IncrementalBuildRequest(ToolRequest):
    """Request for incremental_build tool"""
    tool_id: str = Field(default="incremental_build", init=False)
    action: BuildAction = Field(..., description="Build action")
    changes: List[Dict[str, Any]] = Field(default_factory=list, description="Change specifications")
    rollback_point: Optional[str] = Field(None, description="Rollback point identifier")


class DiffInfo(BaseModel):
    """Diff information"""
    files_changed: List[str] = Field(default_factory=list, description="Changed file paths")
    lines_added: int = Field(default=0, description="Lines added")
    lines_removed: int = Field(default=0, description="Lines removed")
    diff_content: str = Field(default="", description="Unified diff content")


class BuildInfo(BaseModel):
    """Build information"""
    build_id: str = Field(..., description="Build identifier")
    status: str = Field(..., description="Build status")
    files_processed: List[str] = Field(default_factory=list, description="Processed files")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Build timestamp")


class IncrementalBuildPayload(BaseModel):
    """Payload for incremental_build response"""
    build_id: Optional[str] = Field(None, description="Build identifier")
    success: bool = Field(..., description="Whether operation succeeded")
    diff_info: Optional[DiffInfo] = Field(None, description="Diff information if generated")
    build_info: Optional[BuildInfo] = Field(None, description="Build information")
    rollback_success: Optional[bool] = Field(None, description="Rollback success status if applicable")


class IncrementalBuildResponse(ToolResponse):
    """Response from incremental_build tool"""
    tool_id: str = Field(default="incremental_build", init=False)
    section: str = Field(default="[BUILD]", init=False)
    payload: IncrementalBuildPayload
    error: Optional[MCPError] = Field(None, description="Error if build operation failed")


# --- audit_log ---

class AuditLogRequest(ToolRequest):
    """Request for audit_log tool"""
    tool_id: str = Field(default="audit_log", init=False)
    action: AuditAction = Field(..., description="Audit log action")
    log_data: Optional[Dict[str, Any]] = Field(None, description="Log data to write")
    query_params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    time_range: Optional[Dict[str, datetime]] = Field(None, description="Time range filter")


class AuditLogEntry(BaseModel):
    """Audit log entry"""
    log_id: str = Field(..., description="Log entry identifier")
    timestamp: datetime = Field(..., description="Log timestamp")
    event_type: str = Field(..., description="Event type")
    tool_name: str = Field(..., description="Tool name")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Event context")


class AuditLogPayload(BaseModel):
    """Payload for audit_log response"""
    log_id: Optional[str] = Field(None, description="Written log entry ID")
    entries: List[AuditLogEntry] = Field(default_factory=list, description="Queried log entries")
    total_count: int = Field(default=0, description="Total number of entries")
    interventions: List[Dict[str, Any]] = Field(default_factory=list, description="Human intervention records")


class AuditLogResponse(ToolResponse):
    """Response from audit_log tool"""
    tool_id: str = Field(default="audit_log", init=False)
    section: str = Field(default="[AUDIT]", init=False)
    payload: AuditLogPayload
    error: Optional[MCPError] = Field(None, description="Error if audit operation failed")


# ============================================================================
# Config Models
# ============================================================================

class JCodeConfig(BaseModel):
    """JCode configuration model"""
    enabled: bool = Field(default=True, description="JCode enabled status")
    mode: MCPExecutionMode = Field(default=MCPExecutionMode.FULL, description="Execution mode")
    max_iterations: int = Field(default=5, description="Maximum iterations")
    agents: Dict[str, bool] = Field(
        default_factory=lambda: {
            "analyst": True,
            "planner": True,
            "implementer": True,
            "reviewer": True,
            "tester": True,
            "conductor": True
        },
        description="Agent enabled status"
    )
    rules: Dict[str, Dict[str, bool]] = Field(
        default_factory=lambda: {
            "constitution": {
                "R001_no_skip_review": True,
                "R002_require_test": True,
                "R003_nfr_required": True,
                "R004_human_intervention_on_error": True
            },
            "governance": {
                "G001_audit_logging": True,
                "G002_iteration_tracking": True,
                "G003_context_lock_required": True
            }
        },
        description="Rule enabled status"
    )

    model_config = ConfigDict(extra="allow")


# ============================================================================
# Export all models
# ============================================================================

__all__ = [
    # Enums
    "MCPErrorType",
    "MCPErrorAction",
    "MCPExecutionMode",
    "VerifiabilityLevel",
    "ReviewResult",
    "TestResult",
    "ConductorDecision",
    "IssueSeverity",
    "LockAction",
    "RuleAction",
    "BuildAction",
    "AuditAction",
    # Common Models
    "ToolRequest",
    "ToolResponse",
    "MCPError",
    "ErrorResponse",
    # JCode Agent Models
    "AnalyzeRequest",
    "AnalyzeResponse",
    "AnalyzePayload",
    "NFRs",
    "PlanRequest",
    "PlanResponse",
    "PlanPayload",
    "Task",
    "ImplementRequest",
    "ImplementResponse",
    "ImplementPayload",
    "Artifacts",
    "ImplementationMetadata",
    "ReviewRequest",
    "ReviewResponse",
    "ReviewPayload",
    "ReviewIssue",
    "TestRequest",
    "TestResponse",
    "TestPayload",
    "TestEvidence",
    "ConductorRequest",
    "ConductorResponse",
    "ConductorPayload",
    "Deliverables",
    "LockRequest",
    "LockResponse",
    "LockPayload",
    "LockInfo",
    # Superpowers Models
    "RuleEngineRequest",
    "RuleEngineResponse",
    "RuleEnginePayload",
    "RuleResult",
    "IncrementalBuildRequest",
    "IncrementalBuildResponse",
    "IncrementalBuildPayload",
    "DiffInfo",
    "BuildInfo",
    "AuditLogRequest",
    "AuditLogResponse",
    "AuditLogPayload",
    "AuditLogEntry",
    # Config Models
    "JCodeConfig",
]
