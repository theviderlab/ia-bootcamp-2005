"""
Unit tests for MCP tools infrastructure.

Tests for:
- DateTimeTool functionality
- MCPToolRegistry operations
- Tool input/output validation
- LangChain integration
"""

import pytest
from datetime import datetime
from unittest.mock import patch, Mock

from agentlab.mcp.base import MCPToolBase, MCPToolInput, MCPToolOutput
from agentlab.mcp.tools.datetime_tool import DateTimeTool, DateTimeInput, DateTimeOutput
from agentlab.mcp.registry import MCPToolRegistry, get_registry, reset_registry


# ============ DateTimeInput Validation Tests ============


def test_datetime_input_default_values():
    """Test DateTimeInput with default values."""
    input_data = DateTimeInput()
    
    assert input_data.format == "iso"
    assert input_data.timezone is None


def test_datetime_input_valid_formats():
    """Test DateTimeInput with all valid formats."""
    for fmt in ["iso", "human", "timestamp"]:
        input_data = DateTimeInput(format=fmt)
        assert input_data.format == fmt


def test_datetime_input_invalid_format():
    """Test DateTimeInput rejects invalid format."""
    with pytest.raises(ValueError):
        DateTimeInput(format="invalid")


def test_datetime_input_with_timezone():
    """Test DateTimeInput with timezone."""
    input_data = DateTimeInput(timezone="America/New_York")
    
    assert input_data.timezone == "America/New_York"


# ============ DateTimeOutput Validation Tests ============


def test_datetime_output_success():
    """Test DateTimeOutput for successful execution."""
    output = DateTimeOutput(
        success=True,
        datetime="2025-12-21T10:30:00",
        format="iso",
        timezone="UTC",
        error=None
    )
    
    assert output.success is True
    assert output.error is None


def test_datetime_output_failure():
    """Test DateTimeOutput for failed execution."""
    output = DateTimeOutput(
        success=False,
        datetime="",
        format="iso",
        timezone="Invalid/Timezone",
        error="Invalid timezone"
    )
    
    assert output.success is False
    assert output.error == "Invalid timezone"


# ============ DateTimeTool Tests ============


@pytest.mark.asyncio
async def test_datetime_tool_properties():
    """Test DateTimeTool properties."""
    tool = DateTimeTool()
    
    assert tool.name == "get_current_datetime"
    assert "current date" in tool.description.lower()
    assert tool.input_schema == DateTimeInput
    assert tool.output_schema == DateTimeOutput


@pytest.mark.asyncio
async def test_datetime_tool_execute_iso_format():
    """Test DateTimeTool with ISO format."""
    tool = DateTimeTool()
    result = await tool.execute(format="iso")
    
    assert result["success"] is True
    assert result["format"] == "iso"
    assert result["timezone"] == "UTC"
    assert result["error"] is None
    
    # Validate ISO format
    datetime_str = result["datetime"]
    assert isinstance(datetime_str, str)
    # Should be parseable as ISO datetime
    datetime.fromisoformat(datetime_str)


@pytest.mark.asyncio
async def test_datetime_tool_execute_human_format():
    """Test DateTimeTool with human-readable format."""
    tool = DateTimeTool()
    result = await tool.execute(format="human")
    
    assert result["success"] is True
    assert result["format"] == "human"
    assert isinstance(result["datetime"], str)
    # Human format should contain day name and month
    assert any(day in result["datetime"] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])


@pytest.mark.asyncio
async def test_datetime_tool_execute_timestamp_format():
    """Test DateTimeTool with Unix timestamp format."""
    tool = DateTimeTool()
    result = await tool.execute(format="timestamp")
    
    assert result["success"] is True
    assert result["format"] == "timestamp"
    assert isinstance(result["datetime"], (int, float))
    
    # Timestamp should be reasonable (after 2020, before 2100)
    timestamp = result["datetime"]
    assert 1577836800 < timestamp < 4102444800  # 2020-01-01 to 2100-01-01


