"""
JCode CLI Commands

Provides Click-based command-line interface for JCode governance system.
Implements agent commands, config commands, and switch commands.

Reference:
    - governance/JCODE_SWITCH.md (CLI command format)
    - cli/config.py (JCodeConfigManager API)
"""

import click
from pathlib import Path
import sys

# Add parent directory to path to import from core module
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.config import JCodeConfigManager, create_config_manager


# ============================================================================
# Main CLI Group
# ============================================================================

@click.group()
@click.option(
    '--config-path',
    type=click.Path(exists=False),
    help='Path to JCode configuration file'
)
@click.pass_context
def jcode(ctx, config_path):
    """
    JCode - Code Governance System for OpenCode

    Provides CLI interface for managing JCode agents, configuration,
    and switch states across 4 levels: global, mode, agent, and rule.
    """
    # Store config path in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config_path

    # Initialize config manager
    ctx.obj['manager'] = create_config_manager(config_path)


# ============================================================================
# Agent Commands
# ============================================================================

@jcode.command()
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.pass_context
def analyze(ctx, config_path):
    """Execute analyst agent (问题分析 - 司马迁)"""
    manager = _get_manager(ctx, config_path)
    click.echo("Agent command: analyze")
    click.echo("Agent: Analyst (司马迁 - 问题分析)")
    click.echo(f"Config path: {manager.get_config_path()}")


@jcode.command()
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.pass_context
def plan(ctx, config_path):
    """Execute planner agent (任务规划 - 商鞅)"""
    manager = _get_manager(ctx, config_path)
    click.echo("Agent command: plan")
    click.echo("Agent: Planner (商鞅 - 任务规划)")
    click.echo(f"Config path: {manager.get_config_path()}")


@jcode.command()
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.pass_context
def implement(ctx, config_path):
    """Execute implementer agent (代码实现 - 鲁班)"""
    manager = _get_manager(ctx, config_path)
    click.echo("Agent command: implement")
    click.echo("Agent: Implementer (鲁班 - 代码实现)")
    click.echo(f"Config path: {manager.get_config_path()}")


@jcode.command()
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.pass_context
def review(ctx, config_path):
    """Execute reviewer agent (合规审查 - 包拯)"""
    manager = _get_manager(ctx, config_path)
    click.echo("Agent command: review")
    click.echo("Agent: Reviewer (包拯 - 合规审查)")
    click.echo(f"Config path: {manager.get_config_path()}")


@jcode.command()
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.pass_context
def test(ctx, config_path):
    """Execute tester agent (证据验证 - 张衡)"""
    manager = _get_manager(ctx, config_path)
    click.echo("Agent command: test")
    click.echo("Agent: Tester (张衡 - 证据验证)")
    click.echo(f"Config path: {manager.get_config_path()}")


@jcode.command()
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.pass_context
def conductor(ctx, config_path):
    """Execute conductor agent (终局裁决 - 韩非子)"""
    manager = _get_manager(ctx, config_path)
    click.echo("Agent command: conductor")
    click.echo("Agent: Conductor (韩非子 - 终局裁决)")
    click.echo(f"Config path: {manager.get_config_path()}")


# ============================================================================
# Config Commands
# ============================================================================

@jcode.command('show')
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.pass_context
def show(ctx, config_path):
    """Display current JCode configuration status"""
    manager = _get_manager(ctx, config_path)
    click.echo(manager.format_status())


