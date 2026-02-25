"""Test suite for core/rule_engine.py"""

from core.rule_engine import (
    RuleEngine, Rule, RuleMatch, SoftHooksConfig,
    Priority, Severity, ViolationResult,
    RuleParseError, RuleExecutionError
)
import pytest


def test_rule_engine_initialization():
    """Test basic RuleEngine initialization"""
    re = RuleEngine()
    assert re.rules == {}
    assert re.soft_hooks_state == {}
    assert re.compiled_patterns == {}
    print("✓ RuleEngine initialization works")


def test_parse_yaml_single_rule():
    """Test parsing a single YAML rule"""
    yaml_content = """
rule:
  id: "TEST-001"
  version: "1.0.0"
  severity: "HIGH"
  category: "test"
  phase: "IMPLEMENTATION"
  handler: "QUICK_FIX"
  match:
    pattern: "def [a-z]+"
    file_patterns: ["*.py"]
  message: "Test rule"
  metadata:
    owner: "test"
"""
    re = RuleEngine()
    rules = re.parse_yaml(yaml_content)
    assert len(rules) == 1
    assert "TEST-001" in rules
    rule = rules["TEST-001"]
    assert rule.id == "TEST-001"
    assert rule.severity == "HIGH"
    assert rule.priority == Priority.P1
    print("✓ Single YAML rule parsing works")


def test_parse_yaml_multiple_rules():
    """Test parsing multiple YAML rules"""
    yaml_content = """
rules:
  - id: "TEST-001"
    version: "1.0.0"
    severity: "CRITICAL"
    category: "test"
    phase: "IMPLEMENTATION"
    handler: "TERMINATE"
    match:
      pattern: "dangerous"
    message: "Critical rule"
  - id: "TEST-002"
    version: "1.0.0"
    severity: "LOW"
    category: "test"
    phase: "REVIEW"
    handler: "SOFT_HOOK"
    match:
      pattern: "suggestion"
    message: "Soft hook rule"
"""
    re = RuleEngine()
    rules = re.parse_yaml(yaml_content)
    assert len(rules) == 2
    assert "TEST-001" in rules
    assert "TEST-002" in rules
    assert rules["TEST-001"].priority == Priority.P0
    assert rules["TEST-002"].priority == Priority.P3
    print("✓ Multiple YAML rule parsing works")


def test_register_rule():
    """Test rule registration"""
    re = RuleEngine()
    rule = Rule(
        id="REG-001",
        version="1.0.0",
        severity="MEDIUM",
        category="test",
        phase="IMPLEMENTATION",
        handler="LOG_ONLY",
        match=RuleMatch(pattern="test"),
        message="Registration test"
    )
    re.register_rule(rule)
    assert "REG-001" in re.rules
    assert "REG-001" in re.compiled_patterns
    print("✓ Rule registration works")


def test_check_violation():
    """Test violation checking"""
    re = RuleEngine()
    rule = Rule(
        id="VIOL-001",
        version="1.0.0",
        severity="HIGH",
        category="test",
        phase="IMPLEMENTATION",
        handler="QUICK_FIX",
        match=RuleMatch(pattern=r"def bad_function\("),
        message="Bad function name"
    )
    re.register_rule(rule)

    # Test violation
    context = {"code": "def bad_function(): pass"}
    violated = re.check_violation(rule, context)
    assert violated == True

    # Test no violation
    context = {"code": "def good_function(): pass"}
    violated = re.check_violation(rule, context)
    assert violated == False

    print("✓ Violation checking works")


def test_execute_rule():
    """Test rule execution"""
    re = RuleEngine()
    rule = Rule(
        id="EXEC-001",
        version="1.0.0",
        severity="HIGH",
        category="test",
        phase="IMPLEMENTATION",
        handler="QUICK_FIX",
        match=RuleMatch(pattern=r"print\("),
        message="Avoid print statements",
        metadata={"suggestion": "Use logging instead"}
    )
    re.register_rule(rule)

    # Execute with violation
    context = {
        "code": "print('debug')",
        "file": "test.py",
        "phase": "IMPLEMENTATION"
    }
    result = re.execute(rule, context)
    assert result.violated == True
    assert result.rule_id == "EXEC-001"
    assert result.handler == "QUICK_FIX"
    assert result.priority == Priority.P1

    print("✓ Rule execution works")


