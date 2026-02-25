"""
JCode Switch Manager - 4-Level Enablement Mechanism

Implements the 4-level switch hierarchy:
1. Global Switch (enabled/disabled)
2. Mode Switch (full/light/safe/fast/custom)
3. Agent-Level Switch (per-agent enablement)
4. Rule-Level Switch (per-rule configuration)

Supports priority resolution: session > project > user > OMO > default
Implements forced enablement for sensitive files/operations.

Reference: governance/JCODE_SWITCH.md
"""

import fnmatch
import glob
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


# Default configuration
DEFAULT_CONFIG = {
    "enabled": True,
    "mode": "full",
    "agents": {
        "analyst": True,
        "planner": True,
        "implementer": True,
        "reviewer": True,
        "tester": True,
        "conductor": True
    },
    "rules": {
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
    "max_iterations": 5,
    "forced_enable": {
        "file_patterns": [
            "**/config/**",
            "**/*secret*",
            "**/*.env",
            "**/secrets.yaml",
            "**/credentials.json"
        ],
        "operations": [
            "delete_file",
            "modify_permission",
            "database_migration",
            "deploy_production"
        ]
    },
    "audit": {
        "log_switch_changes": True,
        "log_forced_enable": True,
        "retention_days": 90
    },
    "priority": [
        "session_command",
        "project_config",
        "user_config",
        "omo_config",
        "default"
    ]
}

# Valid modes
VALID_MODES = ["full", "light", "safe", "fast", "custom"]

# Required agents that cannot all be disabled simultaneously
REQUIRED_AGENTS = ["analyst", "planner", "implementer", "conductor"]

# Required fallback when reviewer and tester are disabled
REQUIRED_FALLBACK_AGENT = "conductor"


@dataclass
class SwitchManager:
    """
    JCode 4-Level Switch Manager

    Manages the 4-level switch hierarchy with priority resolution and forced enablement.
    """

    config_path: str
    _config: Dict[str, Any] = field(default_factory=dict)
    _session_overrides: Dict[str, Any] = field(default_factory=dict)
    _project_config: Optional[Dict[str, Any]] = None
    _user_config: Optional[Dict[str, Any]] = None
    _omo_config: Optional[Dict[str, Any]] = None
    _project_root: Path = field(init=False)

    def __post_init__(self):
        """Initialize switch manager with config loading."""
        self._project_root = Path(self.config_path).parent.parent
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file with priority resolution.

        Priority order: session > project > user > OMO > default

        Returns:
            Merged configuration dictionary
        """
        # Start with default config
        merged_config = DEFAULT_CONFIG.copy()

        # Load and merge configs in priority order (lowest to highest)
        self._omo_config = self._load_config_file(self._project_root / ".omo" / "config.yaml")
        self._user_config = self._load_config_file(Path.home() / ".jcode" / "config.yaml")
        self._project_config = self._load_config_file(self._project_root / ".jcode" / "config.yaml")
        self._config = self._load_config_file(Path(self.config_path))

        # Merge configs in priority order
        merged_config = self._merge_configs(merged_config, self._omo_config)
        merged_config = self._merge_configs(merged_config, self._user_config)
        merged_config = self._merge_configs(merged_config, self._project_config)
        merged_config = self._merge_configs(merged_config, self._config)

        # Apply session overrides (highest priority)
        if self._session_overrides:
            merged_config = self._merge_configs(merged_config, {"jcode": self._session_overrides})

        # Extract jcode section if exists
        if "jcode" in merged_config:
            merged_config = merged_config["jcode"]

        # Validate configuration
        self._validate_config(merged_config)

        self._config = merged_config
        return merged_config

    def get(self, level: str, key: str = None) -> Any:
        """
        Get configuration value for a specific level.

        Args:
            level: Switch level ("global", "mode", "agent", "rule")
            key: Specific key within level (e.g., "analyst" for agent level,
                  "R001_no_skip_review" for rule level)

        Returns:
            Configuration value(s) for the requested level

        Raises:
            ValueError: If level is invalid
            KeyError: If key is invalid for the level
        """
        config = self._get_effective_config()

        if level == "global":
            if key:
                if key == "enabled":
                    return config.get("enabled", True)
                # Allow getting other top-level config values
                return config.get(key)
            return config.get("enabled", True)

        elif level == "mode":
            if key:
                raise KeyError("Mode level does not support keys")
            return config.get("mode", "full")

        elif level == "agent":
            agents = config.get("agents", {})
            if key:
                if key not in agents:
                    raise KeyError(f"Invalid agent: {key}")
                return agents.get(key, True)
            return agents

        elif level == "rule":
            rules = config.get("rules", {})
            if key:
                # Search for rule in all categories
                for category in rules.values():
                    if key in category:
                        return category[key]
                raise KeyError(f"Invalid rule: {key}")
            return rules

        else:
            raise ValueError(f"Invalid level: {level}. Must be one of: global, mode, agent, rule")

    def set(self, level: str, key: str, value: Any) -> None:
        """
        Set configuration value for a specific level (session override).

        Args:
            level: Switch level ("global", "mode", "agent", "rule")
            key: Specific key within level
            value: Value to set

        Raises:
            ValueError: If level or key is invalid
            RuntimeError: If validation fails
        """
        # Update session overrides
        if level == "global":
            if key != "enabled":
                raise ValueError(f"Invalid global key: {key}")
            self._session_overrides["enabled"] = value

        elif level == "mode":
            if value not in VALID_MODES:
                raise ValueError(f"Invalid mode: {value}. Must be one of: {VALID_MODES}")
            self._session_overrides["mode"] = value

        elif level == "agent":
            if key not in DEFAULT_CONFIG["agents"]:
                raise ValueError(f"Invalid agent: {key}")
            if "agents" not in self._session_overrides:
                self._session_overrides["agents"] = {}
            self._session_overrides["agents"][key] = value

            # Validate agent configuration
            temp_config = self._get_effective_config()
            if "agents" not in temp_config:
                temp_config["agents"] = {}
            temp_config["agents"][key] = value
            self._validate_agents(temp_config["agents"])

        elif level == "rule":
            # Find which category the rule belongs to
            category = None
            for cat, rules in DEFAULT_CONFIG["rules"].items():
                if key in rules:
                    category = cat
                    break

            if category is None:
                raise ValueError(f"Invalid rule: {key}")

            if "rules" not in self._session_overrides:
                self._session_overrides["rules"] = {}
            if category not in self._session_overrides["rules"]:
                self._session_overrides["rules"][category] = {}
            self._session_overrides["rules"][category][key] = value

        else:
            raise ValueError(f"Invalid level: {level}. Must be one of: global, mode, agent, rule")

        # Reload config to apply changes
        self.load_config()

    def get_priority(self, current: Dict[str, Any], fallbacks: List[Dict[str, Any]]) -> Any:
        """
        Resolve configuration value using priority fallback chain.

        Args:
            current: Current configuration dict
            fallbacks: List of fallback configurations (lower priority)

        Returns:
            First non-None value found in priority order
        """
        # Check current first
        for key, value in current.items():
            if value is not None:
                return value

        # Check fallbacks in order
        for fallback in fallbacks:
            for key, value in fallback.items():
                if value is not None:
                    return value

        return None

    def is_forced_enable(self, file_path: Optional[str] = None, operation: Optional[str] = None) -> bool:
        """
        Check if JCode should be forced enabled for a file or operation.

        Args:
            file_path: Path to file being operated on
            operation: Operation type (e.g., "delete_file", "modify_permission")

        Returns:
            True if JCode should be forced enabled
        """
        forced_enable = self._config.get("forced_enable", {})
        file_patterns = forced_enable.get("file_patterns", [])
        operations = forced_enable.get("operations", [])

        # Check file pattern match
        if file_path:
            for pattern in file_patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    return True

        # Check operation match
        if operation and operation in operations:
            return True

        return False

    def should_enable_jcode(self, file_path: Optional[str] = None, operation: Optional[str] = None) -> bool:
        """
        Determine if JCode should be enabled (considering forced enablement).

        Args:
            file_path: Path to file being operated on
            operation: Operation type

        Returns:
            True if JCode should be enabled
        """
        # Check global switch
        if self.get("global", "enabled"):
            return True

        # Check forced enablement
        if self.is_forced_enable(file_path, operation):
            return True

        return False

    def clear_session_overrides(self) -> None:
        """Clear all session-level overrides."""
        self._session_overrides.clear()
        self.load_config()

    def _get_effective_config(self) -> Dict[str, Any]:
        """Get the effective configuration with all overrides applied."""
        config = self._config.copy()
        if self._session_overrides:
            config = self._merge_configs(config, {"jcode": self._session_overrides})
            if "jcode" in config:
                config = config["jcode"]
        return config

    def _load_config_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """
        Load configuration from a YAML file.

        Args:
            path: Path to configuration file

        Returns:
            Configuration dict or None if file doesn't exist
        """
        if not path.exists():
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data is None:
                    return None
                return data
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            return None

    def _merge_configs(self, base: Dict[str, Any], override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge two configuration dicts (override takes precedence).

        Args:
            base: Base configuration
            override: Override configuration

        Returns:
            Merged configuration
        """
        if override is None:
            return base

        result = base.copy()

        for key, value in override.items():
            if key == "jcode" and isinstance(value, dict):
                # Extract jcode section and merge
                result = self._merge_configs(result, value)
            elif key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._merge_configs(result[key], value)
            else:
                # Override with new value
                result[key] = value

        return result

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration according to constraints.

        Args:
            config: Configuration to validate

        Raises:
            RuntimeError: If validation fails
        """
        # Validate mode
        mode = config.get("mode", "full")
        if mode not in VALID_MODES:
            raise RuntimeError(f"Invalid mode: {mode}. Must be one of: {VALID_MODES}")

        # Validate agents
        agents = config.get("agents", {})
        self._validate_agents(agents)

        # Validate max_iterations
        max_iterations = config.get("max_iterations", 5)
        if not isinstance(max_iterations, int) or max_iterations < 1:
            raise RuntimeError(f"Invalid max_iterations: {max_iterations}. Must be >= 1")

    def _validate_agents(self, agents: Dict[str, bool]) -> None:
        """
        Validate agent configuration according to constraints.

        Constraints:
        1. Required agents cannot all be disabled simultaneously
        2. If reviewer and tester are both disabled, conductor must be enabled

        Args:
            agents: Agent configuration dict

        Raises:
            RuntimeError: If validation fails
        """
        # Check that not all required agents are disabled
        required_enabled = [agents.get(agent, True) for agent in REQUIRED_AGENTS]
        if not any(required_enabled):
            raise RuntimeError(
                f"Cannot disable all required agents: {', '.join(REQUIRED_AGENTS)}. "
                "At least one must be enabled to maintain workflow integrity."
            )

        # Check conductor fallback when reviewer and tester are disabled
        if (not agents.get("reviewer", True) and
            not agents.get("tester", True) and
            not agents.get("conductor", True)):
            raise RuntimeError(
                "When reviewer and tester are both disabled, conductor must be enabled "
                "as a fallback mechanism."
            )

    @property
    def enabled(self) -> bool:
        """Shortcut property to check if JCode is globally enabled."""
        return self.get("global", "enabled")

    @property
    def mode(self) -> str:
        """Shortcut property to get current mode."""
        return self.get("mode")

    def __repr__(self) -> str:
        """String representation of switch manager state."""
        return (
            f"SwitchManager(enabled={self.enabled}, mode='{self.mode}', "
            f"config_path='{self.config_path}')"
        )


# Convenience function for quick initialization
def create_switch_manager(config_path: str = None) -> SwitchManager:
    """
    Create a SwitchManager instance with default config path.

    Args:
        config_path: Path to config file (defaults to config/jcode_config.yaml)

    Returns:
        Initialized SwitchManager instance
    """
    if config_path is None:
        # Try to find config in standard locations
        project_root = Path.cwd()
        possible_paths = [
            project_root / "config" / "jcode_config.yaml",
            project_root / ".jcode" / "config.yaml",
        ]

        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break
        else:
            config_path = str(project_root / "config" / "jcode_config.yaml")

    return SwitchManager(config_path=config_path)