@jcode.command('set')
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.argument('key', required=True)
@click.argument('value', required=True)
@click.pass_context
def set_config(ctx, config_path, key, value):
    """
    Set a configuration value.

    Examples:
        jcode set enabled true
        jcode set mode safe
        jcode set max_iterations 3
    """
    manager = _get_manager(ctx, config_path)

    try:
        # Parse value (handle booleans and integers)
        if value.lower() in ('true', 'yes', '1'):
            parsed_value = True
        elif value.lower() in ('false', 'no', '0'):
            parsed_value = False
        elif value.isdigit():
            parsed_value = int(value)
        else:
            parsed_value = value

        # Update configuration
        manager.update_config({key: parsed_value})
        click.echo(f"Configuration updated: {key} = {parsed_value}")

    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@jcode.command('enable')
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.pass_context
def enable_jcode(ctx, config_path):
    """Enable JCode governance system"""
    manager = _get_manager(ctx, config_path)

    try:
        manager.set_switch("global", "enabled", True)
        click.echo("JCode enabled successfully")
        click.echo("\nCurrent status:")
        click.echo(manager.format_status())

    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@jcode.command('disable')
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.pass_context
def disable_jcode(ctx, config_path):
    """Disable JCode governance system"""
    manager = _get_manager(ctx, config_path)

    try:
        manager.set_switch("global", "enabled", False)
        click.echo("JCode disabled successfully")
        click.echo("\nCurrent status:")
        click.echo(manager.format_status())

    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Switch Commands
# ============================================================================

@jcode.command('mode')
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.argument('mode_name', type=click.Choice(['full', 'light', 'safe', 'fast', 'custom']))
@click.pass_context
def set_mode(ctx, config_path, mode_name):
    """
    Set execution mode.

    Modes:
        full   - Complete governance, all agents, 5 iterations
        light  - Lightweight, 3 iterations, quick iteration
        safe   - All agents + human intervention, safety first
        fast   - Skip tester, 2 iterations (prototyping only)
        custom - User-defined agent and rule configuration
    """
    manager = _get_manager(ctx, config_path)

    try:
        manager.set_switch("mode", None, mode_name)
        click.echo(f"Mode set to: {mode_name}")
        click.echo("\nCurrent status:")
        click.echo(manager.format_status())

    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@jcode.command('agent')
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.argument('action', type=click.Choice(['enable', 'disable']))
@click.argument('name', type=click.Choice(['analyst', 'planner', 'implementer', 'reviewer', 'tester', 'conductor']))
@click.pass_context
def agent(ctx, config_path, action, name):
    """
    Enable or disable a specific agent.

    Agents:
        analyst     - Problem analysis (司马迁)
        planner     - Task planning (商鞅)
        implementer - Code implementation (鲁班)
        reviewer    - Compliance review (包拯)
        tester      - Evidence validation (张衡)
        conductor   - Final arbitration (韩非子)
    """
    manager = _get_manager(ctx, config_path)

    try:
        enabled = (action == 'enable')
        manager.set_switch("agent", name, enabled)
        click.echo(f"Agent '{name}' {action}d successfully")
        click.echo("\nCurrent status:")
        click.echo(manager.format_status())

    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@jcode.command('rule')
@click.option('--config-path', type=click.Path(exists=False), help='Path to JCode configuration file')
@click.argument('action', type=click.Choice(['enable', 'disable']))
@click.argument('name', required=True)
@click.pass_context
def rule(ctx, config_path, action, name):
    """
    Enable or disable a specific rule.

    Rules:
        R001_no_skip_review              - Prohibit skipping review
        R002_require_test                - Require test evidence
        R003_nfr_required                - Require non-functional requirements
        R004_human_intervention_on_error - Force human intervention on error
        G001_audit_logging               - Audit logging
        G002_iteration_tracking          - Iteration tracking
        G003_context_lock_required       - Context lock required
    """
    manager = _get_manager(ctx, config_path)

    try:
        enabled = (action == 'enable')
        manager.set_switch("rule", name, enabled)
        click.echo(f"Rule '{name}' {action}d successfully")
        click.echo("\nCurrent status:")
        click.echo(manager.format_status())

    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Helper Functions
# ============================================================================

def _get_manager(ctx, config_path):
    """
    Get or create a config manager instance.

    Args:
        ctx: Click context object
        config_path: Optional config path override

    Returns:
        JCodeConfigManager instance
    """
    # Use config path from context or parameter
    path = config_path or ctx.obj.get('config_path')

    # Reuse existing manager from context if available
    if path is None and 'manager' in ctx.obj:
        return ctx.obj['manager']

    # Create new manager
    return create_config_manager(path)


# ============================================================================
# CLI Entry Point
# ============================================================================

if __name__ == '__main__':
    jcode()
