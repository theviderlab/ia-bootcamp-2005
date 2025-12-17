"""
Unit tests for runtime configuration models.

Tests validation and behavior of configuration models.
"""

import pytest
from pydantic import ValidationError

from agentlab.models.config_models import (
    ConfigurationStatus,
    MemoryToggles,
    RAGToggles,
    RuntimeConfig,
)


def test_memory_toggles_defaults():
    """Test MemoryToggles with default values."""
    toggles = MemoryToggles()
    
    assert toggles.enable_short_term is True
    assert toggles.enable_semantic is True
    assert toggles.enable_episodic is True
    assert toggles.enable_profile is True
    assert toggles.enable_procedural is True


def test_memory_toggles_custom():
    """Test MemoryToggles with custom values."""
    toggles = MemoryToggles(
        enable_short_term=True,
        enable_semantic=False,
        enable_episodic=True,
        enable_profile=False,
        enable_procedural=True,
    )
    
    assert toggles.enable_short_term is True
    assert toggles.enable_semantic is False
    assert toggles.enable_episodic is True
    assert toggles.enable_profile is False
    assert toggles.enable_procedural is True


def test_rag_toggles_defaults():
    """Test RAGToggles with default values."""
    toggles = RAGToggles()
    
    assert toggles.enable_rag is False  # Default is disabled
    assert toggles.namespaces == []
    assert toggles.top_k == 5


def test_rag_toggles_with_namespaces():
    """Test RAGToggles with specific namespaces."""
    toggles = RAGToggles(
        enable_rag=True,
        namespaces=["docs", "tutorials", "examples"],
        top_k=10,
    )
    
    assert toggles.enable_rag is True
    assert len(toggles.namespaces) == 3
    assert "docs" in toggles.namespaces
    assert toggles.top_k == 10


def test_rag_toggles_validation():
    """Test RAGToggles validation for top_k."""
    # Valid range
    toggles = RAGToggles(top_k=5)
    assert toggles.top_k == 5
    
    # Test boundaries
    toggles_min = RAGToggles(top_k=1)
    assert toggles_min.top_k == 1
    
    toggles_max = RAGToggles(top_k=20)
    assert toggles_max.top_k == 20
    
    # Invalid values should raise validation error
    with pytest.raises(ValidationError):
        RAGToggles(top_k=0)
    
    with pytest.raises(ValidationError):
        RAGToggles(top_k=21)


def test_runtime_config_creation():
    """Test RuntimeConfig with all components."""
    config = RuntimeConfig(
        session_id="test-session-123",
        memory=MemoryToggles(enable_semantic=False),
        rag=RAGToggles(enable_rag=True, namespaces=["docs"]),
        metadata={"user": "test_user"},
    )
    
    assert config.session_id == "test-session-123"
    assert config.memory.enable_semantic is False
    assert config.rag.enable_rag is True
    assert config.rag.namespaces == ["docs"]
    assert config.metadata["user"] == "test_user"


def test_runtime_config_defaults():
    """Test RuntimeConfig with default toggles."""
    config = RuntimeConfig(session_id="test-session")
    
    assert config.session_id == "test-session"
    assert isinstance(config.memory, MemoryToggles)
    assert isinstance(config.rag, RAGToggles)
    assert config.metadata is None


def test_configuration_status():
    """Test ConfigurationStatus model."""
    default_config = RuntimeConfig(
        session_id="default",
        memory=MemoryToggles(),
        rag=RAGToggles(),
    )
    
    status = ConfigurationStatus(
        memory_available=True,
        rag_available=False,
        current_config=default_config,
        warnings=["RAG service unavailable"],
        dependencies={"mysql": True, "pinecone": False},
    )
    
    assert status.memory_available is True
    assert status.rag_available is False
    assert status.current_config.session_id == "default"
    assert len(status.warnings) == 1
    assert status.dependencies["mysql"] is True
    assert status.dependencies["pinecone"] is False


def test_configuration_status_no_warnings():
    """Test ConfigurationStatus without warnings."""
    default_config = RuntimeConfig(
        session_id="default",
        memory=MemoryToggles(),
        rag=RAGToggles(),
    )
    
    status = ConfigurationStatus(
        memory_available=True,
        rag_available=True,
        current_config=default_config,
    )
    
    assert status.warnings is None or status.warnings == []


def test_model_serialization():
    """Test that models can be serialized to JSON."""
    config = RuntimeConfig(
        session_id="test",
        memory=MemoryToggles(enable_semantic=False),
        rag=RAGToggles(enable_rag=True, namespaces=["ns1", "ns2"]),
    )
    
    # Convert to dict
    config_dict = config.model_dump()
    
    assert config_dict["session_id"] == "test"
    assert config_dict["memory"]["enable_semantic"] is False
    assert config_dict["rag"]["enable_rag"] is True
    assert len(config_dict["rag"]["namespaces"]) == 2


def test_model_deserialization():
    """Test that models can be created from dict."""
    data = {
        "session_id": "test",
        "memory": {
            "enable_short_term": True,
            "enable_semantic": False,
            "enable_episodic": True,
            "enable_profile": False,
            "enable_procedural": True,
        },
        "rag": {
            "enable_rag": True,
            "namespaces": ["docs"],
            "top_k": 7,
        },
    }
    
    config = RuntimeConfig(**data)
    
    assert config.session_id == "test"
    assert config.memory.enable_semantic is False
    assert config.rag.namespaces == ["docs"]
    assert config.rag.top_k == 7
