"""
Unit tests for MPC routes.

Tests for the MCP tool introspection API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from agentlab.api.main import app
from agentlab.mcp.registry import reset_registry

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_mcp_registry():
    """Reset MCP registry before each test."""
    reset_registry()
    yield
    reset_registry()


# ============ GET /mpc/tools Tests ============


def test_list_tools_success():
    """Test listing all tools returns tool metadata."""
    response = client.get("/mpc/tools")
    
    assert response.status_code == 200
    
    tools = response.json()
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    # Should have datetime tool
    datetime_tool = next((t for t in tools if t["name"] == "get_current_datetime"), None)
    assert datetime_tool is not None
    assert "description" in datetime_tool
    assert "input_schema" in datetime_tool
    assert "output_schema" in datetime_tool


def test_list_tools_structure():
    """Test tool metadata has correct structure."""
    response = client.get("/mpc/tools")
    
    assert response.status_code == 200
    
    tools = response.json()
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert isinstance(tool["name"], str)
        assert isinstance(tool["description"], str)
        assert isinstance(tool["input_schema"], dict)
        
        # Input schema should be valid JSON Schema
        assert "properties" in tool["input_schema"]


# ============ GET /mpc/tools/names Tests ============


def test_list_tool_names_success():
    """Test listing tool names returns simple list."""
    response = client.get("/mpc/tools/names")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "tools" in data
    assert "count" in data
    assert isinstance(data["tools"], list)
    assert isinstance(data["count"], int)
    assert len(data["tools"]) == data["count"]
    
    # Should include datetime tool
    assert "get_current_datetime" in data["tools"]


def test_list_tool_names_count_matches():
    """Test count matches number of tools."""
    response = client.get("/mpc/tools/names")
    
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["tools"]) == data["count"]


# ============ GET /mpc/tools/{tool_name} Tests ============


def test_get_tool_info_success():
    """Test getting specific tool info."""
    response = client.get("/mpc/tools/get_current_datetime")
    
    assert response.status_code == 200
    
    tool = response.json()
    assert tool["name"] == "get_current_datetime"
    assert "description" in tool
    assert "input_schema" in tool
    assert "output_schema" in tool
    
    # Check input schema structure
    input_schema = tool["input_schema"]
    assert "properties" in input_schema
    assert "format" in input_schema["properties"]
    assert "timezone" in input_schema["properties"]


def test_get_tool_info_not_found():
    """Test getting non-existent tool returns 404."""
    response = client.get("/mpc/tools/nonexistent_tool")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_tool_info_output_schema():
    """Test tool info includes output schema."""
    response = client.get("/mpc/tools/get_current_datetime")
    
    assert response.status_code == 200
    
    tool = response.json()
    output_schema = tool["output_schema"]
    
    assert output_schema is not None
    assert "properties" in output_schema
    assert "success" in output_schema["properties"]
    assert "datetime" in output_schema["properties"]
    assert "error" in output_schema["properties"]
