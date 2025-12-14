"""
Example script demonstrating LangChainLLM usage.

This script shows how to use the LangChainLLM class for:
1. Simple text generation
2. Chat conversations
"""

import os
from datetime import datetime

from agentlab.core.llm_interface import LangChainLLM
from agentlab.models import ChatMessage


def example_generate():
    """Example: Simple text generation."""
    print("\n=== Example 1: Text Generation ===")
    
    # Initialize LLM (API key from environment)
    llm = LangChainLLM(model_name="gpt-3.5-turbo")
    
    # Generate text
    prompt = "Explain what is machine learning in one sentence."
    response = llm.generate(prompt, temperature=0.7, max_tokens=100)
    
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")


def example_chat():
    """Example: Chat conversation."""
    print("\n=== Example 2: Chat Conversation ===")
    
    # Initialize LLM
    llm = LangChainLLM(model_name="gpt-3.5-turbo")
    
    # Create conversation history
    messages = [
        ChatMessage(
            role="system",
            content="You are a helpful AI assistant.",
            timestamp=datetime.now(),
        ),
        ChatMessage(
            role="user",
            content="What is the capital of France?",
            timestamp=datetime.now(),
        ),
        ChatMessage(
            role="assistant",
            content="The capital of France is Paris.",
            timestamp=datetime.now(),
        ),
        ChatMessage(
            role="user",
            content="What is the population of that city?",
            timestamp=datetime.now(),
        ),
    ]
    
    # Generate response
    response = llm.chat(messages)
    
    print("Conversation:")
    for msg in messages[-2:]:
        print(f"{msg.role.capitalize()}: {msg.content}")
    print(f"Assistant: {response}")


def example_custom_parameters():
    """Example: Using custom parameters."""
    print("\n=== Example 3: Custom Parameters ===")
    
    # Initialize with custom model
    llm = LangChainLLM(model_name="gpt-4")
    
    # Generate with low temperature for more deterministic output
    prompt = "List three programming languages."
    response = llm.generate(prompt, temperature=0.2, max_tokens=50)
    
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")


def main():
    """Run all examples."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY environment variable not set.")
        print("Set it before running this example:")
        print('export OPENAI_API_KEY="your-api-key-here"')
        return
    
    try:
        example_generate()
        example_chat()
        example_custom_parameters()
        
        print("\n✅ All examples completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
