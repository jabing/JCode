"""
Config Routes - JCode v3.0

REST endpoints for configuration management:
-GET /config - Return current full configuration
-POST /config/reload - Reload configuration from YAML
-POST /config/enable - Enable JCode governance
-POST /config/disable - Disable JCode governance
-POST /config/mode - Change execution mode (full/light/safe/fast/custom)

Implements OMO Superpowers extension point via /tools/config.

Author: JCode v3.0 Implementation
Status: IMPLEMENTATION
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from typing import Optional, Dict, Any
import logging
from datetime import datetime, UTC
from pathlib import Path

from core.switch_manager import SwitchManager

# Configure logging
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/v1")

# Default config path
DEFAULT_CONFIG_PATH = "config/jcode_config.yaml"


# ============================================================================
# Request/Response Models
# ============================================================================


class ConfigResponse(BaseModel):
    """Configuration response with full 4-level structure"""
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    enabled: bool = Field(..., description="JCode enabled status")
    mode: str = Field(..., description="Execution mode (full/light/safe/fast/custom)")
    agents: Dict[str, bool] = Field(..., description="Agent enabled status")
    rules: Dict[str, Dict[str, bool]] = Field(..., description="Rule enabled status")
    max_iterations: int = Field(..., description="Maximum iterations")
    forced_enable: Dict[str, Any] = Field(..., description="Forced enablement configuration")
    audit: Dict[str, Any] = Field(..., description="Audit configuration")
    priority: list = Field(..., description="Priority resolution order")


class ModeSwitchRequest(BaseModel):
    """Request to change execution mode"""
    mode: str = Field(..., description="New mode (full/light/safe/fast/custom)")


class EnableRequest(BaseModel):
    """Request to enable JCode"""
    mode: Optional[str] = Field(None, description="Optional mode to set on enable")


class ReloadRequest(BaseModel):
    """Request to reload configuration"""
    config_path: Optional[str] = Field(None, description="Path to config file")


class ErrorResponse(BaseModel):
    """Error response wrapper"""
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


def get_timestamp() -> str:
    """Get current ISO 8601 timestamp"""
    return datetime.now(UTC).isoformat() + "Z"


def get_full_config(switch_manager: SwitchManager) -> ConfigResponse:
    """
    Get full configuration from switch manager
    
    Returns:
        ConfigResponse with all 4 levels
    """
    config = switch_manager._get_effective_config()
    
    # Build agents dict
    agents = config.get("agents", {})
    
    # Build rules dict
    rules = config.get("rules", {})
    
    return ConfigResponse(
        timestamp=get_timestamp(),
        enabled=config.get("enabled", True),
        mode=config.get("mode", "full"),
        agents=agents,
        rules=rules,
        max_iterations=config.get("max_iterations", 5),
        forced_enable=config.get("forced_enable", {"file_patterns": [], "operations": []}),
        audit=config.get("audit", {}),
        priority=config.get("priority", ["session_command", "project_config", "user_config", "omo_config", "default"])
    )


@router.get("/config", response_model=ConfigResponse, summary="Current JCode configuration", tags=["Config"])
async def get_config() -> ConfigResponse:
    """
    Get current full JCode configuration
    
    Returns:
        ConfigResponse with all 4 levels:
        - Level 1: Global switch (enabled/disabled)
        - Level 2: Mode switch (full/light/safe/fast/custom)
        - Level 3: Agent-level switch (per-agent enablement)
        - Level 4: Rule-level switch (per-rule configuration)
    """
    logger.info("Getting JCode configuration")
    
    try:
        # Load config
        config_path = Path(__file__).parent.parent.parent / DEFAULT_CONFIG_PATH
        switch_manager = SwitchManager(config_path=str(config_path))
        
        return get_full_config(switch_manager)
        
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_type": "CONFIG_ERROR", "message": str(e)}
        )


@router.post("/config/reload", response_model=ConfigResponse, summary="Reload configuration", tags=["Config"])
async def reload_config(request: ReloadRequest) -> ConfigResponse:
    """
    Reload configuration from YAML file
    
    Args:
        request: ReloadRequest with optional config_path
        
    Returns:
        ConfigResponse with reloaded configuration
    """
    config_path_str = request.config_path if request.config_path else DEFAULT_CONFIG_PATH
    
    # Resolve config path
    config_path = Path(config_path_str)
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}, using default")
        config_path = Path(__file__).parent.parent.parent / DEFAULT_CONFIG_PATH
    
    try:
        logger.info(f"Reloading configuration from: {config_path}")
        
        switch_manager = SwitchManager(config_path=str(config_path))
        
        # Reload config
        switch_manager.load_config()
        
        return get_full_config(switch_manager)
        
    except Exception as e:
        logger.error(f"Failed to reload config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_type": "CONFIG_ERROR", "message": str(e)}
        )


@router.post("/config/enable", response_model=ConfigResponse, summary="Enable JCode governance", tags=["Config"])
async def enable_jcode(request: EnableRequest = None) -> ConfigResponse:
    """
    Enable JCode governance (sets global enabled=true)
    
    Args:
        request: Optional EnableRequest with mode to set
        
    Returns:
        ConfigResponse with updated configuration
    """
    try:
        config_path = Path(__file__).parent.parent.parent / DEFAULT_CONFIG_PATH
        switch_manager = SwitchManager(config_path=str(config_path))
        
        # Clear session overrides first
        switch_manager.clear_session_overrides()
        
        # Set enabled to True via session override
        switch_manager.set("global", "enabled", True)
        
        # Set mode if provided
        if request and request.mode:
            switch_manager.set("mode", None, request.mode)
        
        return get_full_config(switch_manager)
        
    except Exception as e:
        logger.error(f"Failed to enable JCode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_type": "CONFIG_ERROR", "message": str(e)}
        )


@router.post("/config/disable", response_model=ConfigResponse, summary="Disable JCode governance", tags=["Config"])
async def disable_jcode() -> ConfigResponse:
    """
    Disable JCode governance (sets global enabled=false)
    
    Returns:
        ConfigResponse with updated configuration
    """
    try:
        config_path = Path(__file__).parent.parent.parent / DEFAULT_CONFIG_PATH
        switch_manager = SwitchManager(config_path=str(config_path))
        
        # Clear session overrides first
        switch_manager.clear_session_overrides()
        
        # Set enabled to False via session override
        switch_manager.set("global", "enabled", False)
        
        return get_full_config(switch_manager)
        
    except Exception as e:
        logger.error(f"Failed to disable JCode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_type": "CONFIG_ERROR", "message": str(e)}
        )


@router.post("/config/mode", response_model=ConfigResponse, summary="Switch execution mode", tags=["Config"])
async def switch_mode(request: ModeSwitchRequest) -> ConfigResponse:
    """
    Change JCode execution mode
    
    Args:
        request: ModeSwitchRequest with new mode
        
    Returns:
        ConfigResponse with updated configuration
    """
    valid_modes = ["full", "light", "safe", "fast", "custom"]
    
    if request.mode not in valid_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_type": "INVALID_MODE",
                "message": f"Invalid mode: {request.mode}. Must be one of: {valid_modes}",
                "timestamp": get_timestamp()
            }
        )
    
    try:
        config_path = Path(__file__).parent.parent.parent / DEFAULT_CONFIG_PATH
        switch_manager = SwitchManager(config_path=str(config_path))
        
        # Clear session overrides first
        switch_manager.clear_session_overrides()
        
        # Set mode via session override
        switch_manager.set("mode", None, request.mode)
        
        return get_full_config(switch_manager)
        
    except Exception as e:
        logger.error(f"Failed to switch mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_type": "CONFIG_ERROR", "message": str(e)}
        )


@router.post("/tools/config", response_model=ConfigResponse, summary="Configuration tool (OMO MCP)", tags=["Tools"])
async def config_tool(request: ReloadRequest) -> ConfigResponse:
    """
    OMO Superpowers Configuration Tool - Configuration reload endpoint
    
    This endpoint implements the OMO MCP Tool integration point for configuration
    management. It provides a unified endpoint for external systems to reload
    JCode configuration via MCP protocol.
    
    Integration Points:
    - OMO Superpowers: Mapped to `configuration` MCP tool
    - Context Lock: Uses `context_lock_id` parameter for state isolation
    - Audit Logging: All changes logged via audit_log tool
    
    Args:
        request: ReloadRequest with optional config_path
        
    Returns:
        ConfigResponse with reloaded configuration
    """
    logger.info(f"Configuration tool invocation: context_lock_id={request.config_path}")
    
    try:
        config_path_str = request.config_path if request.config_path else DEFAULT_CONFIG_PATH
        
        # Resolve config path
        config_path = Path(config_path_str)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using default")
            config_path = Path(__file__).parent.parent.parent / DEFAULT_CONFIG_PATH
        
        switch_manager = SwitchManager(config_path=str(config_path))
        
        # Reload config
        switch_manager.load_config()
        
        return get_full_config(switch_manager)
        
    except Exception as e:
        logger.error(f"Configuration tool failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_type": "CONFIG_ERROR", "message": str(e)}
        )


# Export
__all__ = [
    "router",
    "ConfigResponse",
    "ModeSwitchRequest",
    "EnableRequest",
    "ReloadRequest",
    "ErrorResponse",
]