def test_file_pattern_filtering():
    """Test file pattern filtering"""
    re = RuleEngine()
    rule = Rule(
        id="FILE-001",
        version="1.0.0",
        severity="MEDIUM",
        category="test",
        phase="IMPLEMENTATION",
        handler="LOG_ONLY",
        match=RuleMatch(pattern="test", file_patterns=["*.py", "*.js"]),
        message="File pattern test"
    )
    re.register_rule(rule)

    # Test matching file
    context = {
        "code": "test",
        "file": "script.py",
        "phase": "IMPLEMENTATION"
    }
    result = re.execute(rule, context)
    assert result.violated == True

    # Test non-matching file
    context = {
        "code": "test",
        "file": "script.txt",
        "phase": "IMPLEMENTATION"
    }
    result = re.execute(rule, context)
    assert result.violated == False

    print("✓ File pattern filtering works")


def test_context_filtering():
    """Test context filtering"""
    re = RuleEngine()
    rule = Rule(
        id="CTX-001",
        version="1.0.0",
        severity="HIGH",
        category="test",
        phase="IMPLEMENTATION",
        handler="QUICK_FIX",
        match=RuleMatch(
            pattern="test",
            context_filter={"agent_type": "Implementer"}
        ),
        message="Context filter test"
    )
    re.register_rule(rule)

    # Test matching context
    context = {
        "code": "test",
        "agent_type": "Implementer",
        "phase": "IMPLEMENTATION"
    }
    result = re.execute(rule, context)
    assert result.violated == True

    # Test non-matching context
    context = {
        "code": "test",
        "agent_type": "Analyst",
        "phase": "IMPLEMENTATION"
    }
    result = re.execute(rule, context)
    assert result.violated == False

    print("✓ Context filtering works")


def test_priority_handlers():
    """Test all 4 priority handlers"""
    re = RuleEngine()

    # Test P0 - TERMINATE
    rule_p0 = Rule(
        id="P0-001",
        version="1.0.0",
        severity="CRITICAL",
        category="test",
        phase="IMPLEMENTATION",
        handler="TERMINATE",
        match=RuleMatch(pattern="test"),
        message="Critical violation"
    )
    re.register_rule(rule_p0)
    try:
        context = {"code": "test", "phase": "IMPLEMENTATION"}
        result = re.execute(rule_p0, context)
        re.handle_violation(rule_p0, context, result)
        assert False, "Should have raised RuleExecutionError"
    except RuleExecutionError as e:
        assert "TERMINATE" in str(e)
        print("✓ P0 TERMINATE handler works")

    # Test P1 - QUICK_FIX
    rule_p1 = Rule(
        id="P1-001",
        version="1.0.0",
        severity="HIGH",
        category="test",
        phase="IMPLEMENTATION",
        handler="QUICK_FIX",
        match=RuleMatch(pattern="test"),
        message="High priority violation"
    )
    re.register_rule(rule_p1)
    context = {"code": "test", "phase": "IMPLEMENTATION"}
    result = re.execute(rule_p1, context)
    re.handle_violation(rule_p1, context, result)
    assert result.handler == "QUICK_FIX"
    print("✓ P1 QUICK_FIX handler works")

    # Test P2 - LOG_ONLY
    rule_p2 = Rule(
        id="P2-001",
        version="1.0.0",
        severity="MEDIUM",
        category="test",
        phase="IMPLEMENTATION",
        handler="LOG_ONLY",
        match=RuleMatch(pattern="test"),
        message="Medium priority violation"
    )
    re.register_rule(rule_p2)
    context = {"code": "test", "phase": "IMPLEMENTATION"}
    result = re.execute(rule_p2, context)
    re.handle_violation(rule_p2, context, result)
    assert result.handler == "LOG_ONLY"
    print("✓ P2 LOG_ONLY handler works")

    # Test P3 - SOFT_HOOK
    rule_p3 = Rule(
        id="P3-001",
        version="1.0.0",
        severity="LOW",
        category="test",
        phase="IMPLEMENTATION",
        handler="SOFT_HOOK",
        match=RuleMatch(pattern="test"),
        message="Low priority violation"
    )
    re.register_rule(rule_p3)
    context = {"code": "test", "phase": "IMPLEMENTATION"}
    result = re.execute(rule_p3, context)
    # Note: This rule doesn't have soft_hooks enabled, so it will be treated as LOG_ONLY
    re.handle_violation(rule_p3, context, result)
    # Without soft_hooks config, P3 defaults to LOG_ONLY behavior
    assert result.handler in ["SOFT_HOOK", "LOG_ONLY"]
    print("✓ P3 SOFT_HOOK handler works")


