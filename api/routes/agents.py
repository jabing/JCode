"""
Agent Routes - JCode v3.0

REST endpoints for all 6 JCode Agent tools and Superpowers MCP tools.
Provides FastAPI endpoints that dispatch to AgentManager for execution.

Author: JCode v3.0 Implementation
Status: IMPLEMENTATION
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
import uuid
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/v1")
agent_manager = None  # Will be initialized in api/main.py


# 6 JCode Agent Type Constants
AGENT_ANALYST = "analyst"
AGENT_PLANNER = "planner"
AGENT_IMPLEMENTER = "implementer"
AGENT_REVIEWER = "reviewer"
AGENT_TESTER = "tester"
AGENT_CONDUCTOR = "conductor"


# ============================================================================
# Request/Response Models
# ============================================================================

class AgentRequest(BaseModel):
    """Base request for agent operations"""
    context_lock_id: str = Field(..., description="OMO Context Lock ID for state isolation")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Phase-specific input payload")
    mode: str = Field(default="full", description="Execution mode (full/light/safe/fast/custom)")


class ToolRequest(BaseModel):
    """Base request for tool operations"""
    context_lock_id: str = Field(..., description="OMO Context Lock ID for state isolation")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific input payload")
    mode: str = Field(default="full", description="Execution mode")


class AgentResponse(BaseModel):
    """Standard agent response"""
    task_id: str = Field(..., description="Unique task identifier")
    actor: str = Field(..., description="Agent type that handled the request")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    section: str = Field(..., description="Output section marker (e.g., [ANALYSIS])")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Phase-specific output payload")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information if operation failed")
    iteration: Optional[int] = Field(default=None, description="Current iteration number")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    action: str = Field(..., description="Suggested action (RETRY/STOP/HUMAN_INTERVENTION)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    integration: str
    agents: List[str]


# ============================================================================
# Helper Functions
# ============================================================================

def generate_task_id() -> str:
    """Generate unique task ID"""
    return f"task_{uuid.uuid4().hex[:12]}"


def get_timestamp() -> str:
    """Get current ISO 8601 timestamp"""
    return datetime.utcnow().isoformat() + "Z"


async def dispatch_to_agent_manager(
    agent_type: str,
    context_lock_id: str,
    input_data: Dict[str, Any],
    mode: str
) -> Dict[str, Any]:
    """
    Dispatch request to AgentManager

    Args:
        agent_type: Type of agent to dispatch
        context_lock_id: OMO Context Lock ID
        input_data: Input data for the agent
        mode: Execution mode

    Returns:
        Agent response dictionary

    Raises:
        HTTPException: If dispatch fails
    """
    global agent_manager

    if agent_manager is None:
        logger.warning("AgentManager not initialized, returning mock response")
        # Mock response for testing when AgentManager not yet available
        return {
            "section": f"[{agent_type.upper()}]",
            "payload": {
                "message": f"Agent {agent_type} executed in mock mode",
                "input_data": input_data
            },
            "error": None
        }

    try:
        # Start iteration tracking
        agent_manager.start_iteration()

        # Check iteration count
        if not agent_manager.check_iteration_count():
            logger.error(f"MAX_ITERATIONS exceeded for agent: {agent_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_type": "ITERATION_OVERFLOW",
                    "message": "Maximum iterations exceeded",
                    "action": "HUMAN_INTERVENTION"
                }
            )

        # Dispatch to agent
        result = agent_manager.dispatch_agent(agent_type, {
            "context_lock_id": context_lock_id,
            "input_data": input_data,
            "mode": mode
        })

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent dispatch failed: {agent_type} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "STRUCTURAL_VIOLATION",
                "message": str(e),
                "action": "STOP"
            }
        )


# ============================================================================
# JCode Agent Endpoints
# ============================================================================

@router.post("/jcode/analyze", response_model=AgentResponse, summary="Analyst problem analysis", tags=["Agents"])
async def analyze(request: AgentRequest) -> AgentResponse:
    """
    Execute Analyst agent for problem analysis

    - **context_lock_id**: Required for state isolation
    - **input_data**: problem_statement, user_requirements
    - **mode**: Execution mode (full/light/safe/fast/custom)

    Returns [ANALYSIS] output with verifiability assessment, NFRs, risks
    """
    logger.info(f"Analyzing problem: {request.context_lock_id}")

    result = await dispatch_to_agent_manager(
        AGENT_ANALYST,
        request.context_lock_id,
        request.input_data,
        request.mode
    )

    return AgentResponse(
        task_id=generate_task_id(),
        actor=AGENT_ANALYST,
        timestamp=get_timestamp(),
        section=result.get("section", "[ANALYSIS]"),
        payload=result.get("payload", {}),
        error=result.get("error"),
        iteration=1
    )


@router.post("/jcode/plan", response_model=AgentResponse, summary="Task planning", tags=["Agents"])
async def plan(request: AgentRequest) -> AgentResponse:
    """
    Execute Planner agent for task planning

    - **context_lock_id**: Required for state isolation
    - **input_data**: analysis from Analyst
    - **mode**: Execution mode (full/light/safe/fast/custom)

    Returns [TASKS] output with atomic verifiable tasks
    """
    logger.info(f"Planning tasks: {request.context_lock_id}")

    result = await dispatch_to_agent_manager(
        AGENT_PLANNER,
        request.context_lock_id,
        request.input_data,
        request.mode
    )

    return AgentResponse(
        task_id=generate_task_id(),
        actor=AGENT_PLANNER,
        timestamp=get_timestamp(),
        section=result.get("section", "[TASKS]"),
        payload=result.get("payload", {}),
        error=result.get("error"),
        iteration=1
    )


@router.post("/jcode/implement", response_model=AgentResponse, summary="Code implementation", tags=["Agents"])
async def implement(request: AgentRequest) -> AgentResponse:
    """
    Execute Implementer agent for code implementation

    - **context_lock_id**: Required for state isolation
    - **input_data**: tasks, om_rules, iteration
    - **mode**: Execution mode (full/light/safe/fast/custom)

    Returns [IMPLEMENTATION] output with code artifacts
    """
    logger.info(f"Implementing code: {request.context_lock_id}")

    result = await dispatch_to_agent_manager(
        AGENT_IMPLEMENTER,
        request.context_lock_id,
        request.input_data,
        request.mode
    )

    return AgentResponse(
        task_id=generate_task_id(),
        actor=AGENT_IMPLEMENTER,
        timestamp=get_timestamp(),
        section=result.get("section", "[IMPLEMENTATION]"),
        payload=result.get("payload", {}),
        error=result.get("error"),
        iteration=request.input_data.get("iteration", 1)
    )


@router.post("/jcode/review", response_model=AgentResponse, summary="Compliance review", tags=["Agents"])
async def review(request: AgentRequest) -> AgentResponse:
    """
    Execute Reviewer agent for compliance review

    - **context_lock_id**: Required for state isolation
    - **input_data**: tasks, implementation, quick_fix_eligible
    - **mode**: Execution mode (full/light/safe/fast/custom)

    Returns [REVIEW] output with APPROVED/REJECTED judgment
    """
    logger.info(f"Reviewing implementation: {request.context_lock_id}")

    result = await dispatch_to_agent_manager(
        AGENT_REVIEWER,
        request.context_lock_id,
        request.input_data,
        request.mode
    )

    return AgentResponse(
        task_id=generate_task_id(),
        actor=AGENT_REVIEWER,
        timestamp=get_timestamp(),
        section=result.get("section", "[REVIEW]"),
        payload=result.get("payload", {}),
        error=result.get("error"),
        iteration=1
    )


@router.post("/jcode/test", response_model=AgentResponse, summary="Evidence verification", tags=["Agents"])
async def test(request: AgentRequest) -> AgentResponse:
    """
    Execute Tester agent for evidence verification

    - **context_lock_id**: Required for state isolation
    - **input_data**: tasks, implementation, verify_by_clauses
    - **mode**: Execution mode (full/light/safe/fast/custom)

    Returns [TEST] output with PASSED/FAILED judgment
    """
    logger.info(f"Testing implementation: {request.context_lock_id}")

    result = await dispatch_to_agent_manager(
        AGENT_TESTER,
        request.context_lock_id,
        request.input_data,
        request.mode
    )

    return AgentResponse(
        task_id=generate_task_id(),
        actor=AGENT_TESTER,
        timestamp=get_timestamp(),
        section=result.get("section", "[TEST]"),
        payload=result.get("payload", {}),
        error=result.get("error"),
        iteration=1
    )


@router.post("/jcode/conductor", response_model=AgentResponse, summary="Final arbitration", tags=["Agents"])
async def conductor(request: AgentRequest) -> AgentResponse:
    """
    Execute Conductor agent for final arbitration

    - **context_lock_id**: Required for state isolation
    - **input_data**: review_result, test_result, iteration_count, max_iterations
    - **mode**: Execution mode (full/light)

    Returns [FINAL] output with DELIVER/ITERATE/STOP decision
    """
    logger.info(f"Conducting final arbitration: {request.context_lock_id}")

    result = await dispatch_to_agent_manager(
        AGENT_CONDUCTOR,
        request.context_lock_id,
        request.input_data,
        request.mode
    )

    return AgentResponse(
        task_id=generate_task_id(),
        actor=AGENT_CONDUCTOR,
        timestamp=get_timestamp(),
        section=result.get("section", "[FINAL]"),
        payload=result.get("payload", {}),
        error=result.get("error"),
        iteration=request.input_data.get("iteration_count", 1)
    )


# ============================================================================
# Superpowers Tool Endpoints
# ============================================================================

@router.post("/tools/lock", response_model=AgentResponse, summary="Context Lock tool", tags=["Tools"])
async def context_lock(request: ToolRequest) -> AgentResponse:
    """
    Execute Context Lock tool

    - **context_lock_id**: Required for state isolation
    - **input_data**: operation (acquire/refresh/release/query)
    - **mode**: Execution mode

    Returns context lock operation result
    """
    logger.info(f"Context lock operation: {request.context_lock_id}")

    # Will be implemented via MCP client when available
    return AgentResponse(
        task_id=generate_task_id(),
        actor="context_lock",
        timestamp=get_timestamp(),
        section="[CONTEXT_LOCK]",
        payload={
            "message": "Context lock tool executed",
            "operation": request.input_data.get("operation", "unknown")
        },
        error=None
    )


@router.post("/tools/rule_engine", response_model=AgentResponse, summary="Rule Engine tool", tags=["Tools"])
async def rule_engine(request: ToolRequest) -> AgentResponse:
    """
    Execute Rule Engine tool

    - **context_lock_id**: Required for state isolation
    - **input_data**: phase, implementation artifacts
    - **mode**: Execution mode

    Returns rule check results with violations
    """
    logger.info(f"Rule engine check: {request.context_lock_id}")

    # Will be implemented via MCP client when available
    return AgentResponse(
        task_id=generate_task_id(),
        actor="rule_engine",
        timestamp=get_timestamp(),
        section="[RULE_ENGINE]",
        payload={
            "message": "Rule engine check executed",
            "violations": []
        },
        error=None
    )


@router.post("/tools/incremental_build", response_model=AgentResponse, summary="Incremental Build tool", tags=["Tools"])
async def incremental_build(request: ToolRequest) -> AgentResponse:
    """
    Execute Incremental Build tool

    - **context_lock_id**: Required for state isolation
    - **input_data**: changes, diff level
    - **mode**: Execution mode

    Returns diff generation and build application results
    """
    logger.info(f"Incremental build: {request.context_lock_id}")

    # Will be implemented via MCP client when available
    return AgentResponse(
        task_id=generate_task_id(),
        actor="incremental_build",
        timestamp=get_timestamp(),
        section="[INCREMENTAL_BUILD]",
        payload={
            "message": "Incremental build executed",
            "changes_applied": 0
        },
        error=None
    )


@router.post("/tools/audit_log", response_model=AgentResponse, summary="Audit Log tool", tags=["Tools"])
async def audit_log(request: ToolRequest) -> AgentResponse:
    """
    Execute Audit Log tool

    - **context_lock_id**: Required for state isolation
    - **input_data**: operation (write/query), log data
    - **mode**: Execution mode

    Returns audit log operation results
    """
    logger.info(f"Audit log operation: {request.context_lock_id}")

    # Will be implemented via MCP client when available
    return AgentResponse(
        task_id=generate_task_id(),
        actor="audit_log",
        timestamp=get_timestamp(),
        section="[AUDIT_LOG]",
        payload={
            "message": "Audit log operation executed",
            "log_id": generate_task_id()
        },
        error=None
    )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health", response_model=HealthResponse, summary="Health check", tags=["System"])
async def health_check() -> HealthResponse:
    """
    Check API health status

    Returns API status, version, and available agents
    """
    return HealthResponse(
        status="healthy",
        version="3.0.0",
        integration="jcode-v3",
        agents=[
            AGENT_ANALYST,
            AGENT_PLANNER,
            AGENT_IMPLEMENTER,
            AGENT_REVIEWER,
            AGENT_TESTER,
            AGENT_CONDUCTOR
        ]
    )


# Export
__all__ = [
    "router",
    "AGENT_ANALYST",
    "AGENT_PLANNER",
    "AGENT_IMPLEMENTER",
    "AGENT_REVIEWER",
    "AGENT_TESTER",
    "AGENT_CONDUCTOR",
    "AgentRequest",
    "ToolRequest",
    "AgentResponse",
    "ErrorResponse",
    "HealthResponse"
]
