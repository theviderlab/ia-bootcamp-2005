"""
MPC (Model Context Protocol) management API routes.

Endpoints for:
- Listing available MCP tools
- Getting tool information
- Tool introspection
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentlab.mcp.registry import get_registry

router = APIRouter()


class ToolInfoResponse(BaseModel):
    """Response model for tool information."""

    name: str = Field(description="Unique tool identifier")
    description: str = Field(description="Human-readable description of the tool")
    input_schema: dict[str, Any] = Field(
        description="JSON schema for tool input parameters"
    )
    output_schema: dict[str, Any] | None = Field(
        default=None, description="JSON schema for tool output (if defined)"
    )


class ToolListResponse(BaseModel):
    """Response model for list of available tools."""

    tools: list[str] = Field(description="List of tool names")
    count: int = Field(description="Total number of tools")


@router.get("/tools", response_model=list[ToolInfoResponse])
async def list_tools():
    """
    List all available MCP tools with their metadata.
    
    Returns detailed information about each registered tool including:
    - Tool name and description
    - Input parameter schema (JSON Schema format)
    - Output schema (if defined)
    
    Returns:
        List of tool information objects
    """
    try:
        registry = get_registry()
        tools_info = registry.get_tools_info()
        
        return [
            ToolInfoResponse(
                name=tool["name"],
                description=tool["description"],
                input_schema=tool["input_schema"],
                output_schema=tool.get("output_schema")
            )
            for tool in tools_info
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tools: {str(e)}"
        )


@router.get("/tools/names", response_model=ToolListResponse)
async def list_tool_names():
    """
    List names of all available MCP tools.
    
    Returns a simple list of tool names without detailed metadata.
    Use this endpoint for quick discovery of available tools.
    
    Returns:
        List of tool names and count
    """
    try:
        registry = get_registry()
        tool_names = registry.list_tools()
        
        return ToolListResponse(
            tools=tool_names,
            count=len(tool_names)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tool names: {str(e)}"
        )


@router.get("/tools/{tool_name}", response_model=ToolInfoResponse)
async def get_tool_info(tool_name: str):
    """
    Get detailed information about a specific tool.
    
    Args:
        tool_name: Unique identifier of the tool
    
    Returns:
        Tool information including name, description, and schemas
    
    Raises:
        404: If tool is not found
    """
    try:
        registry = get_registry()
        tool_info = registry.get_tool_info(tool_name)
        
        if tool_info is None:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_name}' not found"
            )
        
        return ToolInfoResponse(
            name=tool_info["name"],
            description=tool_info["description"],
            input_schema=tool_info["input_schema"],
            output_schema=tool_info.get("output_schema")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tool info: {str(e)}"
        )
