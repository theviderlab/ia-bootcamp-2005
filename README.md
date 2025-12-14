# Agent Lab

A modern Python learning platform for experimenting with **Large Language Models (LLMs)**, **Model Context Protocol (MCP)** servers/clients, and **Retrieval Augmented Generation (RAG)** systems. Built with [uv](https://docs.astral.sh/uv/) for fast dependency management, FastAPI for the backend, and LangChain for LLM integration.

## 🎯 Purpose

Agent Lab is designed for learning and experimentation with:
- **LLM Integration**: Using LangChain to interact with OpenAI, Anthropic, and other providers
- **MCP Protocol**: Implementing Anthropic's Model Context Protocol for server/client communication
- **RAG Systems**: Building Retrieval Augmented Generation with vector embeddings and MySQL
- **API Development**: Creating production-ready FastAPI applications

## 🏗️ Architecture

```
agentlab/
├── frontend/                     # Frontend application (React/Vue)
│   ├── src/
│   │   └── components/
│   │       ├── Chat.jsx          # Chat interface
│   │       ├── MPCManager.jsx    # MPC instance management
│   │       └── RAGViewer.jsx     # RAG visualization
│   └── README.md
│
├── src/agentlab/                 # Python backend package
│   ├── database/                 # Database layer
│   │   ├── config.py             # MySQL connection config
│   │   ├── models.py             # Table schemas
│   │   └── crud.py               # CRUD operations
│   │
│   ├── core/                     # Core business logic
│   │   ├── rag_service.py        # RAG implementation
│   │   ├── mpc_manager.py        # MPC instance manager
│   │   └── llm_interface.py      # LangChain LLM wrapper
│   │
│   ├── agents/                   # Low-level implementations
│   │   ├── rag_processor.py      # Embedding & retrieval
│   │   ├── mpc_client_base.py    # MPC client base class
│   │   └── mpc_server_base.py    # MPC server base class
│   │
│   ├── api/                      # FastAPI application
│   │   ├── main.py               # FastAPI app entry point
│   │   └── routes/
│   │       ├── chat_routes.py    # Chat & RAG endpoints
│   │       └── mpc_routes.py     # MPC management endpoints
│   │
│   ├── models.py                 # Data models & Protocols
│   └── main.py                   # CLI entry point
│
├── data/                         # Static data & configurations
│   ├── initial_knowledge/        # RAG knowledge base documents
│   ├── examples/                 # Example queries
│   └── configs/                  # Config files
│
├── tests/
│   ├── unit/                     # Unit tests with mocks
│   └── integration/              # Integration tests
│
├── pyproject.toml                # Dependencies & configuration
├── Makefile                      # Development automation
├── AGENTS.md                     # AI coding assistant guidelines
└── README.md                     # This file
```

## 🚀 Features

- **Fast Package Management**: Uses `uv` for lightning-fast dependency resolution
- **Modern Python**: Python 3.12+ with type hints and Protocols
- **FastAPI Backend**: Production-ready REST API with automatic documentation
- **LangChain Integration**: Unified interface for multiple LLM providers
- **MCP Support**: Anthropic's Model Context Protocol implementation
- **RAG System**: Vector embeddings with MySQL storage
- **Testing Ready**: Pre-configured pytest with unit and integration tests
- **Code Quality**: Ruff for formatting and linting
- **SOLID Principles**: Clean architecture with dependency injection

## 📋 Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- MySQL 8.0+ (for database)
- Node.js 18+ (for frontend, optional)

## 🛠️ Installation

### 1. Install uv (if not already installed)

**Windows:**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/theviderlab/ia-bootcamp-2005
cd ia-bootcamp-2005

# Sync dependencies (creates .venv and installs packages)
uv sync

# Or use Make
make install

# OPCIONAL: Instalar el paquete en modo editable para importarlo sin uv run
uv pip install -e .
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
# - Database configuration (MySQL)
# - OpenAI API key
# - Anthropic API key (optional)
```

Required environment variables:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=agent_lab

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Setup Database

```bash
# Initialize MySQL database and tables
make setup-db
```

## 🎯 Usage

### Important: Using uv run

Con el layout `src/`, hay dos formas de ejecutar código:

**Opción 1: Usando `uv run` (Recomendado)**
```bash
# uv run configura automáticamente el entorno
uv run python script.py
uv run python -m agentlab.main
```

**Opción 2: Instalar en modo editable**
```bash
# Instalar una vez
uv pip install -e .

# Luego ejecutar normalmente
python script.py
```

### Running the FastAPI Server

```bash
# Start the API server (with auto-reload)
make api

# Or directly with uvicorn
uv run uvicorn agentlab.api.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### API Endpoints

**Chat & RAG:**
- `POST /api/chat/message` - Send a chat message
- `POST /api/chat/rag/query` - Query the RAG system
- `POST /api/chat/rag/documents` - Add documents to knowledge base

**MCP Management:**
- `POST /api/mpc/instances` - Create MPC server instance
- `GET /api/mpc/instances` - List all instances
- `GET /api/mpc/instances/{id}` - Get instance status
- `DELETE /api/mpc/instances/{id}` - Stop instance

### Running the CLI

```bash
# Run the main CLI application
make main

# Or directly
uv run python -m agentlab.main
```

### Development Commands

```bash
make help              # Show all available commands
make install           # Install/sync dependencies
make api               # Start FastAPI server
make setup-db          # Initialize database
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make format            # Format code with Ruff
make lint              # Lint code with Ruff
make pre-commit        # Run pre-commit checks
make clean             # Clean cache files
```

## 🧪 Testing

The project uses pytest with separation between unit and integration tests:

- **Unit Tests** ([tests/unit/](tests/unit/)): Fast, isolated tests using mocks
- **Integration Tests** ([tests/integration/](tests/integration/)): Tests with real APIs/services

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only  
make test-integration

# With verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=src/agentlab

# Specific test file
uv run pytest tests/unit/test_specific.py
```

## 🤖 LLM Integration

### Using LangChainLLM

The project includes a fully implemented LLM interface using LangChain for interacting with OpenAI models.

**Quick Start:**

```python
from agentlab.core.llm_interface import LangChainLLM
from agentlab.models import ChatMessage
from datetime import datetime

# Initialize LLM
llm = LangChainLLM(model_name="gpt-3.5-turbo")

# Simple text generation
response = llm.generate(
    prompt="Explain machine learning in one sentence",
    temperature=0.7,
    max_tokens=100
)

# Chat with conversation history
messages = [
    ChatMessage(
        role="system",
        content="You are a helpful assistant",
        timestamp=datetime.now()
    ),
    ChatMessage(
        role="user",
        content="What is Python?",
        timestamp=datetime.now()
    ),
]
response = llm.chat(messages)
```

**Features:**
- ✅ Text generation with customizable parameters
- ✅ Chat conversations with history
- ✅ Support for system, user, and assistant roles
- ✅ Error handling and validation
- ✅ Multiple model support (GPT-3.5, GPT-4)

**Run the example:**
```bash
# Make sure OPENAI_API_KEY is set
export OPENAI_API_KEY="your-api-key"

# Run example script
uv run python -m agentlab.examples.llm_example

# Or run basic tests
uv run python test_llm_basic.py
```

**Full documentation:** [docs/llm_interface_guide.md](docs/llm_interface_guide.md)

## 📦 Dependency Management

### Adding Dependencies

```bash
# Add runtime dependency
uv add <package-name>

# Add development dependency
uv add --dev <package-name>

# Examples:
uv add langchain-anthropic     # Add Anthropic support
uv add --dev pytest-asyncio    # Add async test support
```

### Updating Dependencies

```bash
# Update specific package
uv lock --upgrade-package langchain

# Update all packages
uv lock --upgrade

# Sync after updating
uv sync
```

### Removing Dependencies

```bash
uv remove <package-name>
```

## 🎨 Code Quality

### Project Guidelines

This project follows **SOLID principles** and enforces:
- **150-line maximum** per file (refactor if exceeded)
- **Protocol-based interfaces** for dependency injection
- **Type hints** for all function signatures
- **Docstrings** for all public APIs (Google style)
- **Composition over inheritance**

See [AGENTS.md](AGENTS.md) for complete coding guidelines.

### Formatting

```bash
# Auto-format all code
make format

# Check formatting without changes
uv run ruff format --check
```

### Linting

```bash
# Run linter
make lint

# Auto-fix issues
uv run ruff check --fix
```

### Pre-commit Checks

```bash
# Run before committing (unit tests + format + lint)
make pre-commit
```

## 🗄️ Database Schema

### Tables

**knowledge_base**: Stores documents and embeddings for RAG
```sql
- id: INT (primary key)
- doc_id: VARCHAR(255) (unique)
- content: TEXT
- embedding: JSON
- metadata: JSON
- created_at: TIMESTAMP
```

**chat_history**: Stores conversation history
```sql
- id: INT (primary key)
- session_id: VARCHAR(255)
- role: ENUM('user', 'assistant', 'system')
- content: TEXT
- metadata: JSON
- created_at: TIMESTAMP
```

**mpc_instances**: Tracks MPC server instances
```sql
- id: INT (primary key)
- instance_id: VARCHAR(255) (unique)
- status: ENUM('running', 'stopped', 'error')
- host: VARCHAR(255)
- port: INT
- metadata: JSON
- created_at: TIMESTAMP
```

## 📚 Learning Paths

### 1. LLM Integration with LangChain
- Implement [llm_interface.py](src/agentlab/core/llm_interface.py)
- Add support for multiple providers (OpenAI, Anthropic, etc.)
- Experiment with different prompting strategies

### 2. RAG System Development
- Implement [rag_service.py](src/agentlab/core/rag_service.py)
- Add document embedding generation
- Build similarity search functionality

### 3. MCP Protocol
- Implement [mpc_client_base.py](src/agentlab/agents/mpc_client_base.py)
- Implement [mpc_server_base.py](src/agentlab/agents/mpc_server_base.py)
- Follow Anthropic's MCP specification

### 4. API Development
- Complete FastAPI routes in [chat_routes.py](src/agentlab/api/routes/chat_routes.py)
- Add authentication and rate limiting
- Build comprehensive test suite

### 5. Frontend Integration
- Choose React or Vue.js
- Implement chat interface
- Build MPC instance manager UI

## � Project Structure Details

### Core Modules

**[models.py](src/agentlab/models.py)**: Protocol definitions and data models
- `LLMInterface`: Abstract interface for LLM implementations
- `RAGService`: Protocol for RAG operations
- `MPCClient/MPCServer`: MCP protocol interfaces
- Data models: `ChatMessage`, `RAGResult`, `MPCInstanceInfo`

**[database/](src/agentlab/database/)**: Database layer
- [config.py](src/agentlab/database/config.py): MySQL connection configuration
- [models.py](src/agentlab/database/models.py): Table schemas and SQL definitions
- [crud.py](src/agentlab/database/crud.py): CRUD operations

**[core/](src/agentlab/core/)**: Business logic
- [rag_service.py](src/agentlab/core/rag_service.py): RAG implementation
- [mpc_manager.py](src/agentlab/core/mpc_manager.py): MPC instance manager
- [llm_interface.py](src/agentlab/core/llm_interface.py): LangChain LLM wrapper

**[agents/](src/agentlab/agents/)**: Low-level implementations
- [rag_processor.py](src/agentlab/agents/rag_processor.py): Embedding generation, chunking
- [mpc_client_base.py](src/agentlab/agents/mpc_client_base.py): MPC client base class
- [mpc_server_base.py](src/agentlab/agents/mpc_server_base.py): MPC server base class

**[api/](src/agentlab/api/)**: FastAPI application
- [main.py](src/agentlab/api/main.py): FastAPI app entry point
- [routes/chat_routes.py](src/agentlab/api/routes/chat_routes.py): Chat & RAG endpoints
- [routes/mpc_routes.py](src/agentlab/api/routes/mpc_routes.py): MPC management endpoints

## 🚧 Development Status

### ✅ Completed
- Project structure and organization
- Protocol definitions and interfaces
- Database schema design
- FastAPI skeleton with routes
- Development tooling (Makefile, testing setup)

### 🔨 To Be Implemented
- LangChain LLM integration
- RAG service with embeddings
- MCP client/server implementations
- Database CRUD operations
- Frontend application
- Docker composition

## 🤝 Contributing

This is a learning project. To contribute:

1. Follow the coding guidelines in [AGENTS.md](AGENTS.md)
2. Maintain **150-line limit** per file
3. Use **Protocol-based interfaces** for new features
4. Add **unit tests** for all new code
5. Run `make pre-commit` before committing
6. Add **docstrings** with Args, Returns, and Raises sections

## 📖 Resources

### Documentation
- [LangChain Documentation](https://python.langchain.com/)
- [Anthropic MCP Specification](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [uv Documentation](https://docs.astral.sh/uv/)

### Learning Materials
- [AGENTS.md](AGENTS.md) - Comprehensive coding guidelines
- [Frontend README](frontend/README.md) - Frontend structure
- [Data README](data/README.md) - Data directory usage

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check MySQL is running
mysql -u root -p

# Verify credentials in .env
cat .env | grep DB_
```

### Import Errors
```bash
# Ensure dependencies are synced
uv sync

# Verify package is installed
uv pip list | grep agentlab
```

### Port Already in Use
```bash
# Change API port in .env
API_PORT=8001

# Or specify when running
uv run uvicorn agentlab.api.main:app --port 8001
```

## 👥 Authors

- Built for IA Bootcamp 2025
- Based on Python template by Alejandro Fernández Camello

## 📝 License

This project is for educational purposes.

## 🙏 Acknowledgments

- [uv](https://docs.astral.sh/uv/) - Fast Python package management
- [LangChain](https://python.langchain.com/) - LLM framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Ruff](https://github.com/astral-sh/ruff) - Python linter and formatter
- [Anthropic](https://www.anthropic.com/) - MCP specification
