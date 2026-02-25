"""
Rule Engine for JCode Agent System

Implements YAML rule parsing, execution, violation handling, and soft hooks
based on governance/RULE_ENGINE.md specification.
"""

import re
import yaml
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, UTC

class Priority(str, Enum):
    """Rule priority levels mapping to violation handlers"""
    P0 = "TERMINATE"
    P1 = "QUICK_FIX"
    P2 = "LOG_ONLY"
    P3 = "SOFT_HOOK"


class Severity(str, Enum):
    """Rule severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# Priority mapping: Severity -> Priority
SEVERITY_TO_PRIORITY = {
    Severity.CRITICAL: Priority.P0,
    Severity.HIGH: Priority.P1,
    Severity.MEDIUM: Priority.P2,
    Severity.LOW: Priority.P3,
}


@dataclass
class RuleMatch:
    """Rule matching conditions"""
    pattern: str
    file_patterns: List[str] = field(default_factory=list)
    context_filter: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SoftHooksConfig:
    """Soft hooks configuration"""
    enabled: bool = True
    can_be_ignored: bool = True
    notify_on_ignore: bool = False
    priority_boost_phase: Optional[str] = None
    interceptors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Rule:
    """Rule definition"""
    id: str
    version: str
    severity: str
    category: str
    phase: str
    handler: str
    match: RuleMatch
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    soft_hooks: Optional[SoftHooksConfig] = None

    @property
    def priority(self) -> Priority:
        """Get priority from severity"""
        return SEVERITY_TO_PRIORITY.get(Severity(self.severity), Priority.P2)


@dataclass
class ViolationResult:
    """Result of rule violation check"""
    violated: bool
    rule_id: str
    handler: str
    priority: Priority
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
@dataclass
class SoftHookState:
    """State tracking for soft hooks"""
    rule_id: str
    ignore_count: int = 0
    last_triggered: Optional[str] = None
    upgraded: bool = False
    upgrade_timestamp: Optional[str] = None


class RuleEngineError(Exception):
    """Base exception for rule engine errors"""
    pass


class RuleParseError(RuleEngineError):
    """Raised when rule parsing fails"""
    pass


class RuleExecutionError(RuleEngineError):
    """Raised when rule execution fails"""
    pass


class RuleEngine:
    """
    YAML Rule Execution Engine

    Implements rule parsing, execution, violation handling, and soft hooks
    based on governance/RULE_ENGINE.md specification.
    """

    # Default priority mapping
    PRIORITY_MAPPING = {
        Priority.P0: {
            "action": "TERMINATE",
            "notify_human": True,
            "rollback": True,
            "iteration_penalty": "+MAX"
        },
        Priority.P1: {
            "action": "QUICK_FIX",
            "notify_human": False,
            "rollback": False,
            "iteration_penalty": "+0"
        },
        Priority.P2: {
            "action": "LOG_ONLY",
            "notify_human": False,
            "rollback": False,
            "iteration_penalty": "+0"
        },
        Priority.P3: {
            "action": "SOFT_HOOK",
            "notify_human": False,
            "rollback": False,
            "iteration_penalty": "+0"
        }
    }

    # Allowed phases for rule execution
    ALLOWED_PHASES = ["ANALYSIS", "TASKS", "IMPLEMENTATION", "REVIEW", "TEST"]

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize RuleEngine

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.rules: Dict[str, Rule] = {}
        self.soft_hooks_state: Dict[str, SoftHookState] = {}
        self.compiled_patterns: Dict[str, re.Pattern] = {}

    def parse_yaml(self, yaml_content: str) -> Dict[str, Rule]:
        """
        Parse YAML rule definitions

        Args:
            yaml_content: YAML string containing rule definitions

        Returns:
            Dictionary of rule_id -> Rule objects

        Raises:
            RuleParseError: If YAML parsing fails
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise RuleParseError(f"Failed to parse YAML: {e}")

        if not data or not isinstance(data, dict):
            raise RuleParseError("Invalid YAML structure: expected dict")

        rules = {}

        # Handle single rule
        if "rule" in data:
            rule = self._parse_single_rule(data["rule"])
            rules[rule.id] = rule
        # Handle multiple rules
        elif "rules" in data:
            for rule_data in data["rules"]:
                rule = self._parse_single_rule(rule_data)
                rules[rule.id] = rule

        return rules

    def _parse_single_rule(self, rule_data: Dict) -> Rule:
        """Parse a single rule definition"""
        try:
            # Parse match section
            match_data = rule_data.get("match", {})
            match = RuleMatch(
                pattern=match_data.get("pattern", ""),
                file_patterns=match_data.get("file_patterns", []),
                context_filter=match_data.get("context_filter", {})
            )

            # Parse soft hooks if present
            soft_hooks = None
            if "soft_hooks" in rule_data:
                soft_hooks_data = rule_data["soft_hooks"]
                soft_hooks = SoftHooksConfig(
                    enabled=soft_hooks_data.get("enabled", True),
                    can_be_ignored=soft_hooks_data.get("can_be_ignored", True),
                    notify_on_ignore=soft_hooks_data.get("notify_on_ignore", False),
                    priority_boost_phase=soft_hooks_data.get("priority_boost_phase"),
                    interceptors=soft_hooks_data.get("interceptors", [])
                )

            return Rule(
                id=rule_data.get("id", ""),
                version=rule_data.get("version", "1.0.0"),
                severity=rule_data.get("severity", "MEDIUM"),
                category=rule_data.get("category", "general"),
                phase=rule_data.get("phase", "IMPLEMENTATION"),
                handler=rule_data.get("handler", "LOG_ONLY"),
                match=match,
                message=rule_data.get("message", ""),
                metadata=rule_data.get("metadata", {}),
                soft_hooks=soft_hooks
            )
        except Exception as e:
            raise RuleParseError(f"Failed to parse rule: {e}")

    def register_rule(self, rule: Rule) -> None:
        """
        Register a rule to the engine

        Args:
            rule: Rule object to register
        """
        self.rules[rule.id] = rule

        # Compile pattern for efficient matching
        try:
            self.compiled_patterns[rule.id] = re.compile(rule.match.pattern)
        except re.error as e:
            raise RuleParseError(f"Invalid regex pattern in rule {rule.id}: {e}")

        # Initialize soft hooks state if applicable
        if rule.soft_hooks:
            self.soft_hooks_state[rule.id] = SoftHookState(rule_id=rule.id)

    def execute(self, rule: Dict, context: Dict) -> ViolationResult:
        """
        Execute a rule against context

        Args:
            rule: Rule definition (as dict or Rule object)
            context: Execution context containing code, file, phase, etc.

        Returns:
            ViolationResult indicating if rule was violated
        """
        # Convert dict to Rule if necessary
        if isinstance(rule, dict):
            rule_obj = Rule(
                id=rule.get("id", ""),
                version=rule.get("version", "1.0.0"),
                severity=rule.get("severity", "MEDIUM"),
                category=rule.get("category", "general"),
                phase=rule.get("phase", "IMPLEMENTATION"),
                handler=rule.get("handler", "LOG_ONLY"),
                match=RuleMatch(
                    pattern=rule.get("match", {}).get("pattern", ""),
                    file_patterns=rule.get("match", {}).get("file_patterns", []),
                    context_filter=rule.get("match", {}).get("context_filter", {})
                ),
                message=rule.get("message", ""),
                metadata=rule.get("metadata", {})
            )
        else:
            rule_obj = rule

        # Check if phase allows rule execution
        phase = context.get("phase", "")
        if phase and phase not in self.ALLOWED_PHASES:
            return ViolationResult(
                violated=False,
                rule_id=rule_obj.id,
                handler=rule_obj.handler,
                priority=rule_obj.priority,
                message=f"Phase {phase} not allowed for this rule",
                context=context
            )

        # Check context filter
        if not self._check_context_filter(rule_obj, context):
            return ViolationResult(
                violated=False,
                rule_id=rule_obj.id,
                handler=rule_obj.handler,
                priority=rule_obj.priority,
                message="Context filter does not match",
                context=context
            )

        # Check file pattern
        if "file" in context:
            file_path = context["file"]
            if not self._check_file_pattern(rule_obj, file_path):
                return ViolationResult(
                    violated=False,
                    rule_id=rule_obj.id,
                    handler=rule_obj.handler,
                    priority=rule_obj.priority,
                    message=f"File pattern does not match: {file_path}",
                    context=context
                )

        # Check if code matches pattern
        code = context.get("code", "")
        violated = self.check_violation(rule_obj, context)

        if violated:
            return self._create_violation_result(rule_obj, context)
        else:
            return ViolationResult(
                violated=False,
                rule_id=rule_obj.id,
                handler=rule_obj.handler,
                priority=rule_obj.priority,
                message="Rule passed",
                context=context
            )

    def check_violation(self, rule: Rule, context: Dict) -> bool:
        """
        Check if rule is violated

        Args:
            rule: Rule object
            context: Execution context

        Returns:
            True if violation detected, False otherwise
        """
        code = context.get("code", "")

        # Get or compile pattern
        if rule.id in self.compiled_patterns:
            pattern = self.compiled_patterns[rule.id]
        else:
            try:
                pattern = re.compile(rule.match.pattern)
                self.compiled_patterns[rule.id] = pattern
            except re.error:
                return False

        # Check if pattern matches
        match = pattern.search(code)
        return match is not None

    def handle_violation(self, rule: Rule, context: Dict, violation: ViolationResult) -> None:
        """
        Handle a rule violation based on priority

        Args:
            rule: Rule that was violated
            context: Execution context
            violation: Violation result

        Raises:
            RuleExecutionError: For P0 violations (TERMINATE)
        """
        priority = violation.priority
        handler = violation.handler

        if priority == Priority.P0:
            self._handle_terminate(rule, context, violation)
        elif priority == Priority.P1:
            self._handle_quick_fix(rule, context, violation)
        elif priority == Priority.P2:
            self._handle_log_only(rule, context, violation)
        elif priority == Priority.P3:
            self._handle_soft_hook(rule, context, violation)
        else:
            raise RuleExecutionError(f"Unknown priority: {priority}")

    def _handle_terminate(self, rule: Rule, context: Dict, violation: ViolationResult) -> None:
        """
        Handle P0 violation - TERMINATE

        Terminates execution, notifies human, logs audit, triggers rollback
        """
        raise RuleExecutionError(
            f"TERMINATE: {rule.id} - {violation.message}\n"
            f"Location: {violation.location}\n"
            f"Action: Immediate termination and rollback required"
        )

    def _handle_quick_fix(self, rule: Rule, context: Dict, violation: ViolationResult) -> None:
        """
        Handle P1 violation - QUICK_FIX

        Marks for quick fix via QUICK_FIX_CHANNEL without iteration penalty
        """
        # In a full implementation, this would trigger the quick fix channel
        # For now, we just mark the violation as requiring quick fix
        violation.handler = "QUICK_FIX"

    def _handle_log_only(self, rule: Rule, context: Dict, violation: ViolationResult) -> None:
        """
        Handle P2 violation - LOG_ONLY

        Logs violation to audit log without interrupting task
        """
        # In a full implementation, this would write to audit/rule_violations.jsonl
        # For now, we just mark the handler
        violation.handler = "LOG_ONLY"

    def _handle_soft_hook(self, rule: Rule, context: Dict, violation: ViolationResult) -> None:
        """
        Handle P3 violation - SOFT_HOOK

        Provides optional warning that can be ignored
        Tracks ignore count and upgrades to higher priority if threshold exceeded
        """
        if not rule.soft_hooks or not rule.soft_hooks.enabled:
            violation.handler = "LOG_ONLY"
            return

        # Get or create soft hook state
        if rule.id not in self.soft_hooks_state:
            self.soft_hooks_state[rule.id] = SoftHookState(rule_id=rule.id)

        state = self.soft_hooks_state[rule.id]
        state.last_triggered = datetime.now(UTC).isoformat()
        for interceptor in rule.soft_hooks.interceptors:
            if interceptor.get("type") == "referrer":
                threshold = interceptor.get("config", {}).get("threshold", 3)
                if state.ignore_count >= threshold and not state.upgraded:
                    # Upgrade to P2
                    state.upgraded = True
                    state.upgrade_timestamp = datetime.now(UTC).isoformat()
                    violation.handler = "LOG_ONLY"
                    violation.message = f"[UPGRADED] {violation.message}"
                    return

        violation.handler = "SOFT_HOOK"

    def increment_soft_hook_ignore(self, rule_id: str) -> None:
        """
        Increment ignore count for a soft hook

        Args:
            rule_id: ID of the rule to increment
        """
        if rule_id in self.soft_hooks_state:
            self.soft_hooks_state[rule_id].ignore_count += 1

    def _check_context_filter(self, rule: Rule, context: Dict) -> bool:
        """Check if context matches rule's context filter"""
        filter_dict = rule.match.context_filter
        if not filter_dict:
            return True

        for key, value in filter_dict.items():
            if key not in context:
                return False
            if context[key] != value:
                return False

        return True

    def _check_file_pattern(self, rule: Rule, file_path: str) -> bool:
        """Check if file matches rule's file patterns"""
        file_patterns = rule.match.file_patterns
        if not file_patterns:
            return True

        for pattern in file_patterns:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            if re.search(regex_pattern, file_path):
                return True

        return False

    def _create_violation_result(self, rule: Rule, context: Dict) -> ViolationResult:
        """Create violation result from rule and context"""
        code = context.get("code", "")
        file_path = context.get("file", "")

        # Try to find match location
        location = file_path
        if rule.id in self.compiled_patterns:
            match = self.compiled_patterns[rule.id].search(code)
            if match:
                line_num = code[:match.start()].count('\n') + 1
                if file_path:
                    location = f"{file_path}:{line_num}"
                else:
                    location = f"line:{line_num}"

        return ViolationResult(
            violated=True,
            rule_id=rule.id,
            handler=rule.handler,
            priority=rule.priority,
            message=rule.message,
            location=location,
            suggestion=rule.metadata.get("suggestion"),
            context=context
        )

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """
        Get a registered rule by ID

        Args:
            rule_id: Rule ID

        Returns:
            Rule object or None if not found
        """
        return self.rules.get(rule_id)

    def get_rules_by_phase(self, phase: str) -> List[Rule]:
        """
        Get all rules for a specific phase

        Args:
            phase: Phase name (ANALYSIS, TASKS, IMPLEMENTATION, REVIEW, TEST)

        Returns:
            List of rules for the phase
        """
        return [rule for rule in self.rules.values() if rule.phase == phase]

    def get_soft_hooks_state(self, rule_id: str) -> Optional[SoftHookState]:
        """
        Get soft hook state for a rule

        Args:
            rule_id: Rule ID

        Returns:
            SoftHookState object or None if not found
        """
        return self.soft_hooks_state.get(rule_id)
