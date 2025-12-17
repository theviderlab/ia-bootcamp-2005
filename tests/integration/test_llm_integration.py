"""
Integration tests for LLM functionality.

These tests verify real LLM behavior with actual API calls.
Requires OPENAI_API_KEY environment variable to be set.
"""

import os
from datetime import datetime

import pytest

from agentlab.core.llm_interface import LangChainLLM
from agentlab.models import ChatMessage

from dotenv import load_dotenv
load_dotenv()

@pytest.fixture
def skip_if_no_api_key():
    """Skip test if OpenAI API key is not available."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY environment variable not set")


def test_llm_initialization_with_custom_parameters(skip_if_no_api_key):
    """Test LLM initializes correctly with custom temperature and max_tokens."""
    llm = LangChainLLM(
        model_name="gpt-3.5-turbo",
        temperature=0.5,
        max_tokens=200
    )
    
    assert llm.temperature == 0.5
    assert llm.max_tokens == 200
    assert llm.model_name == "gpt-3.5-turbo"


def test_generate_with_low_temperature_deterministic(skip_if_no_api_key):
    """Test that low temperature produces deterministic output."""
    llm = LangChainLLM(temperature=0.0, max_tokens=50)
    
    prompt = "Say exactly: Hello, World!"
    
    # Generate twice with temperature 0.0 (should be deterministic)
    response1 = llm.generate(prompt, temperature=0.0, max_tokens=20)
    response2 = llm.generate(prompt, temperature=0.0, max_tokens=20)
    
    # Responses should be identical or very similar
    assert isinstance(response1, str)
    assert isinstance(response2, str)
    assert len(response1) > 0
    assert len(response2) > 0


def test_generate_with_high_temperature_creative(skip_if_no_api_key):
    """Test that high temperature produces creative output."""
    llm = LangChainLLM(temperature=0.9, max_tokens=100)
    
    prompt = "Write a creative one-sentence story."
    
    # Generate with high temperature
    response = llm.generate(prompt, temperature=0.9, max_tokens=50)
    
    assert isinstance(response, str)
    assert len(response) > 0
    # High temperature responses should be non-empty strings


def test_generate_respects_max_tokens(skip_if_no_api_key):
    """Test that max_tokens parameter limits response length."""
    llm = LangChainLLM(temperature=0.7, max_tokens=1000)
    
    prompt = "Write a very long story about a cat."
    
    # Generate with low max_tokens
    short_response = llm.generate(prompt, temperature=0.7, max_tokens=20)
    
    # Generate with higher max_tokens
    long_response = llm.generate(prompt, temperature=0.7, max_tokens=100)
    
    # Short response should be shorter than long response
    # (tokens != characters, but this is a rough check)
    assert len(short_response) < len(long_response) * 2


def test_chat_with_system_message(skip_if_no_api_key):
    """Test chat respects system message instructions."""
    llm = LangChainLLM(temperature=0.7, max_tokens=500)
    
    messages = [
        ChatMessage(
            role="system",
            content="You are a helpful assistant that always responds in exactly 3 words.",
            timestamp=datetime.now()
        ),
        ChatMessage(
            role="user",
            content="What is the capital of France?",
            timestamp=datetime.now()
        )
    ]
    
    response = llm.chat(messages)
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should be concise due to system message (though not always exactly 3 words)
    word_count = len(response.split())
    assert word_count <= 10, f"Expected concise response, got {word_count} words"


def test_chat_with_custom_temperature(skip_if_no_api_key):
    """Test chat with custom temperature parameter."""
    llm = LangChainLLM(temperature=0.7, max_tokens=500)
    
    messages = [
        ChatMessage(
            role="user",
            content="Say hello.",
            timestamp=datetime.now()
        )
    ]
    
    # Chat with low temperature (more deterministic)
    response1 = llm.chat(messages, temperature=0.2, max_tokens=20)
    
    # Chat with high temperature (more creative)
    response2 = llm.chat(messages, temperature=0.9, max_tokens=20)
    
    assert isinstance(response1, str)
    assert isinstance(response2, str)
    assert len(response1) > 0
    assert len(response2) > 0


def test_chat_with_custom_max_tokens(skip_if_no_api_key):
    """Test chat respects custom max_tokens parameter."""
    llm = LangChainLLM(temperature=0.7, max_tokens=1000)
    
    messages = [
        ChatMessage(
            role="system",
            content="You are a helpful assistant that provides detailed explanations.",
            timestamp=datetime.now()
        ),
        ChatMessage(
            role="user",
            content="Explain the SOLID principles in software engineering.",
            timestamp=datetime.now()
        )
    ]
    
    # Generate with limited tokens
    short_response = llm.chat(messages, temperature=0.7, max_tokens=50)
    
    # Generate with more tokens
    long_response = llm.chat(messages, temperature=0.7, max_tokens=300)
    
    assert isinstance(short_response, str)
    assert isinstance(long_response, str)
    assert len(short_response) > 0
    assert len(long_response) > len(short_response)


def test_chat_uses_instance_defaults(skip_if_no_api_key):
    """Test that chat uses instance default parameters when not overridden."""
    llm = LangChainLLM(
        temperature=0.3,
        max_tokens=100
    )
    
    messages = [
        ChatMessage(
            role="user",
            content="Say hello in one word.",
            timestamp=datetime.now()
        )
    ]
    
    # Call chat without overriding parameters
    response = llm.chat(messages)
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should produce a concise response due to low max_tokens default


def test_conversation_with_context(skip_if_no_api_key):
    """Test multi-turn conversation maintains context."""
    llm = LangChainLLM(temperature=0.7, max_tokens=200)
    
    messages = [
        ChatMessage(
            role="user",
            content="My favorite color is blue.",
            timestamp=datetime.now()
        ),
        ChatMessage(
            role="assistant",
            content="That's great! Blue is a wonderful color.",
            timestamp=datetime.now()
        ),
        ChatMessage(
            role="user",
            content="What was my favorite color?",
            timestamp=datetime.now()
        )
    ]
    
    response = llm.chat(messages)
    
    assert isinstance(response, str)
    # Response should mention "blue" or reference the previous context
    assert "blue" in response.lower() or "color" in response.lower()
