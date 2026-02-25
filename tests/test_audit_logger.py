import pytest
import tempfile
import os
from pathlib import Path
from core.audit_logger import AuditLogger



def test_init():
    """Test AuditLogger initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = tmpdir
        logger = AuditLogger(log_dir)
        expected_file = Path(log_dir) / "audit.log"
        assert logger.log_file == expected_file


def test_write_log():
    """Test writing a log entry"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = tmpdir
        logger = AuditLogger(log_dir)
        
        logger.write_log("ANALYST", "session_001", "test_action", {"test": "data"})
        
        log_file = Path(log_dir) / "audit.log"
        assert log_file.exists()
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "session_001" in content
            assert "ANALYST" in content
            assert "TEST_ACTION" in content


def test_query_logs():
    """Test querying logs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = tmpdir
        logger = AuditLogger(log_dir)
        
        logger.write_log("ANALYST", "session_001", "action1", {"test": "data"})
        logger.write_log("PLANNER", "session_002", "action2", {"test": "data"})
        
        results = logger.query_logs(filters={"actor_id": "session_001"})
        assert len(results) == 1
        assert results[0]["actor_id"] == "session_001"


def test_get_session_log():
    """Test getting session logs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = tmpdir
        logger = AuditLogger(log_dir)
        
        logger.write_log("ANALYST", "session_001", "action1", {"test": "data"})
        logger.write_log("PLANNER", "session_002", "action2", {"test": "data"})
        
        session_logs = logger.get_session_log("session_001")
        assert len(session_logs) == 1
        assert session_logs[0]["actor_id"] == "session_001"


def test_clear_logs():
    """Test clearing logs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = tmpdir
        logger = AuditLogger(log_dir)
        
        logger.write_log("ANALYST", "session_001", "action1", {"test": "data"})
        log_file = Path(log_dir) / "audit.log"
        assert log_file.exists()
        
        logger.clear_logs()
        
        assert not log_file.exists()


def run_all_tests():
    """Run all tests programmatically"""
    test_init()
    print("✓ test_init passed")
    
    test_write_log()
    print("✓ test_write_log passed")
    
    test_query_logs()
    print("✓ test_query_logs passed")
    
    test_get_session_log()
    print("✓ test_get_session_log passed")
    
    test_clear_logs()
    print("✓ test_clear_logs passed")
    
    print("\nAll tests passed!")


if __name__ == "__main__":
    run_all_tests()
