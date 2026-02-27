"""
Integration tests for JCode MCP Server - All 6 MCP Tools.

Tests the MCP protocol integration via FastAPI TestClient, covering:
- Health endpoint
- tools/list method
- All 6 JCode agent tools via tools/call
- Error handling for invalid requests
"""

import pytest
from fastapi.testclient import TestClient
from mcp.server import app


client = TestClient(app)


# =============================================================================
# HEALTH ENDPOINT TESTS
# =============================================================================

class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_ok_status(self):
        """Test that health endpoint returns ok status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["tools"] == 6

    def test_health_returns_tool_count(self):
        """Test that health endpoint returns correct tool count."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert data["tools"] == 6  # 6 JCode agent tools


# =============================================================================
# TOOLS/LIST METHOD TESTS
# =============================================================================

class TestToolsListMethod:
    """Tests for tools/list JSON-RPC method."""

    def test_tools_list_returns_success(self):
        """Test tools/list returns a valid response."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data

    def test_tools_list_returns_six_tools(self):
        """Test tools/list returns 6 tools."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
        )
        
        data = response.json()
        assert "result" in data
        tools = data["result"].get("tools", [])
        assert len(tools) == 6


# =============================================================================
# JCODE-ANALYST TOOL TESTS
# =============================================================================