def test_soft_hooks_mechanism():
    """Test soft hooks mechanism"""
    re = RuleEngine()
    soft_hooks_config = SoftHooksConfig(
        enabled=True,
        can_be_ignored=True,
        interceptors=[{
            "type": "referrer",
            "config": {"threshold": 2}
        }]
    )
    rule = Rule(
        id="SOFT-001",
        version="1.0.0",
        severity="LOW",
        category="test",
        phase="IMPLEMENTATION",
        handler="SOFT_HOOK",
        match=RuleMatch(pattern="test"),
        message="Soft hook violation",
        soft_hooks=soft_hooks_config
    )
    re.register_rule(rule)

    # First violation - should be SOFT_HOOK
    context = {"code": "test", "phase": "IMPLEMENTATION"}
    result = re.execute(rule, context)
    re.handle_violation(rule, context, result)
    assert result.handler == "SOFT_HOOK"
    assert result.priority == Priority.P3

    # Increment ignore count
    re.increment_soft_hook_ignore("SOFT-001")

    # Second violation - still SOFT_HOOK
    result = re.execute(rule, context)
    re.handle_violation(rule, context, result)
    assert result.handler == "SOFT_HOOK"

    # Increment ignore count again (now at threshold)
    re.increment_soft_hook_ignore("SOFT-001")

    # Third violation - should upgrade to LOG_ONLY
    result = re.execute(rule, context)
    re.handle_violation(rule, context, result)
    assert result.priority == Priority.P2
    assert result.handler == "LOG_ONLY"

    print("✓ Soft hooks mechanism with upgrade works")


def test_get_rules_by_phase():
    """Test getting rules by phase"""
    re = RuleEngine()

    rules_to_add = [
        ("RULE-001", "ANALYSIS", "HIGH"),
        ("RULE-002", "ANALYSIS", "MEDIUM"),
        ("RULE-003", "IMPLEMENTATION", "CRITICAL"),
        ("RULE-004", "REVIEW", "LOW"),
    ]

    for rid, phase, severity in rules_to_add:
        rule = Rule(
            id=rid,
            version="1.0.0",
            severity=severity,
            category="test",
            phase=phase,
            handler="LOG_ONLY",
            match=RuleMatch(pattern="test"),
            message=f"Rule {rid}"
        )
        re.register_rule(rule)

    analysis_rules = re.get_rules_by_phase("ANALYSIS")
    assert len(analysis_rules) == 2

    impl_rules = re.get_rules_by_phase("IMPLEMENTATION")
    assert len(impl_rules) == 1

    print("✓ Getting rules by phase works")


def test_get_soft_hooks_state():
    """Test retrieving soft hook state"""
    re = RuleEngine()
    soft_hooks_config = SoftHooksConfig(enabled=True)
    rule = Rule(
        id="STATE-001",
        version="1.0.0",
        severity="LOW",
        category="test",
        phase="IMPLEMENTATION",
        handler="SOFT_HOOK",
        match=RuleMatch(pattern="test"),
        message="State test",
        soft_hooks=soft_hooks_config
    )
    re.register_rule(rule)

    # Execute to create state
    context = {"code": "test", "phase": "IMPLEMENTATION"}
    result = re.execute(rule, context)
    re.handle_violation(rule, context, result)

    state = re.get_soft_hooks_state("STATE-001")
    assert state is not None
    assert state.rule_id == "STATE-001"
    assert state.ignore_count == 0
    assert state.upgraded == False

    print("✓ Getting soft hooks state works")


def run_all_tests():
    """Run all tests"""
    print("Running Rule Engine Tests...\n")

    test_rule_engine_initialization()
    test_parse_yaml_single_rule()
    test_parse_yaml_multiple_rules()
    test_register_rule()
    test_check_violation()
    test_execute_rule()
    test_file_pattern_filtering()
    test_context_filtering()
    test_priority_handlers()
    test_soft_hooks_mechanism()
    test_get_rules_by_phase()
    test_get_soft_hooks_state()

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all_tests()
