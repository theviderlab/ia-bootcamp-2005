"""
DateTime MCP tool - returns current date and time.

Provides access to current date/time information with multiple format options
and timezone support.
"""

from datetime import datetime, UTC
from typing import Any, Literal

from pydantic import Field

from agentlab.mcp.base import MCPToolBase, MCPToolInput, MCPToolOutput


class DateTimeInput(MCPToolInput):
    """Input schema for datetime tool."""

    format: Literal["iso", "human", "timestamp"] = Field(
        default="iso",
        description=(
            "Output format: 'iso' for ISO 8601 format, "
            "'human' for human-readable format, "
            "'timestamp' for Unix timestamp"
        ),
    )
    timezone: str | None = Field(
        default=None,
        description=(
            "Timezone name (e.g., 'America/New_York', 'Europe/London'). "
            "Defaults to UTC if not specified."
        ),
    )


class DateTimeOutput(MCPToolOutput):
    """Output schema for datetime tool."""

    success: bool = Field(description="Whether the operation was successful")
    datetime: str | float = Field(description="The formatted date/time result")
    format: str = Field(description="The format used for the result")
    timezone: str = Field(description="The timezone used")
    error: str | None = Field(
        default=None, description="Error message if operation failed"
    )


class DateTimeTool(MCPToolBase):
    """
    Tool that returns current date and time.
    
    Supports multiple output formats (ISO 8601, human-readable, Unix timestamp)
    and timezone conversion.
    """

    @property
    def name(self) -> str:
        """Tool identifier."""
        return "get_current_datetime"

    @property
    def description(self) -> str:
        """Tool description for LLMs."""
        return (
            "Get the current date and time. "
            "Use this tool when you need to know the current date, time, or day of the week. "
            "Supports multiple formats (ISO 8601, human-readable, Unix timestamp) "
            "and timezone conversion. "
            "By default returns UTC time in ISO 8601 format."
        )

    @property
    def input_schema(self) -> type[DateTimeInput]:
        """Input parameter schema."""
        return DateTimeInput

    @property
    def output_schema(self) -> type[DateTimeOutput]:
        """Output validation schema."""
        return DateTimeOutput

    async def execute(self, **kwargs) -> dict[str, Any]:
        """
        Execute datetime retrieval.
        
        Args:
            format: Output format ('iso', 'human', 'timestamp')
            timezone: Optional timezone name
        
        Returns:
            Dictionary with datetime information
        """
        # Get validated inputs
        inputs = DateTimeInput(**kwargs)

        # Handle timezone conversion if provided
        if inputs.timezone:
            try:
                import pytz

                tz = pytz.timezone(inputs.timezone)
                now = datetime.now(tz)
                timezone_name = inputs.timezone
            except Exception as e:
                return {
                    "success": False,
                    "datetime": "",
                    "format": inputs.format,
                    "timezone": inputs.timezone,
                    "error": f"Invalid timezone '{inputs.timezone}': {str(e)}",
                }
        else:
            # Use UTC if no timezone specified
            now = datetime.now(UTC)
            timezone_name = "UTC"

        # Format output based on requested format
        try:
            if inputs.format == "iso":
                result: str | float = now.isoformat()
            elif inputs.format == "timestamp":
                result = now.timestamp()
            else:  # human
                result = now.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z")

            return {
                "success": True,
                "datetime": result,
                "format": inputs.format,
                "timezone": timezone_name,
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "datetime": "",
                "format": inputs.format,
                "timezone": timezone_name,
                "error": f"Failed to format datetime: {str(e)}",
            }
