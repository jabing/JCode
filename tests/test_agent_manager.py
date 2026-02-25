"""
Test suite for AgentManager
"""
import pytest
from core.agent_manager import AgentManager, create_agent_manager, ALL_AGENTS


def test_init():
    """Test AgentManager initialization"""
    manager = AgentManager()
    assert manager is not None
    assert hasattr(manager, 'iteration_count')
    assert manager.iteration_count == 0


def test_list_agents():
    """Test listing 6 agents"""
    manager = AgentManager()
    agents = manager.list_agents()
    assert isinstance(agents, list)
    assert len(agents) == 6
    expected_agents = ['analyst', 'planner', 'implementer', 'reviewer', 'tester', 'conductor']
    for agent in expected_agents:
        assert agent in agents


def test_dispatch_agent():
    """Test dispatching to an agent"""
    manager = AgentManager()
    result = manager.dispatch_agent('analyst', 'Test task')
    assert result is not None
    assert result['payload']['agent'] == 'analyst'


def test_iteration_tracking():
    """Test iteration count"""
    manager = AgentManager()
    initial_count = manager.iteration_count
    assert initial_count == 0

    # Simulate an iteration
    manager.start_iteration()
    assert manager.iteration_count == 1
    assert manager.iteration_count > initial_count


def test_invalid_agent_raises_error():
    """Test ValueError on invalid agent"""
    manager = AgentManager()
    with pytest.raises(ValueError, match="Invalid agent_type"):
        manager.dispatch_agent('invalid_agent', 'Test task')


def run_all_tests():
    """Run all tests in this file"""
    pytest.main([__file__, '-v'])


if __name__ == "__main__":
    run_all_tests()