@pytest.mark.asyncio
async def test_datetime_tool_with_valid_timezone():
    """Test DateTimeTool with valid timezone."""
    tool = DateTimeTool()
    result = await tool.execute(format="iso", timezone="America/New_York")
    
    assert result["success"] is True
    assert result["timezone"] == "America/New_York"


@pytest.mark.asyncio
async def test_datetime_tool_with_invalid_timezone():
    """Test DateTimeTool with invalid timezone."""
    tool = DateTimeTool()
    result = await tool.execute(format="iso", timezone="Invalid/Timezone")
    
    assert result["success"] is False
    assert "Invalid timezone" in result["error"]
    assert result["timezone"] == "Invalid/Timezone"


@pytest.mark.asyncio
async def test_datetime_tool_execute_with_validation():
    """Test DateTimeTool with input/output validation."""
    tool = DateTimeTool()
    
    # Should validate inputs and outputs
    result = await tool.execute_with_validation(format="iso")
    
    assert result["success"] is True
    # Output should be validated against DateTimeOutput schema
    validated_output = DateTimeOutput(**result)
    assert validated_output.success is True


@pytest.mark.asyncio
async def test_datetime_tool_execute_with_validation_invalid_input():
    """Test DateTimeTool validation rejects invalid input."""
    tool = DateTimeTool()
    
    with pytest.raises(ValueError, match="Input validation failed"):
        await tool.execute_with_validation(format="invalid_format")


@pytest.mark.asyncio
async def test_datetime_tool_to_langchain_tool():
    """Test DateTimeTool conversion to LangChain format."""
    tool = DateTimeTool()
    langchain_tool = tool.to_langchain_tool()
    
    assert langchain_tool.name == "get_current_datetime"
    assert langchain_tool.description == tool.description
    assert langchain_tool.args_schema == DateTimeInput
    
    # Should be callable
    result = await langchain_tool.coroutine(format="iso")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_datetime_tool_get_metadata():
    """Test DateTimeTool metadata retrieval."""
    tool = DateTimeTool()
    metadata = tool.get_metadata()
    
    assert metadata["name"] == "get_current_datetime"
    assert metadata["description"] == tool.description
    assert "input_schema" in metadata
    assert "output_schema" in metadata
    
    # Schemas should be JSON schema format
    assert "properties" in metadata["input_schema"]
    assert "properties" in metadata["output_schema"]


# ============ MCPToolRegistry Tests ============


@pytest.fixture(autouse=True)
def reset_registry_fixture():
    """Reset global registry before and after each test."""
    reset_registry()
    yield
    reset_registry()


def test_registry_initialization():
    """Test registry initializes with built-in tools."""
    registry = MCPToolRegistry()
    
    # Should have datetime tool registered
    assert len(registry) > 0
    assert registry.has_tool("get_current_datetime")


def test_registry_register_tool():
    """Test registering a new tool."""
    registry = MCPToolRegistry()
    initial_count = len(registry)
    
    # Create a mock tool
    class MockTool(MCPToolBase):
        @property
        def name(self):
            return "mock_tool"
        
        @property
        def description(self):
            return "Mock tool for testing"
        
        @property
        def input_schema(self):
            return MCPToolInput
        
        async def execute(self, **kwargs):
            return {"result": "mock"}
    
    mock_tool = MockTool()
    registry.register(mock_tool)
    
    assert len(registry) == initial_count + 1
    assert registry.has_tool("mock_tool")
    assert registry.get_tool("mock_tool") == mock_tool


def test_registry_register_duplicate_tool_raises():
    """Test registering duplicate tool raises ValueError."""
    registry = MCPToolRegistry()
    
    # Try to register another datetime tool
    with pytest.raises(ValueError, match="already registered"):
        registry.register(DateTimeTool())


def test_registry_register_invalid_tool_raises():
    """Test registering non-tool object raises ValueError."""
    registry = MCPToolRegistry()
    
    with pytest.raises(ValueError, match="must be an instance of MCPToolBase"):
        registry.register("not a tool")


