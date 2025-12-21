# MCP (Model Context Protocol) Tools

Comprehensive guide to using and extending the MCP tools infrastructure in AgentLab.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Using Existing Tools](#using-existing-tools)
- [Creating Custom Tools](#creating-custom-tools)
- [Tool Input/Output Schemas](#tool-inputoutput-schemas)
- [Error Handling](#error-handling)
- [Testing Tools](#testing-tools)
- [Registry Management](#registry-management)
- [LangChain Integration](#langchain-integration)
- [API Endpoints](#api-endpoints)

---

## Overview

MCP (Model Context Protocol) tools provide a standardized way for LLMs to interact with external functionality. Tools are:

- **Discoverable**: Tools expose their capabilities through structured schemas
- **Validated**: Inputs and outputs are validated using Pydantic models
- **Async-first**: All tools use async/await for optimal performance
- **LangChain-compatible**: Tools can be converted to LangChain format
- **Integrated with Chat**: Autonomous tool execution with memory persistence

### Built-in Tools

- **`get_current_datetime`**: Returns current date/time with format and timezone support

### Integration with Chat System

Tools are integrated with the chat system through a ReAct-style agent pattern:

1. **Autonomous Execution**: The LLM decides when to call tools based on the user's query
2. **Memory Persistence**: Tool calls and results are stored in conversation history
3. **Context Integration**: Tool results are included in the context builder for subsequent turns
4. **Iterative Reasoning**: The agent can call multiple tools sequentially until reaching a final answer

**Data Models** (defined in `src/agentlab/models/__init__.py`):

```python
@dataclass
class ToolCall:
    """Represents a tool call made by the LLM."""
    tool_name: str
    tool_args: dict[str, Any]
    call_id: str
    timestamp: datetime | None = None

@dataclass
class ToolResult:
    """Result from executing a tool call."""
    tool_name: str
    success: bool
    result: dict[str, Any]
    error: str | None = None
    call_id: str
    timestamp: datetime | None = None

@dataclass
class AgentStep:
    """Represents a single step in the agent's reasoning process."""
    step_number: int
    tool_name: str
    tool_args: dict[str, Any]
    result: dict[str, Any]
    reasoning: str | None = None
```

**Memory Storage**: Tool calls and results are stored with `metadata.is_tool_call=True` in the chat history, allowing filtering and analytics.

---

## Architecture

```
agentlab/mcp/
├── __init__.py           # Public API exports
├── base.py               # Base classes (MCPToolBase, MCPToolInput, MCPToolOutput)
├── registry.py           # Tool registry and management
└── tools/
    ├── __init__.py
    └── datetime_tool.py  # DateTimeTool implementation
```

### Key Components

1. **MCPToolBase**: Abstract base class for all tools
2. **MCPToolInput**: Base Pydantic model for tool inputs
3. **MCPToolOutput**: Base Pydantic model for tool outputs (optional)
4. **MCPToolRegistry**: Centralized tool registration and discovery

---

## Using Existing Tools

### Via API

```bash
# List all available tools
curl http://localhost:8000/mpc/tools/names

# Get detailed tool information
curl http://localhost:8000/mpc/tools/get_current_datetime

# List all tools with metadata
curl http://localhost:8000/mpc/tools
```

### Via Python

```python
from agentlab.mcp import get_registry

# Get the global registry
registry = get_registry()

# List all tools
tool_names = registry.list_tools()
print(f"Available tools: {tool_names}")

# Get a specific tool
datetime_tool = registry.get_tool("get_current_datetime")

# Execute a tool
result = await datetime_tool.execute(format="iso", timezone="America/New_York")
print(result)
# {'success': True, 'datetime': '2025-12-21T10:30:00-05:00', ...}
```

### With LangChain

```python
from agentlab.mcp import get_registry
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Get tools in LangChain format
registry = get_registry()
tools = registry.get_langchain_tools()

# Bind tools to LLM
llm = ChatOpenAI(model="gpt-4")
llm_with_tools = llm.bind_tools(tools)

# Use tools
messages = [HumanMessage(content="What time is it in New York?")]
response = llm_with_tools.invoke(messages)

if response.tool_calls:
    for tool_call in response.tool_calls:
        # Handle tool calls
        pass
```

### Integrated Chat with Tools

```python
from agentlab.core.llm_interface import LangChainLLM
from agentlab.mcp import get_registry
from agentlab.models import ChatMessage
from datetime import datetime

# Initialize LLM
llm = LangChainLLM()

# Get tools
registry = get_registry()
langchain_tools = registry.get_langchain_tools()

# Prepare messages
messages = [
    ChatMessage(
        role="user",
        content="What time is it in Tokyo?",
        timestamp=datetime.now()
    )
]

# Chat with tools (async)
response, agent_steps, tool_results = await llm.chat_with_tools(
    messages=messages,
    tools=langchain_tools,
    max_iterations=5
)

print(f"Response: {response}")
print(f"Tools used: {len(tool_results)}")

for step in agent_steps:
    print(f"Step {step.step_number}: Called {step.tool_name}")
    print(f"  Args: {step.tool_args}")
    print(f"  Result: {step.result}")
```

### Via API with Memory

```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What time is it in London?"}
    ],
    "session_id": "user-123",
    "use_tools": true,
    "use_memory": true,
    "available_tools": ["get_current_datetime"]
  }'
```

**Response includes:**
- `tools_used`: Boolean indicating if tools were executed
- `tool_calls`: List of tool invocations with arguments
- `tool_results`: Results of tool executions
- `agent_steps`: Reasoning steps taken by the agent

**Memory Integration**: Tool calls and results are automatically stored in the session's conversation history with metadata, enabling:
- Future reference to tool usage patterns
- Context-aware follow-up questions
- Analytics on tool effectiveness
        print(f"Tool: {tool_call['name']}")
        print(f"Args: {tool_call['args']}")
```

---

## Creating Custom Tools

### Step 1: Define Input/Output Schemas

```python
from pydantic import Field
from agentlab.mcp.base import MCPToolInput, MCPToolOutput

class CalculatorInput(MCPToolInput):
    """Input schema for calculator tool."""
    
    operation: Literal["add", "subtract", "multiply", "divide"] = Field(
        description="Mathematical operation to perform"
    )
    a: float = Field(description="First operand")
    b: float = Field(description="Second operand")


class CalculatorOutput(MCPToolOutput):
    """Output schema for calculator tool."""
    
    success: bool = Field(description="Whether calculation succeeded")
    result: float | None = Field(default=None, description="Calculation result")
    error: str | None = Field(default=None, description="Error message if failed")
```

### Step 2: Implement Tool Class

```python
from typing import Any
from agentlab.mcp.base import MCPToolBase

class CalculatorTool(MCPToolBase):
    """Tool for basic arithmetic operations."""
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return (
            "Perform basic arithmetic operations (add, subtract, multiply, divide). "
            "Use this tool when you need to calculate numerical results."
        )
    
    @property
    def input_schema(self) -> type[CalculatorInput]:
        return CalculatorInput
    
    @property
    def output_schema(self) -> type[CalculatorOutput]:
        return CalculatorOutput
    
    async def execute(self, **kwargs) -> dict[str, Any]:
        """Execute the calculation."""
        inputs = CalculatorInput(**kwargs)
        
        try:
            if inputs.operation == "add":
                result = inputs.a + inputs.b
            elif inputs.operation == "subtract":
                result = inputs.a - inputs.b
            elif inputs.operation == "multiply":
                result = inputs.a * inputs.b
            elif inputs.operation == "divide":
                if inputs.b == 0:
                    return {
                        "success": False,
                        "result": None,
                        "error": "Division by zero"
                    }
                result = inputs.a / inputs.b
            else:
                return {
                    "success": False,
                    "result": None,
                    "error": f"Unknown operation: {inputs.operation}"
                }
            
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }
```

### Step 3: Register the Tool

**Option A: Auto-register (recommended for built-in tools)**

Edit `src/agentlab/mcp/registry.py`:

```python
def _register_builtin_tools(self) -> None:
    """Register all built-in tools."""
    try:
        self.register(DateTimeTool())
        self.register(CalculatorTool())  # Add your tool
        logger.info("Registered built-in tools: datetime, calculator")
    except Exception as e:
        logger.error(f"Failed to register built-in tools: {e}")
```

**Option B: Manual registration**

```python
from agentlab.mcp import get_registry
from mytools import CalculatorTool

# Get registry and register tool
registry = get_registry()
registry.register(CalculatorTool())
```

---

## Tool Input/Output Schemas

### Best Practices

1. **Use descriptive field names**
   ```python
   # Good
   temperature: float = Field(description="Temperature in Celsius")
   
   # Bad
   temp: float  # No description
   ```

2. **Add validation constraints**
   ```python
   temperature: float = Field(ge=-273.15, le=1000, description="Temperature in Celsius")
   percentage: float = Field(ge=0.0, le=100.0)
   count: int = Field(gt=0)
   ```

3. **Use Literal for enums**
   ```python
   format: Literal["json", "xml", "csv"] = Field(default="json")
   ```

4. **Make fields optional when appropriate**
   ```python
   timezone: str | None = Field(default=None, description="Optional timezone")
   ```

5. **Always include success/error fields in outputs**
   ```python
   class MyToolOutput(MCPToolOutput):
       success: bool
       result: Any | None = None
       error: str | None = None
   ```

### Schema Validation

Input validation happens automatically in `execute_with_validation()`:

```python
# This is called automatically by LangChain integration
result = await tool.execute_with_validation(
    operation="add",
    a=5,
    b=3
)
```

---

## Error Handling

### Return Error in Result (Recommended)

```python
async def execute(self, **kwargs) -> dict[str, Any]:
    try:
        # ... tool logic ...
        return {
            "success": True,
            "result": data,
            "error": None
        }
    except SpecificError as e:
        return {
            "success": False,
            "result": None,
            "error": f"Specific error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": f"Unexpected error: {str(e)}"
        }
```

### Raise Exception (For critical errors only)

```python
async def execute(self, **kwargs) -> dict[str, Any]:
    if critical_resource_missing:
        raise RuntimeError("Critical resource not available")
    
    # Normal execution...
```

### Error Patterns

| Situation | Pattern | Example |
|-----------|---------|---------|
| Invalid input | Return error | `{"success": False, "error": "Invalid timezone"}` |
| Operation failed | Return error | `{"success": False, "error": "API timeout"}` |
| Partial success | Return with warning | `{"success": True, "result": data, "warning": "..."}` |
| Critical failure | Raise exception | `raise RuntimeError("Database unavailable")` |

---

## Testing Tools

### Unit Test Template

```python
import pytest
from mytools import MyTool, MyToolInput, MyToolOutput

@pytest.mark.asyncio
async def test_my_tool_success():
    """Test successful tool execution."""
    tool = MyTool()
    
    result = await tool.execute(param1="value1", param2="value2")
    
    assert result["success"] is True
    assert "result" in result
    assert result["error"] is None


@pytest.mark.asyncio
async def test_my_tool_invalid_input():
    """Test tool with invalid input."""
    tool = MyTool()
    
    with pytest.raises(ValueError, match="Input validation failed"):
        await tool.execute_with_validation(invalid_param="bad")


@pytest.mark.asyncio
async def test_my_tool_error_handling():
    """Test tool error handling."""
    tool = MyTool()
    
    result = await tool.execute(param_that_causes_error="trigger")
    
    assert result["success"] is False
    assert result["error"] is not None


def test_my_tool_metadata():
    """Test tool metadata."""
    tool = MyTool()
    metadata = tool.get_metadata()
    
    assert metadata["name"] == "my_tool"
    assert "description" in metadata
    assert "input_schema" in metadata
    assert "output_schema" in metadata
```

### Testing with Registry

```python
import pytest
from agentlab.mcp.registry import MCPToolRegistry, reset_registry

@pytest.fixture(autouse=True)
def reset_test_registry():
    """Reset registry before each test."""
    reset_registry()
    yield
    reset_registry()


def test_tool_registration():
    """Test registering custom tool."""
    registry = MCPToolRegistry()
    tool = MyTool()
    
    registry.register(tool)
    
    assert registry.has_tool("my_tool")
    assert registry.get_tool("my_tool") == tool
```

---

## Registry Management

### Singleton Pattern

The registry uses a singleton pattern for global access:

```python
from agentlab.mcp import get_registry

# Always returns the same instance
registry1 = get_registry()
registry2 = get_registry()
assert registry1 is registry2
```

### Registry Operations

```python
from agentlab.mcp import get_registry, reset_registry

registry = get_registry()

# List tools
tools = registry.list_tools()

# Check if tool exists
if registry.has_tool("calculator"):
    tool = registry.get_tool("calculator")

# Get tool metadata
info = registry.get_tool_info("calculator")

# Get LangChain tools
langchain_tools = registry.get_langchain_tools()

# Get specific tools for LangChain
specific_tools = registry.get_langchain_tools(["calculator", "get_current_datetime"])

# Reset registry (testing only)
reset_registry()
```

---

## LangChain Integration

### Binding Tools to LLM

```python
from langchain_openai import ChatOpenAI
from agentlab.mcp import get_registry

# Get tools
registry = get_registry()
tools = registry.get_langchain_tools()

# Create LLM with tools
llm = ChatOpenAI(model="gpt-4")
llm_with_tools = llm.bind_tools(tools)
```

### Tool Execution Loop

```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

async def chat_with_tools(user_message: str):
    """Chat with tool support."""
    messages = [HumanMessage(content=user_message)]
    
    while True:
        # Get LLM response
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)
        
        # Check if LLM wants to use tools
        if not response.tool_calls:
            return response.content
        
        # Execute each tool call
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Get tool from registry
            tool = registry.get_tool(tool_name)
            if tool is None:
                result = {"success": False, "error": f"Tool {tool_name} not found"}
            else:
                result = await tool.execute(**tool_args)
            
            # Add tool result to messages
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
            )
```

---

## API Endpoints

### GET `/mpc/tools`

List all available tools with full metadata.

**Response:**
```json
[
  {
    "name": "get_current_datetime",
    "description": "Get the current date and time...",
    "input_schema": {
      "type": "object",
      "properties": {
        "format": {...},
        "timezone": {...}
      }
    },
    "output_schema": {...}
  }
]
```

### GET `/mpc/tools/names`

List tool names only.

**Response:**
```json
{
  "tools": ["get_current_datetime", "calculator"],
  "count": 2
}
```

### GET `/mpc/tools/{tool_name}`

Get detailed information about a specific tool.

**Response:**
```json
{
  "name": "get_current_datetime",
  "description": "Get the current date and time...",
  "input_schema": {...},
  "output_schema": {...}
}
```

**Error (404):**
```json
{
  "detail": "Tool 'unknown_tool' not found"
}
```

---

## Advanced Topics

### Async vs Sync Tools

All tools must be async. If you need to wrap sync code:

```python
import asyncio

async def execute(self, **kwargs) -> dict[str, Any]:
    # Wrap blocking code
    result = await asyncio.to_thread(blocking_function, arg1, arg2)
    return {"success": True, "result": result}
```

### Tool Dependencies

If a tool needs external services:

```python
class WebSearchTool(MCPToolBase):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def execute(self, **kwargs):
        # Use self.api_key
        pass

# Register with dependencies
from myapp.config import get_api_key
registry.register(WebSearchTool(api_key=get_api_key()))
```

### Conditional Tool Registration

```python
def _register_builtin_tools(self) -> None:
    """Register tools based on environment."""
    # Always register
    self.register(DateTimeTool())
    
    # Conditional registration
    if os.getenv("ENABLE_WEB_SEARCH"):
        self.register(WebSearchTool())
    
    if os.getenv("DATABASE_URL"):
        self.register(DatabaseTool())
```

---

## Architecture Decisions

### 1. Tool Result Context Integration

**Decision**: Add "Tool Execution Results" as dedicated markdown section in context  
**Rationale**:
- Clear separation from memory/RAG context
- Easy for LLM to parse and reference
- Maintains context structure consistency
- Allows for future enhancements (e.g., selective tool result inclusion)

**Implementation**: The `ContextBuilder` formats tool results as:
```markdown
## Tool Execution Results

### Tool 1: `get_current_datetime` (✅ Success)
**Time**: 10:30:00
**Call ID**: call_123
**Result**:
- **success**: True
- **datetime**: 2025-12-21T10:30:00
- **format**: iso
```

### 2. Memory Persistence

**Decision**: Store tool calls with `metadata.is_tool_call=True` flag  
**Rationale**:
- Reuses existing `ChatMessage.metadata` field
- Enables filtering in memory retrieval
- Minimal schema changes
- Supports future analytics on tool usage

**Storage Format**:
```python
# Tool call message
ChatMessage(
    role="assistant",
    content="",
    metadata={
        "is_tool_call": True,
        "tool_name": "get_current_datetime",
        "tool_args": {"format": "iso"},
        "call_id": "call_123"
    }
)

# Tool result message
ChatMessage(
    role="system",
    content="Tool result: ...",
    metadata={
        "is_tool_call": True,
        "tool_result": {...},
        "tool_success": True,
        "call_id": "call_123"
    }
)
```

### 3. Backward Compatibility

**Decision**: Default `use_tools=False` in chat endpoint  
**Rationale**:
- Existing API consumers unaffected
- Explicit opt-in for new functionality
- No performance overhead when disabled

### 4. ReAct Agent Pattern

**Decision**: Implement iterative tool calling with max iterations guard  
**Rationale**:
- Allows multi-step reasoning
- Prevents infinite loops
- Follows industry best practices (ReAct paper)
- LangChain native support

**Flow**:
1. LLM receives message + available tools
2. LLM decides: answer directly OR call tool
3. If tool call: execute → add result → repeat
4. Continue until final answer or max iterations

### 5. Error Handling Strategy

**Decision**: Return errors in ToolResult instead of raising exceptions  
**Rationale**:
- Allows LLM to handle errors gracefully
- Agent can retry or request clarification
- Maintains conversation flow
- Better user experience

### 6. Async-First Design

**Decision**: All tool execution is async  
**Rationale**:
- Non-blocking I/O operations
- Better performance for external API calls
- Scales with concurrent requests
- FastAPI native support

---

## Best Practices

### Tool Design

1. **Single Responsibility**: Each tool should do one thing well
2. **Clear Names**: Use descriptive, verb-based names (e.g., `get_current_datetime`, not `datetime_tool`)
3. **Comprehensive Schemas**: Provide detailed field descriptions for LLM guidance
4. **Graceful Degradation**: Return partial results on non-critical errors
5. **Idempotency**: Tools should be safe to call multiple times with same inputs

### Security Considerations

1. **Input Validation**: Always validate and sanitize tool inputs
2. **Rate Limiting**: Implement rate limits for expensive operations
3. **Authentication**: Require auth for sensitive operations
4. **Audit Logging**: Log all tool executions with user context
5. **Sandboxing**: Isolate tool execution from main application

### Performance Optimization

1. **Caching**: Cache expensive tool results when appropriate
2. **Timeouts**: Set reasonable timeouts for external calls
3. **Parallel Execution**: Execute independent tools concurrently
4. **Lazy Loading**: Only load tool dependencies when needed
5. **Connection Pooling**: Reuse connections for repeated API calls

---

## Next Steps

- **Phase 3**: Add more built-in tools (web search, file operations, calculator)
- **Phase 4**: Tool authentication and rate limiting
- **Phase 5**: Tool composition and chaining
- **Phase 6**: Tool marketplace and discovery

For questions or contributions, see the main project README.