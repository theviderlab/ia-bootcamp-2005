"""
LLM (Large Language Model) interface implementation using LangChain.

Provides a unified interface for interacting with different LLM providers
(OpenAI, Anthropic, etc.) through LangChain.
"""

from agent_lab.models import ChatMessage


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
        self.api_key = api_key
        # LangChain components will be initialized here

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
        """
        # Implementation to be added in future iterations
        raise NotImplementedError("Text generation to be implemented")

    def chat(self, messages: list[ChatMessage]) -> str:
        """
        Generate a chat response from conversation history.

        Args:
            messages: List of chat messages.

        Returns:
            Generated response from the assistant.
        """
        raise NotImplementedError("Chat functionality to be implemented")

    def _convert_messages(self, messages: list[ChatMessage]) -> list[dict]:
        """
        Convert ChatMessage objects to LangChain format.

        Args:
            messages: List of ChatMessage objects.

        Returns:
            List of message dictionaries for LangChain.
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