def test_registry_unregister_tool():
    """Test unregistering a tool."""
    registry = MCPToolRegistry()
    
    # Unregister datetime tool
    registry.unregister("get_current_datetime")
    
    assert not registry.has_tool("get_current_datetime")
    assert registry.get_tool("get_current_datetime") is None


def test_registry_unregister_nonexistent_tool_raises():
    """Test unregistering non-existent tool raises KeyError."""
    registry = MCPToolRegistry()
    
    with pytest.raises(KeyError, match="not found"):
        registry.unregister("nonexistent_tool")


def test_registry_get_tool():
    """Test getting a tool by name."""
    registry = MCPToolRegistry()
    
    tool = registry.get_tool("get_current_datetime")
    
    assert tool is not None
    assert isinstance(tool, DateTimeTool)
    assert tool.name == "get_current_datetime"


def test_registry_get_nonexistent_tool_returns_none():
    """Test getting non-existent tool returns None."""
    registry = MCPToolRegistry()
    
    tool = registry.get_tool("nonexistent")
    assert tool is None


def test_registry_list_tools():
    """Test listing all tool names."""
    registry = MCPToolRegistry()
    
    tools = registry.list_tools()
    
    assert isinstance(tools, list)
    assert "get_current_datetime" in tools


def test_registry_get_langchain_tools_all():
    """Test getting all tools in LangChain format."""
    registry = MCPToolRegistry()
    
    langchain_tools = registry.get_langchain_tools()
    
    assert isinstance(langchain_tools, list)
    assert len(langchain_tools) > 0
    
    # All should have required LangChain attributes
    for tool in langchain_tools:
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert hasattr(tool, "args_schema")


def test_registry_get_langchain_tools_specific():
    """Test getting specific tools in LangChain format."""
    registry = MCPToolRegistry()
    
    langchain_tools = registry.get_langchain_tools(["get_current_datetime"])
    
    assert len(langchain_tools) == 1
    assert langchain_tools[0].name == "get_current_datetime"


def test_registry_get_langchain_tools_nonexistent_raises():
    """Test getting non-existent tool raises KeyError."""
    registry = MCPToolRegistry()
    
    with pytest.raises(KeyError, match="not found"):
        registry.get_langchain_tools(["nonexistent_tool"])


def test_registry_get_tools_info():
    """Test getting metadata for all tools."""
    registry = MCPToolRegistry()
    
    info = registry.get_tools_info()
    
    assert isinstance(info, list)
    assert len(info) > 0
    
    # Each should have required fields
    for tool_info in info:
        assert "name" in tool_info
        assert "description" in tool_info
        assert "input_schema" in tool_info


def test_registry_get_tool_info():
    """Test getting metadata for specific tool."""
    registry = MCPToolRegistry()
    
    info = registry.get_tool_info("get_current_datetime")
    
    assert info is not None
    assert info["name"] == "get_current_datetime"
    assert "description" in info
    assert "input_schema" in info
    assert "output_schema" in info


def test_registry_get_tool_info_nonexistent_returns_none():
    """Test getting info for non-existent tool returns None."""
    registry = MCPToolRegistry()
    
    info = registry.get_tool_info("nonexistent")
    assert info is None


def test_registry_clear():
    """Test clearing all tools."""
    registry = MCPToolRegistry()
    
    assert len(registry) > 0
    
    registry.clear()
    
    assert len(registry) == 0
    assert not registry.has_tool("get_current_datetime")


def test_registry_repr():
    """Test registry string representation."""
    registry = MCPToolRegistry()
    
    repr_str = repr(registry)
    
    assert "MCPToolRegistry" in repr_str
    assert "get_current_datetime" in repr_str


def test_get_registry_singleton():
    """Test get_registry returns singleton instance."""
    reset_registry()
    
    registry1 = get_registry()
    registry2 = get_registry()
    
    assert registry1 is registry2


def test_reset_registry():
    """Test reset_registry creates new instance."""
    registry1 = get_registry()
    
    reset_registry()
    
    registry2 = get_registry()
    assert registry1 is not registry2
