"""
LLM (Large Language Model) interface implementation using LangChain.

Provides a unified interface for interacting with different LLM providers
(OpenAI, Anthropic, etc.) through LangChain.
"""

import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from agentlab.models import ChatMessage


class LangChainLLM:
    """
    LangChain-based LLM implementation.

    Supports:
    - Multiple LLM providers via LangChain
    - Text generation
    - Chat conversations
    - Configurable parameters (temperature, max_tokens)
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: str | None = None):
        """
        Initialize the LLM interface.

        Args:
            model_name: Name of the model to use.
            api_key: Optional API key (defaults to environment variable).
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            temperature=0.7,
        )

    def generate(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000
    ) -> str:
        """
        Generate text from the LLM.

        Args:
            prompt: Input prompt for the model.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            Generated text response.
        
        Raises:
            ValueError: If prompt is empty.
            RuntimeError: If LLM generation fails.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            # Create a temporary LLM instance with custom parameters
            llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            message = HumanMessage(content=prompt)
            response = llm.invoke([message])
            return response.content
        
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}") from e

    def chat(self, messages: list[ChatMessage]) -> str:
        """
        Generate a chat response from conversation history.

        Args:
            messages: List of chat messages.

        Returns:
            Generated response from the assistant.
        
        Raises:
            ValueError: If messages list is empty.
            RuntimeError: If chat generation fails.
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        try:
            langchain_messages = self._convert_messages(messages)
            response = self.llm.invoke(langchain_messages)
            return response.content
        
        except Exception as e:
            raise RuntimeError(f"Chat generation failed: {e}") from e

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
