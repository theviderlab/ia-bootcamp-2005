"""
Base classes for MCP tools.

Provides abstract base classes and protocols for defining tools that can be
used by LLMs through the Model Context Protocol.
"""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel


class MCPToolInput(BaseModel):
    """
    Base input schema for MCP tools.
    
    All tool input schemas should inherit from this class and define
    their specific parameters using Pydantic fields.
    """

    pass


class MCPToolOutput(BaseModel):
    """
    Base output schema for MCP tools.
    
    All tool output schemas should inherit from this class to provide
    structure and validation for tool results.
    """

    pass


class MCPToolBase(ABC):
    """
    Base class for MCP tools.
    
    Each tool must define:
    - name: Unique identifier for the tool
    - description: Human-readable description for LLMs
    - input_schema: Pydantic model defining input parameters
    - output_schema: Optional Pydantic model for output validation
    - execute: Async implementation of the tool logic
    
    Tools can be converted to LangChain StructuredTool format for integration
    with LangChain agents and chat models.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique tool identifier.
        
        Should be descriptive and follow snake_case convention.
        Example: 'get_current_datetime', 'search_documents'
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable description of what the tool does.
        
        This description is provided to the LLM to help it understand
        when and how to use the tool. Should be clear and concise.
        """
        pass

    @property
    @abstractmethod
    def input_schema(self) -> type[MCPToolInput]:
        """
        Pydantic model defining the tool's input parameters.
        
        Must be a subclass of MCPToolInput. Define fields with appropriate
        types, descriptions, and constraints.
        """
        pass

    @property
    def output_schema(self) -> type[MCPToolOutput] | None:
        """
        Optional Pydantic model for validating tool output.
        
        If provided, the execute method's return value will be validated
        against this schema. Return None if no validation is needed.
        """
        return None

    @abstractmethod
    async def execute(self, **kwargs) -> dict[str, Any]:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters matching input_schema
        
        Returns:
            Dictionary containing the tool execution result.
            If output_schema is defined, this will be validated.
        
        Raises:
            ValueError: If input parameters are invalid
            RuntimeError: If tool execution fails
        """
        pass

    async def execute_with_validation(self, **kwargs) -> dict[str, Any]:
        """
        Execute the tool and validate output against output_schema if defined.
        
        Args:
            **kwargs: Tool-specific parameters
        
        Returns:
            Validated tool execution result
        
        Raises:
            ValueError: If input/output validation fails
            RuntimeError: If tool execution fails
        """
        # Validate inputs against input_schema
        try:
            validated_inputs = self.input_schema(**kwargs)
            kwargs = validated_inputs.model_dump()
        except Exception as e:
            raise ValueError(f"Input validation failed: {e}") from e

        # Execute the tool
        result = await self.execute(**kwargs)

        # Validate output if schema is defined
        if self.output_schema is not None:
            try:
                validated_output = self.output_schema(**result)
                result = validated_output.model_dump()
            except Exception as e:
                raise ValueError(f"Output validation failed: {e}") from e

        return result

    def to_langchain_tool(self) -> StructuredTool:
        """
        Convert this tool to a LangChain StructuredTool.
        
        Returns:
            StructuredTool instance compatible with LangChain agents
        """
        return StructuredTool(
            name=self.name,
            description=self.description,
            args_schema=self.input_schema,
            coroutine=self.execute_with_validation,
        )

    def get_metadata(self) -> dict[str, Any]:
        """
        Get tool metadata including name, description, and schemas.
        
        Returns:
            Dictionary with tool metadata
        """
        metadata = {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema.model_json_schema(),
        }

        if self.output_schema is not None:
            metadata["output_schema"] = self.output_schema.model_json_schema()

        return metadata
