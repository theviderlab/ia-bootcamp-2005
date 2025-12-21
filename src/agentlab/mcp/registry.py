"""
Registry for MCP tools.

Provides centralized management of all available MCP tools, including
registration, discovery, and integration with LangChain.
"""

import logging
from typing import Any

from agentlab.mcp.base import MCPToolBase
from agentlab.mcp.tools.datetime_tool import DateTimeTool

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """
    Central registry for all MCP tools.
    
    Responsibilities:
    - Register and manage tool instances
    - Provide tool discovery
    - Convert tools to LangChain format
    - Prevent duplicate registrations
    """

    def __init__(self):
        """Initialize registry and register built-in tools."""
        self._tools: dict[str, MCPToolBase] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        """Register all built-in tools."""
        try:
            # Register datetime tool
            self.register(DateTimeTool())
            logger.info("Registered built-in tools: datetime")
        except Exception as e:
            logger.error(f"Failed to register built-in tools: {e}")

    def register(self, tool: MCPToolBase) -> None:
        """
        Register a new tool.
        
        Args:
            tool: Tool instance to register
        
        Raises:
            ValueError: If tool name already exists or tool is invalid
        """
        if not isinstance(tool, MCPToolBase):
            raise ValueError(f"Tool must be an instance of MCPToolBase, got {type(tool)}")

        tool_name = tool.name

        if tool_name in self._tools:
            raise ValueError(
                f"Tool '{tool_name}' is already registered. "
                "Each tool must have a unique name."
            )

        self._tools[tool_name] = tool
        logger.debug(f"Registered tool: {tool_name}")

    def unregister(self, tool_name: str) -> None:
        """
        Unregister a tool by name.
        
        Args:
            tool_name: Name of the tool to remove
        
        Raises:
            KeyError: If tool doesn't exist
        """
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' not found in registry")

        del self._tools[tool_name]
        logger.debug(f"Unregistered tool: {tool_name}")

    def get_tool(self, name: str) -> MCPToolBase | None:
        """
        Get a tool by name.
        
        Args:
            name: Tool identifier
        
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        """
        Check if a tool exists in the registry.
        
        Args:
            name: Tool identifier
        
        Returns:
            True if tool exists, False otherwise
        """
        return name in self._tools

    def list_tools(self) -> list[str]:
        """
        List all registered tool names.
        
        Returns:
            List of tool identifiers
        """
        return list(self._tools.keys())

    def get_langchain_tools(self, tool_names: list[str] | None = None) -> list:
        """
        Get tools in LangChain StructuredTool format.
        
        Args:
            tool_names: Optional list of specific tool names to retrieve.
                       If None, returns all tools.
        
        Returns:
            List of LangChain StructuredTool instances
        
        Raises:
            KeyError: If a specified tool name doesn't exist
        """
        if tool_names is None:
            # Return all tools
            return [tool.to_langchain_tool() for tool in self._tools.values()]

        # Return specific tools
        langchain_tools = []
        for name in tool_names:
            if name not in self._tools:
                raise KeyError(f"Tool '{name}' not found in registry")
            langchain_tools.append(self._tools[name].to_langchain_tool())

        return langchain_tools

    def get_tools_info(self) -> list[dict[str, Any]]:
        """
        Get metadata for all registered tools.
        
        Returns:
            List of tool metadata dictionaries containing name,
            description, input_schema, and optional output_schema
        """
        return [tool.get_metadata() for tool in self._tools.values()]

    def get_tool_info(self, name: str) -> dict[str, Any] | None:
        """
        Get metadata for a specific tool.
        
        Args:
            name: Tool identifier
        
        Returns:
            Tool metadata dictionary or None if not found
        """
        tool = self.get_tool(name)
        return tool.get_metadata() if tool else None

    def clear(self) -> None:
        """
        Clear all registered tools.
        
        Warning: This will remove all tools including built-in ones.
        Use with caution.
        """
        self._tools.clear()
        logger.warning("All tools cleared from registry")

    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)

    def __repr__(self) -> str:
        """String representation of registry."""
        tool_names = ", ".join(self._tools.keys())
        return f"MCPToolRegistry(tools=[{tool_names}])"


# Global registry instance
_registry: MCPToolRegistry | None = None


def get_registry() -> MCPToolRegistry:
    """
    Get the global tool registry instance.
    
    Returns:
        Global MCPToolRegistry singleton
    """
    global _registry
    if _registry is None:
        _registry = MCPToolRegistry()
        logger.info("Initialized global MCP tool registry")
    return _registry


def reset_registry() -> None:
    """
    Reset the global registry instance.
    
    Used primarily for testing to ensure clean state.
    """
    global _registry
    _registry = None
    logger.debug("Global registry reset")
