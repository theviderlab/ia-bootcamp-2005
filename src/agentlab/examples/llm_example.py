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
    
    # Initialize LLM with default parameters (API key from environment)
    llm = LangChainLLM(model_name="gpt-3.5-turbo")
    
    # Generate text
    prompt = "Explain what is machine learning in one sentence."
    response = llm.generate(prompt, temperature=0.7, max_tokens=100)
    
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")


def example_chat():
    """Example: Chat conversation."""
    print("\n=== Example 2: Chat Conversation ===")
    
    # Initialize LLM with custom default parameters
    llm = LangChainLLM(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=500
    )
    
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
    
    # Generate response (uses instance defaults: temperature=0.7, max_tokens=500)
    response = llm.chat(messages)
    
    print("Conversation:")
    for msg in messages[-2:]:
        print(f"{msg.role.capitalize()}: {msg.content}")
    print(f"Assistant: {response}")


def example_custom_parameters():
    """Example: Using custom parameters."""
    print("\n=== Example 3: Custom Parameters ===")
    
    # Initialize with custom model and instance defaults
    llm = LangChainLLM(
        model_name="gpt-4",
        temperature=0.5,
        max_tokens=200
    )
    
    # Generate with low temperature for more deterministic output
    prompt = "List three programming languages."
    response = llm.generate(prompt, temperature=0.2, max_tokens=50)
    
    print(f"Prompt: {prompt}")
    print(f"Response (deterministic with temp=0.2): {response}")


def example_chat_with_parameters():
    """Example: Chat with override parameters."""
    print("\n=== Example 4: Chat with Custom Parameters ===")
    
    # Initialize with default parameters
    llm = LangChainLLM(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=1000
    )
    
    # Create conversation
    messages = [
        ChatMessage(
            role="system",
            content="You are a concise technical assistant.",
            timestamp=datetime.now(),
        ),
        ChatMessage(
            role="user",
            content="Explain the SOLID principles.",
            timestamp=datetime.now(),
        ),
    ]
    
    # Generate response with overridden parameters for concise output
    response = llm.chat(messages, temperature=0.5, max_tokens=300)
    
    print("System: You are a concise technical assistant.")
    print("User: Explain the SOLID principles.")
    print(f"Assistant (with temp=0.5, max_tokens=300): {response}")


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
        example_chat_with_parameters()
        
        print("\n✅ All examples completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
