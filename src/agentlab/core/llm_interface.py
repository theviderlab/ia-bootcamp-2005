"""
LLM (Large Language Model) interface implementation using LangChain.

Provides a unified interface for interacting with different LLM providers
(OpenAI, Anthropic, etc.) through LangChain.
"""

import os
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from agentlab.models import ChatMessage, ToolCall, ToolResult, AgentStep
from agentlab.mcp import get_registry


class LangChainLLM:
    """
    LangChain-based LLM implementation.

    Supports:
    - Multiple LLM providers via LangChain
    - Text generation
    - Chat conversations
    - Configurable parameters (temperature, max_tokens)
    """

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        api_key: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """
        Initialize the LLM interface.

        Args:
            model_name: Name of the model to use.
            api_key: Optional API key (defaults to environment variable).
            temperature: Default sampling temperature (0.0 to 1.0).
            max_tokens: Default maximum tokens to generate (1 to 4000).
        
        Raises:
            ValueError: If API key is missing or parameters are out of range.
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Validate temperature
        if not 0.0 <= temperature <= 1.0:
            raise ValueError(
                f"temperature must be between 0.0 and 1.0, got {temperature}"
            )
        
        # Validate max_tokens
        if not 0 < max_tokens <= 4000:
            raise ValueError(
                f"max_tokens must be between 1 and 4000, got {max_tokens}"
            )
        
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def generate(
        self,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate text from the LLM.

        Args:
            prompt: Input prompt for the model.
            temperature: Sampling temperature (0.0 to 1.0). Defaults to instance value.
            max_tokens: Maximum tokens to generate. Defaults to instance value.

        Returns:
            Generated text response.
        
        Raises:
            ValueError: If prompt is empty or parameters are out of range.
            RuntimeError: If LLM generation fails.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Use provided values or fall back to instance defaults
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # Validate parameters
        if not 0.0 <= temp <= 1.0:
            raise ValueError(f"temperature must be between 0.0 and 1.0, got {temp}")
        if not 0 < tokens <= 4000:
            raise ValueError(f"max_tokens must be between 1 and 4000, got {tokens}")
        
        try:
            # Create a temporary LLM instance with custom parameters
            llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                temperature=temp,
                max_tokens=tokens,
            )
            
            message = HumanMessage(content=prompt)
            response = llm.invoke([message])
            return response.content
        
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}") from e

    def chat(
        self,
        messages: list[ChatMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a chat response from conversation history.

        Args:
            messages: List of chat messages.
            temperature: Sampling temperature (0.0 to 1.0). Defaults to instance value.
            max_tokens: Maximum tokens to generate. Defaults to instance value.

        Returns:
            Generated response from the assistant.
        
        Raises:
            ValueError: If messages list is empty or parameters are out of range.
            RuntimeError: If chat generation fails.
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        # Use provided values or fall back to instance defaults
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # Validate parameters
        if not 0.0 <= temp <= 1.0:
            raise ValueError(f"temperature must be between 0.0 and 1.0, got {temp}")
        if not 0 < tokens <= 4000:
            raise ValueError(f"max_tokens must be between 1 and 4000, got {tokens}")
        
        try:
            # Create a temporary LLM instance with custom parameters
            llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                temperature=temp,
                max_tokens=tokens,
            )
            
            langchain_messages = self._convert_messages(messages)
            response = llm.invoke(langchain_messages)
            return response.content
        
        except Exception as e:
            raise RuntimeError(f"Chat generation failed: {e}") from e

    async def chat_with_tools(
        self,
        messages: list[ChatMessage],
        tool_names: list[str] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        max_iterations: int = 5,
    ) -> tuple[str, list[AgentStep], list[ToolResult]]:
        """
        Generate a chat response with tool calling support.

        Implements a ReAct-style agent that can call registered MCP tools
        to gather information and perform actions before generating a final response.

        Args:
            messages: List of chat messages (conversation history).
            tool_names: Optional list of specific tool names to use. If None, uses all registered tools.
            temperature: Sampling temperature (0.0 to 1.0). Defaults to instance value.
            max_tokens: Maximum tokens to generate. Defaults to instance value.
            max_iterations: Maximum number of agent iterations to prevent infinite loops.

        Returns:
            Tuple of (final_response, agent_steps, tool_results):
                - final_response: The final text response from the LLM
                - agent_steps: List of AgentStep objects tracking the agent's reasoning
                - tool_results: List of all ToolResult objects from tool executions

        Raises:
            ValueError: If messages list is empty or parameters are out of range.
            RuntimeError: If chat generation or tool execution fails critically.
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")

        if max_iterations < 1:
            raise ValueError(f"max_iterations must be at least 1, got {max_iterations}")

        # Use provided values or fall back to instance defaults
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        # Validate parameters
        if not 0.0 <= temp <= 1.0:
            raise ValueError(f"temperature must be between 0.0 and 1.0, got {temp}")
        if not 0 < tokens <= 4000:
            raise ValueError(f"max_tokens must be between 1 and 4000, got {tokens}")

        try:
            # Get tools from registry
            registry = get_registry()
            
            if tool_names is None:
                # Use all registered tools
                langchain_tools = registry.get_langchain_tools()
            else:
                # Use only specified tools
                langchain_tools = registry.get_langchain_tools(tool_names)

            if not langchain_tools:
                raise ValueError(
                    f"No tools available. Requested: {tool_names}, "
                    f"Available: {registry.list_tools()}"
                )

            # Create LLM with tools bound
            llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                temperature=temp,
                max_tokens=tokens,
            )
            llm_with_tools = llm.bind_tools(langchain_tools)

            # Convert initial messages
            langchain_messages = self._convert_messages(messages)

            # Track agent execution
            agent_steps: list[AgentStep] = []
            all_tool_results: list[ToolResult] = []
            step_number = 1

            # Agent loop
            for iteration in range(max_iterations):
                # Invoke LLM
                response = await llm_with_tools.ainvoke(langchain_messages)
                langchain_messages.append(response)

                # Check if LLM wants to use tools
                if not response.tool_calls:
                    # No more tool calls - this is the final answer
                    agent_steps.append(
                        AgentStep(
                            step_number=step_number,
                            action="final_answer",
                            reasoning=f"Agent completed after {iteration + 1} iteration(s)",
                        )
                    )
                    return response.content, agent_steps, all_tool_results

                # Execute each tool call
                for tool_call_data in response.tool_calls:
                    tool_call = ToolCall(
                        id=tool_call_data["id"],
                        name=tool_call_data["name"],
                        args=tool_call_data["args"],
                        timestamp=datetime.now(),
                    )

                    # Get tool from registry
                    tool = registry.get_tool(tool_call.name)

                    if tool is None:
                        # Tool not found
                        tool_result = ToolResult(
                            tool_call_id=tool_call.id,
                            tool_name=tool_call.name,
                            result={},
                            success=False,
                            error=f"Tool '{tool_call.name}' not found in registry",
                            timestamp=datetime.now(),
                        )
                    else:
                        # Execute tool
                        try:
                            result = await tool.execute(**tool_call.args)
                            tool_result = ToolResult(
                                tool_call_id=tool_call.id,
                                tool_name=tool_call.name,
                                result=result,
                                success=result.get("success", True),
                                error=result.get("error"),
                                timestamp=datetime.now(),
                            )
                        except Exception as e:
                            # Tool execution failed
                            tool_result = ToolResult(
                                tool_call_id=tool_call.id,
                                tool_name=tool_call.name,
                                result={},
                                success=False,
                                error=f"Tool execution failed: {str(e)}",
                                timestamp=datetime.now(),
                            )

                    # Store tool result
                    all_tool_results.append(tool_result)

                    # Add tool result to message history
                    tool_message = ToolMessage(
                        content=str(tool_result.result),
                        tool_call_id=tool_call.id,
                    )
                    langchain_messages.append(tool_message)

                    # Record agent step
                    agent_steps.append(
                        AgentStep(
                            step_number=step_number,
                            action="tool_call",
                            tool_call=tool_call,
                            tool_result=tool_result,
                        )
                    )
                    step_number += 1

            # Max iterations reached without final answer
            # Force a final response
            final_response = await llm.ainvoke(langchain_messages)
            agent_steps.append(
                AgentStep(
                    step_number=step_number,
                    action="final_answer",
                    reasoning=f"Max iterations ({max_iterations}) reached, forcing final answer",
                )
            )
            return final_response.content, agent_steps, all_tool_results

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise RuntimeError(f"Chat with tools failed: {e}") from e

    def _convert_messages(
        self, messages: list[ChatMessage]
    ) -> list[HumanMessage | AIMessage | SystemMessage]:
        """
        Convert ChatMessage objects to LangChain message format.

        Args:
            messages: List of ChatMessage objects.

        Returns:
            List of LangChain message objects.
        """
        langchain_messages = []
        
        for msg in messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
        
        return langchain_messages