class TestJCodeAnalystTool:
    """Tests for jcode-analyst tool."""

    def test_analyst_tool_success(self):
        """Test jcode-analyst tool with valid input."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": "analyze",
                    "arguments": {
                        "context_lock_id": "test_lock_analyst",
                        "input_data": {
                            "problem_statement": "Add user authentication",
                            "requirements": ["secure", "fast"]
                        },
                        "mode": "full"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "content" in data["result"]
        assert len(data["result"]["content"]) == 1
        assert data["result"]["content"][0]["type"] == "text"

    def test_analyst_tool_missing_input_data(self):
        """Test jcode-analyst tool with missing input_data."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {
                    "name": "analyze",
                    "arguments": {
                        "context_lock_id": "test_lock_analyst"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32602
        assert "input_data is required" in data["error"]["data"]


# =============================================================================
# JCODE-PLANNER TOOL TESTS
# =============================================================================

class TestJCodePlannerTool:
    """Tests for jcode-planner tool."""

    def test_planner_tool_success(self):
        """Test jcode-planner tool with valid input."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 20,
                "method": "tools/call",
                "params": {
                    "name": "plan",
                    "arguments": {
                        "context_lock_id": "test_lock_planner",
                        "input_data": {
                            "analysis": {
                                "verifiability": "HARD",
                                "tasks_needed": 3
                            }
                        },
                        "mode": "full"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "content" in data["result"]

    def test_planner_tool_missing_input_data(self):
        """Test jcode-planner tool with missing input_data."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 21,
                "method": "tools/call",
                "params": {
                    "name": "plan",
                    "arguments": {
                        "context_lock_id": "test_lock_planner"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32602


# =============================================================================
# JCODE-IMPLEMENTER TOOL TESTS
# =============================================================================

class TestJCodeImplementerTool:
    """Tests for jcode-implementer tool."""

    def test_implementer_tool_success(self):
        """Test jcode-implementer tool with valid input."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 30,
                "method": "tools/call",
                "params": {
                    "name": "implement",
                    "arguments": {
                        "context_lock_id": "test_lock_implementer",
                        "input_data": {
                            "implementation": "def hello(): return 'world'",
                            "files_changed": ["src/hello.py"]
                        },
                        "mode": "full"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        text = data["result"]["content"][0]["text"]
        assert "Checks:" in text
        assert "Warnings:" in text

    def test_implementer_tool_missing_input_data(self):
        """Test jcode-implementer tool with missing input_data."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 31,
                "method": "tools/call",
                "params": {
                    "name": "implement",
                    "arguments": {
                        "context_lock_id": "test_lock_implementer"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32602
        assert "input_data is required" in data["error"]["data"]

    def test_implementer_tool_with_sensitive_data_warning(self):
        """Test jcode-implementer tool with sensitive data."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 32,
                "method": "tools/call",
                "params": {
                    "name": "implement",
                    "arguments": {
                        "context_lock_id": "test_lock_implementer",
                        "input_data": {
                            "implementation": "password = 'secret123'",
                            "files_changed": ["src/config.py"]
                        }
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        text = data["result"]["content"][0]["text"]
        assert "HUMAN_INTERVENTION" in text


# =============================================================================
# JCODE-REVIEWER TOOL TESTS
# =============================================================================

class TestJCodeReviewerTool:
    """Tests for jcode-reviewer tool."""

    def test_reviewer_tool_success_approved(self):
        """Test jcode-reviewer tool with APPROVED verdict."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 40,
                "method": "tools/call",
                "params": {
                    "name": "review",
                    "arguments": {
                        "context_lock_id": "test_lock_reviewer",
                        "input_data": {
                            "review": "Code follows project standards",
                            "files_implemented": ["src/hello.py"]
                        },
                        "mode": "full"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        text = data["result"]["content"][0]["text"]
        assert "Verdict: APPROVED" in text

    def test_reviewer_tool_success_rejected(self):
        """Test jcode-reviewer tool with REJECTED verdict."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 41,
                "method": "tools/call",
                "params": {
                    "name": "review",
                    "arguments": {
                        "context_lock_id": "test_lock_reviewer",
                        "input_data": {
                            "review": "Code fails security checks. REJECTED.",
                            "files_implemented": ["src/config.py"]
                        },
                        "mode": "full"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        text = data["result"]["content"][0]["text"]
        assert "Verdict: REJECTED" in text

    def test_reviewer_tool_missing_input_data(self):
        """Test jcode-reviewer tool with missing input_data."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 42,
                "method": "tools/call",
                "params": {
                    "name": "review",
                    "arguments": {
                        "context_lock_id": "test_lock_reviewer"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32602

    def test_reviewer_tool_light_mode(self):
        """Test jcode-reviewer tool with light mode."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 43,
                "method": "tools/call",
                "params": {
                    "name": "review",
                    "arguments": {
                        "context_lock_id": "test_lock_reviewer",
                        "input_data": {
                            "review": "Quick review",
                            "files_implemented": ["src/light.py"]
                        },
                        "mode": "light"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data


# =============================================================================
# JCODE-TESTER TOOL TESTS
# =============================================================================

class TestJCodeTesterTool:
    """Tests for jcode-tester tool."""

    def test_tester_tool_success(self):
        """Test jcode-tester tool with valid input."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 50,
                "method": "tools/call",
                "params": {
                    "name": "test",
                    "arguments": {
                        "context_lock_id": "test_lock_tester",
                        "input_data": {
                            "test_results": "All tests passed",
                            "files_tested": ["src/hello.py"]
                        },
                        "mode": "full"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "content" in data["result"]

    def test_tester_tool_missing_input_data(self):
        """Test jcode-tester tool with missing input_data."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 51,
                "method": "tools/call",
                "params": {
                    "name": "test",
                    "arguments": {
                        "context_lock_id": "test_lock_tester"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32602
        assert "input_data is required" in data["error"]["data"]


# =============================================================================
# JCODE-CONDUCTOR TOOL TESTS
# =============================================================================

class TestJCodeConductorTool:
    """Tests for jcode-conductor tool."""

    def test_conductor_tool_success(self):
        """Test jcode-conductor tool with valid input."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 60,
                "method": "tools/call",
                "params": {
                    "name": "conductor",
                    "arguments": {
                        "context_lock_id": "test_lock_conductor",
                        "input_data": {
                            "review_result": "APPROVED",
                            "test_result": "PASSED",
                            "iteration_count": 1
                        },
                        "mode": "full"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert "content" in data["result"]

    def test_conductor_tool_missing_input_data(self):
        """Test jcode-conductor tool with missing input_data."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 61,
                "method": "tools/call",
                "params": {
                    "name": "conductor",
                    "arguments": {
                        "context_lock_id": "test_lock_conductor"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32602
        assert "input_data is required" in data["error"]["data"]


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Tests for JSON-RPC error handling."""

    def test_invalid_json(self):
        """Test with invalid JSON payload."""
        response = client.post(
            "/mcp",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32700  # Parse error

    def test_missing_jsonrpc_field(self):
        """Test with missing jsonrpc field."""
        response = client.post(
            "/mcp",
            json={
                "id": 1,
                "method": "tools/list"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32600  # Invalid Request

    def test_invalid_jsonrpc_version(self):
        """Test with invalid jsonrpc version."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "1.0",
                "id": 1,
                "method": "tools/list"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32600

    def test_missing_method_field(self):
        """Test with missing method field."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32600

    def test_unknown_method(self):
        """Test with unknown method."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "unknown/method"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32601  # Method not found

    def test_tool_not_found(self):
        """Test with non-existent tool."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "jcode-nonexistent",
                    "arguments": {}
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32601  # Method not found


# =============================================================================
# COMPLETE WORKFLOW TEST
# =============================================================================

class TestCompleteWorkflow:
    """Tests for complete agent workflow."""

    def test_full_workflow(self):
        """Test complete workflow through all 6 agents."""
        # Step 1: Analyst
        analyst_response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 100,
                "method": "tools/call",
                "params": {
                    "name": "analyze",
                    "arguments": {
                        "context_lock_id": "workflow_test",
                        "input_data": {
                            "problem_statement": "Implement feature X"
                        }
                    }
                }
            }
        )
        assert analyst_response.status_code == 200
        assert "result" in analyst_response.json()

        # Step 2: Planner
        planner_response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 101,
                "method": "tools/call",
                "params": {
                    "name": "plan",
                    "arguments": {
                        "context_lock_id": "workflow_test",
                        "input_data": {
                            "analysis": {"verifiability": "HARD"}
                        }
                    }
                }
            }
        )
        assert planner_response.status_code == 200
        assert "result" in planner_response.json()

        # Step 3: Implementer
        implementer_response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 102,
                "method": "tools/call",
                "params": {
                    "name": "implement",
                    "arguments": {
                        "context_lock_id": "workflow_test",
                        "input_data": {
                            "implementation": "def feature_x(): pass",
                            "files_changed": ["feature.py"]
                        }
                    }
                }
            }
        )
        assert implementer_response.status_code == 200
        assert "result" in implementer_response.json()

        # Step 4: Reviewer
        reviewer_response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 103,
                "method": "tools/call",
                "params": {
                    "name": "review",
                    "arguments": {
                        "context_lock_id": "workflow_test",
                        "input_data": {
                            "review": "Code looks good",
                            "files_implemented": ["feature.py"]
                        }
                    }
                }
            }
        )
        assert reviewer_response.status_code == 200
        assert "result" in reviewer_response.json()

        # Step 5: Tester
        tester_response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 104,
                "method": "tools/call",
                "params": {
                    "name": "test",
                    "arguments": {
                        "context_lock_id": "workflow_test",
                        "input_data": {
                            "test_results": "All passed",
                            "files_tested": ["feature.py"]
                        }
                    }
                }
            }
        )
        assert tester_response.status_code == 200
        assert "result" in tester_response.json()

        # Step 6: Conductor
        conductor_response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 105,
                "method": "tools/call",
                "params": {
                    "name": "conductor",
                    "arguments": {
                        "context_lock_id": "workflow_test",
                        "input_data": {
                            "review_result": "APPROVED",
                            "test_result": "PASSED",
                            "iteration_count": 1
                        }
                    }
                }
            }
        )
        assert conductor_response.status_code == 200
        assert "result" in conductor_response.json()
