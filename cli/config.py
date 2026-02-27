"""
JCode CLI Configuration Manager

Provides high-level configuration management functions for CLI commands.
Wraps the core SwitchManager to provide convenient methods for configuration
loading, validation, updates, and switch operations.

Reference:
    - governance/JCODE_SWITCH.md (4-level switch mechanism)
    - config/jcode_config.yaml (configuration structure)
    - core/switch_manager.py (SwitchManager API)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add parent directory to path to import from core module
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.switch_manager import (
    SwitchManager,
    create_switch_manager,
    DEFAULT_CONFIG,
    VALID_MODES,
    REQUIRED_AGENTS
)


class JCodeConfigManager:
    """
    High-level configuration manager for JCode CLI commands.

    Provides convenient methods for:
    - Loading configuration from YAML files
    - Validating configuration structure
    - Updating configuration values
    - Managing switch states (global, mode, agent, rule levels)

    The manager wraps the core SwitchManager and offers a CLI-friendly
    interface with better error messages and type hints.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to configuration file. If None, will search
                        standard locations (config/jcode_config.yaml, .jcode/config.yaml)
        """
        self.switch_manager = create_switch_manager(config_path)
        self.config_path = self.switch_manager.config_path

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file with priority resolution.

        Priority order: session > project > user > OMO > default

        Returns:
            Merged configuration dictionary
        """
        return self.switch_manager.load_config()

    def validate_config(self) -> bool:
        """
        Validate the current configuration structure.

        Validates:
        - Mode is valid (full/light/safe/fast/custom)
        - Agent configuration (required agents not all disabled)
        - Max iterations >= 1
        - Rule structure is correct

        Returns:
            True if configuration is valid

        Raises:
            RuntimeError: If validation fails
        """
        try:
            config = self.load_config()

            # Validate mode
            mode = config.get("mode", "full")
            if mode not in VALID_MODES:
                raise RuntimeError(
                    f"Invalid mode: {mode}. Must be one of: {', '.join(VALID_MODES)}"
                )

            # Validate agents
            agents = config.get("agents", {})
            self._validate_agents(agents)

            # Validate max_iterations
            max_iterations = config.get("max_iterations", 5)
            if not isinstance(max_iterations, int) or max_iterations < 1:
                raise RuntimeError(
                    f"Invalid max_iterations: {max_iterations}. Must be >= 1"
                )

            # Validate rules structure
            rules = config.get("rules", {})
            if not isinstance(rules, dict):
                raise RuntimeError("Rules must be a dictionary")

            for category, rule_dict in rules.items():
                if not isinstance(rule_dict, dict):
                    raise RuntimeError(f"Rules category '{category}' must be a dictionary")

            return True

        except Exception as e:
            raise RuntimeError(f"Configuration validation failed: {e}")

    def _validate_agents(self, agents: Dict[str, bool]) -> None:
        """
        Validate agent configuration.

        Constraints:
        1. Required agents cannot all be disabled simultaneously
        2. If reviewer and tester are both disabled, conductor must be enabled

        Args:
            agents: Agent configuration dictionary

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

    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.

        Supports updating:
        - Global switch (enabled)
        - Mode (mode)
        - Agent states (agents.{agent_name})
        - Rule states (rules.{category}.{rule_name})
        - Max iterations (max_iterations)

        Args:
            updates: Dictionary of configuration updates

        Raises:
            RuntimeError: If update validation fails
        """
        try:
            for key, value in updates.items():
                if key == "enabled":
                    self.set_switch("global", "enabled", value)

                elif key == "mode":
                    if value not in VALID_MODES:
                        raise RuntimeError(
                            f"Invalid mode: {value}. Must be one of: {', '.join(VALID_MODES)}"
                        )
                    self.set_switch("mode", None, value)

                elif key == "max_iterations":
                    if not isinstance(value, int) or value < 1:
                        raise RuntimeError(
                            f"Invalid max_iterations: {value}. Must be >= 1"
                        )
                    # Access internal config for max_iterations
                    self.switch_manager._config["max_iterations"] = value

                elif key == "agents":
                    if not isinstance(value, dict):
                        raise RuntimeError("Agents must be a dictionary")

                    for agent_name, agent_value in value.items():
                        if agent_name not in DEFAULT_CONFIG["agents"]:
                            raise RuntimeError(f"Invalid agent: {agent_name}")
                        self.set_switch("agent", agent_name, agent_value)

                elif key == "rules":
                    if not isinstance(value, dict):
                        raise RuntimeError("Rules must be a dictionary")

                    for category, rules in value.items():
                        if not isinstance(rules, dict):
                            raise RuntimeError(f"Rules category '{category}' must be a dictionary")

                        for rule_name, rule_value in rules.items():
                            self.set_switch("rule", rule_name, rule_value)

                else:
                    raise RuntimeError(f"Unknown configuration key: {key}")

        except Exception as e:
            raise RuntimeError(f"Failed to update configuration: {e}")

    def get_switch_status(self) -> Dict[str, Any]:
        """
        Get the current status of all switches.

        Returns:
            Dictionary containing:
            - enabled: Global enablement status
            - mode: Current mode
            - agents: Dictionary of agent states
            - rules: Dictionary of rule states
            - max_iterations: Maximum iterations
        """
        config = self.load_config()

        return {
            "enabled": config.get("enabled", True),
            "mode": config.get("mode", "full"),
            "agents": config.get("agents", DEFAULT_CONFIG["agents"]),
            "rules": config.get("rules", DEFAULT_CONFIG["rules"]),
            "max_iterations": config.get("max_iterations", 5)
        }

    def set_switch(self, level: str, key: Optional[str], value: Any) -> None:
        """
        Set a switch value at the specified level.

        Args:
            level: Switch level ("global", "mode", "agent", "rule")
            key: Specific key within level (e.g., "analyst" for agent level)
            value: Value to set

        Raises:
            RuntimeError: If switch validation fails
        """
        try:
            self.switch_manager.set(level, key, value)
        except (ValueError, KeyError) as e:
            raise RuntimeError(f"Failed to set switch: {e}")

    def toggle_switch(self, level: str, key: Optional[str] = None) -> bool:
        """
        Toggle a switch value.

        For "global" level, toggles the enabled status.
        For "agent" level, toggles the specified agent's enabled status.
        For "rule" level, toggles the specified rule's enabled status.
        "mode" level cannot be toggled (use set_switch instead).

        Args:
            level: Switch level ("global", "agent", "rule")
            key: Specific key within level (required for agent and rule levels)

        Returns:
            New value after toggling

        Raises:
            RuntimeError: If toggle operation fails
        """
        try:
            if level == "global":
                current = self.get_switch_status()["enabled"]
                new_value = not current
                self.set_switch("global", "enabled", new_value)
                return new_value

            elif level == "agent":
                if key is None:
                    raise RuntimeError("Agent toggle requires an agent name")
                current = self.switch_manager.get("agent", key)
                new_value = not current
                self.set_switch("agent", key, new_value)
                return new_value

            elif level == "rule":
                if key is None:
                    raise RuntimeError("Rule toggle requires a rule name")
                current = self.switch_manager.get("rule", key)
                new_value = not current
                self.set_switch("rule", key, new_value)
                return new_value

            else:
                raise RuntimeError(
                    f"Cannot toggle level '{level}'. Toggle only supports: global, agent, rule"
                )

        except Exception as e:
            raise RuntimeError(f"Failed to toggle switch: {e}")

    def is_enabled(self, file_path: Optional[str] = None, operation: Optional[str] = None) -> bool:
        """
        Check if JCode should be enabled.

        Considers both global switch and forced enablement scenarios.

        Args:
            file_path: Optional path to file being operated on
            operation: Optional operation type

        Returns:
            True if JCode should be enabled
        """
        return self.switch_manager.should_enable_jcode(file_path, operation)

    def get_agent_status(self, agent_name: str) -> bool:
        """
        Check if a specific agent is enabled.

        Args:
            agent_name: Name of the agent (e.g., "analyst", "planner")

        Returns:
            True if the agent is enabled

        Raises:
            RuntimeError: If agent name is invalid
        """
        try:
            return self.switch_manager.get("agent", agent_name)
        except KeyError:
            raise RuntimeError(f"Invalid agent: {agent_name}")

    def get_rule_status(self, rule_name: str) -> bool:
        """
        Check if a specific rule is enabled.

        Args:
            rule_name: Name of the rule (e.g., "R001_no_skip_review")

        Returns:
            True if the rule is enabled

        Raises:
            RuntimeError: If rule name is invalid
        """
        try:
            return self.switch_manager.get("rule", rule_name)
        except KeyError:
            raise RuntimeError(f"Invalid rule: {rule_name}")

    def clear_session_overrides(self) -> None:
        """Clear all session-level overrides."""
        self.switch_manager.clear_session_overrides()

    def get_config_path(self) -> str:
        """Get the path to the active configuration file."""
        return self.config_path

    def get_forced_enable_patterns(self) -> Dict[str, List[str]]:
        """
        Get the forced enablement patterns.

        Returns:
            Dictionary with 'file_patterns' and 'operations' lists
        """
        config = self.load_config()
        forced_enable = config.get("forced_enable", {})

        return {
            "file_patterns": forced_enable.get("file_patterns", []),
            "operations": forced_enable.get("operations", [])
        }

    def is_forced_enable(self, file_path: Optional[str] = None, operation: Optional[str] = None) -> bool:
        """
        Check if JCode should be forced enabled for a file or operation.

        Args:
            file_path: Path to file being operated on
            operation: Operation type (e.g., "delete_file", "modify_permission")

        Returns:
            True if JCode should be forced enabled
        """
        return self.switch_manager.is_forced_enable(file_path, operation)

    def format_status(self) -> str:
        """
        Format the current switch status as a human-readable string.

        Returns:
            Formatted status string
        """
        status = self.get_switch_status()

        lines = [
            "JCode Status:",
            f"  Enabled: {'✓' if status['enabled'] else '✗'}",
            f"  Mode: {status['mode']}",
            f"  Max Iterations: {status['max_iterations']}",
            "",
            "Agent Status:"
        ]

        for agent, enabled in status["agents"].items():
            lines.append(f"  {'✓' if enabled else '✗'} {agent.capitalize()}")

        lines.append("")
        lines.append("Rule Status:")

        for category, rules in status["rules"].items():
            lines.append(f"  {category.capitalize()}:")
            for rule, enabled in rules.items():
                lines.append(f"    {'✓' if enabled else '✗'} {rule}")

        return "\n".join(lines)


def create_config_manager(config_path: Optional[str] = None) -> JCodeConfigManager:
    """
    Create a JCodeConfigManager instance.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Initialized JCodeConfigManager instance
    """
    return JCodeConfigManager(config_path)


# Convenience function for quick status checks
def get_status(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick function to get current JCode status.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Dictionary with current status
    """
    manager = create_config_manager(config_path)
    return manager.get_switch_status()


def is_jcode_enabled(config_path: Optional[str] = None) -> bool:
    """
    Quick function to check if JCode is enabled.

    Args:
        config_path: Optional path to configuration file

    Returns:
        True if JCode is enabled
    """
    manager = create_config_manager(config_path)
    return manager.is_enabled()
