"""Test suite for core/switch_manager.py"""
import pytest
import tempfile
import os
from pathlib import Path
from core.switch_manager import SwitchManager, create_switch_manager, DEFAULT_CONFIG, VALID_MODES


def test_init():
    """Test SwitchManager initialization with temp config"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        
        with open(config_path, "w") as f:
            f.write("enabled: true\nmode: full\n")
        
        manager = SwitchManager(config_path=config_path)
        
        assert manager.config_path == config_path
        assert manager._session_overrides == {}
        assert manager._project_config is None
        assert manager._user_config is None
        assert manager._omo_config is None
        assert manager._config.get("enabled", False) == True
        assert manager._config.get("mode", "") == "full"


def test_get_global():
    """Test get("global", "enabled")"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        
        with open(config_path, "w") as f:
            f.write("enabled: true\nmode: safe\n")
        
        manager = SwitchManager(config_path=config_path)
        
        result = manager.get("global", "enabled")
        assert result == True
        
        # Test with disabled
        with open(config_path, "w") as f:
            f.write("enabled: false\nmode: safe\n")
        
        manager2 = SwitchManager(config_path=config_path)
        result2 = manager2.get("global", "enabled")
        assert result2 == False


def test_get_mode():
    """Test get("mode")"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        
        with open(config_path, "w") as f:
            f.write("enabled: true\nmode: fast\n")
        
        manager = SwitchManager(config_path=config_path)
        
        result = manager.get("mode")
        assert result == "fast"
        
        # Test other valid modes
        for mode in VALID_MODES:
            with open(config_path, "w") as f:
                f.write(f"enabled: true\nmode: {mode}\n")
            
            manager = SwitchManager(config_path=config_path)
            assert manager.get("mode") == mode


def test_set_global():
    """Test set("global", "enabled", False)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        
        with open(config_path, "w") as f:
            f.write("enabled: true\nmode: full\n")
        
        manager = SwitchManager(config_path=config_path)
        
        # Set to False via session override
        manager.set("global", "enabled", False)
        
        result = manager.get("global", "enabled")
        assert result == False


def test_set_mode():
    """Test set("mode", None, "safe")"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.yaml")
        
        with open(config_path, "w") as f:
            f.write("enabled: true\nmode: full\n")
        
        manager = SwitchManager(config_path=config_path)
        
        # Set mode to safe via session override
        manager.set("mode", None, "safe")
        
        result = manager.get("mode")
        assert result == "safe"
        
        # Test invalid mode raises ValueError
        with pytest.raises(ValueError):
            manager.set("mode", None, "invalid")


def run_all_tests():
    """Run all tests"""
    print("Running Switch Manager Tests...\n")
    
    test_init()
    print("✓ test_init passed")
    
    test_get_global()
    print("✓ test_get_global passed")
    
    test_get_mode()
    print("✓ test_get_mode passed")
    
    test_set_global()
    print("✓ test_set_global passed")
    
    test_set_mode()
    print("✓ test_set_mode passed")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all_tests()
