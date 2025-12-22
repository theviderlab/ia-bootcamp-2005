# Frontend for Agent Lab

⚠️ **IMPORTANT**: This is a specification document. Implementation has not yet started. This README defines requirements, architecture, and integration patterns for development.

## Project Status

- **Backend API**: ✅ Fully implemented and documented in `docs/API.md`
- **Frontend Implementation**: ❌ Not started (only placeholder files exist)
- **Configuration Files**: ❌ Need to be created (see Setup section below)

This directory contains the design specifications and documentation for the Agent Lab frontend application. The goal is to build a clean, minimalist interface for interacting with the AI Agent ecosystem, managing memory, and utilizing RAG capabilities.

## Technical Requirements

- **Authentication**: Single-user system (for testing/development purposes only)
- **Mobile Support**: Yes - responsive design required for mobile/tablet
- **File Upload**: Accepts text content or file paths (see RAG Section for details)
- **Browser Requirements**: Modern browsers with ES6+ support
- **Backend Dependency**: Requires backend server running at `http://localhost:8000`

## Technology Stack (Recommended)

- **Framework**: React or Vue.js
- **Build Tool**: Vite
- **Styling**: Tailwind CSS (for minimalist design)
- **State Management**: Zustand, Redux Toolkit, or Context API
- **HTTP Client**: Axios or Fetch API
- **UI Components**: Headless UI or Radix UI (for accessible tabs, toggles)
- **Code Highlighting**: Prism.js or Highlight.js (for Context Window tab)
- **Drag & Drop**: react-dropzone or vue-dropzone

## Recommended Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Header.jsx          # Top bar with tabs and action buttons
│   │   │   ├── ActionButtons.jsx   # Reset Session & Delete All buttons
│   │   │   ├── Sidebar.jsx         # Right sidebar container
│   │   │   └── Layout.jsx          # Main layout wrapper
│   │   ├── Tabs/
│   │   │   ├── ChatTab.jsx         # Main chat interface
│   │   │   ├── ShortTermMemoryTab.jsx
│   │   │   ├── LongTermMemoryTab.jsx
│   │   │   ├── RAGResultsTab.jsx
│   │   │   └── ContextWindowTab.jsx
│   │   ├── Chat/
│   │   │   ├── MessageList.jsx     # Scrollable message area
│   │   │   ├── Message.jsx         # Single message component
│   │   │   └── InputBox.jsx        # Message input field
│   │   ├── Sidebar/
│   │   │   ├── MemorySection.jsx   # Memory toggles
│   │   │   ├── RAGSection.jsx      # File upload & selection
│   │   │   └── MPCSection.jsx      # Future: MCP management
│   │   ├── Memory/
│   │   │   ├── SemanticView.jsx    # Semantic memory cards
│   │   │   ├── EpisodicView.jsx    # Episodic timeline
│   │   │   ├── ProfileView.jsx     # User profile table
│   │   │   └── ProceduralView.jsx  # Learned patterns
│   │   └── RAG/
│   │       ├── ChunkCard.jsx       # Single chunk display
│   │       ├── ScoreBar.jsx        # Visual score indicator
│   │       └── FileUploader.jsx    # Drag & drop component
│   ├── services/
│   │   ├── api.js                  # Base API client
│   │   ├── chatService.js          # Chat endpoints
│   │   ├── memoryService.js        # Memory endpoints
│   │   ├── ragService.js           # RAG endpoints
│   │   ├── configService.js        # Configuration endpoints
│   │   └── sessionService.js       # Session management (reset, delete all)
│   ├── hooks/
│   │   ├── useChat.js              # Chat state & actions
│   │   ├── useMemory.js            # Memory state & actions
│   │   ├── useRAG.js               # RAG state & actions
│   │   └── useSession.js           # Session management
│   ├── store/
│   │   ├── chatSlice.js            # Chat state (if using Redux)
│   │   ├── memorySlice.js          # Memory state
│   │   └── configSlice.js          # Configuration state
│   ├── utils/
│   │   ├── tokenCounter.js         # Estimate token counts
│   │   ├── formatters.js           # Date/time formatters
│   │   └── validators.js           # Input validation
│   ├── constants/
│   │   ├── api.js                  # API endpoints & config
│   │   └── memoryTypes.js          # Memory type definitions
│   ├── App.jsx                     # Main app component
│   └── main.jsx                    # Entry point
├── public/                         # Static assets
├── package.json                    # Dependencies
└── vite.config.js                  # Vite configuration
```

## UI/UX Design Overview

The application features a modern, split-screen layout designed for focus and ease of configuration.

### Responsive Design Strategy

**Desktop (≥1024px)**:
- Split-screen layout: Chat on left (60%), Sidebar on right (40%)
- Tabs in horizontal row at top
- Full sidebar visible with all sections expanded

**Tablet (768px - 1023px)**:
- Stack layout: Chat above, Sidebar below
- Or: Sidebar as collapsible drawer (hamburger menu)
- Tabs remain horizontal but may scroll

**Mobile (≤767px)**:
- Full-width single column layout
- Sidebar becomes bottom sheet or slide-out drawer
- Tabs become dropdown or bottom navigation
- Action buttons in floating action button (FAB) or menu
- Touch-optimized: larger tap targets, swipe gestures
- Virtual keyboard considerations for input field

**Breakpoint Summary**:
```css
/* Mobile first approach */
@media (min-width: 768px) { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
```

### Tab System Architecture

The interface uses a dynamic tab system where tabs appear/disappear based on enabled features and user actions:

- **Persistent Tabs**: Chat, Context Window (always visible).
- **Conditional Tabs**: Short-term Memory, Long-term Memory, RAG Results (visible when feature is enabled).
- **Tab State**: Active tab state persists per session.

### 1. Header (Top Bar)
- **Tabs/Navigation**: Located at the top. Tabs appear dynamically based on enabled features.
- **Available Tabs**:
  - **Chat** (Always visible): Main conversation interface.
  - **Short-term Memory** (Conditional): Displays when short-term memory is enabled. Shows recent conversation buffer.
  - **Long-term Memory** (Conditional): Displays when semantic/episodic/profile/procedural memory is enabled. Shows stored memories with timestamps and metadata.
  - **RAG Results** (Conditional): Displays when RAG is enabled and a query has been made. Shows retrieved chunks with similarity scores and source metadata.
  - **Context Window** (Always visible): Shows the complete context being sent to the LLM, including system prompt, memory, RAG chunks, and conversation history.
- **Action Buttons** (Top Right Corner):
  - **Reset Session** (🔄 icon): Creates a new session and clears short-term memory buffer. Long-term memory and RAG documents are preserved.
    - Shows confirmation dialog before executing.
    - Generates new session ID.
    - Clears chat interface.
    - **⚠️ Note**: Clears conversation history from ALL sessions (not just current). This is by design as the system works with one active session at a time.
  - **Delete All** (💀 skull icon): Nuclear option - deletes ALL data and restores system to initial state.
    - Shows strong warning dialog with confirmation input (must type "DELETE" exactly - case-sensitive).
    - Deletes:
      - All short-term memory (conversation buffers)
      - All long-term memory (semantic, episodic, profile, procedural)
      - All RAG documents and vectors (Pinecone)
      - All session data (MySQL database)
    - Restores system to factory settings.
    - **Important**: This is irreversible - no backups are created.
- **Style**: Minimalist, low profile. Active tab highlighted. Action buttons are icon-only with tooltips.

### 2. Main Layout (Left Panel - Chat)
- **Role**: Primary interaction area.
- **Components**:
  - **Message List**: Scrollable area displaying user prompts and LLM responses.
  - **Input Area**: Clean text input field at the bottom for sending messages.
- **Behavior**: Real-time updates of the conversation.

### 3. Sidebar (Right Panel - Configuration)
The sidebar is the control center, divided into three distinct sections:

#### A. Memory Section
Controls to manage the agent's memory capabilities.
- **Functionality**: Enable or disable specific memory types.
- **UI Elements**: Toggles/Checkboxes for:
  - Semantic Memory
  - Episodic Memory
  - Profile Memory
  - Procedural Memory

#### B. RAG Section (Retrieval-Augmented Generation)
Interface for managing the knowledge base and context.
- **Drag and Drop**: Area to upload files (text, markdown, logs) directly to the RAG system.
  - **File Upload Mechanism**: Backend accepts either:
    - Text content directly (string)
    - File paths (string, e.g., `"./docs/manual.md"`)
  - **Frontend Strategy**: 
    - Read file content in browser using FileReader API
    - Send content as text string in request body
    - No multipart/form-data upload needed
  - **Example payload**:
    ```json
    {
      "documents": [
        "This is direct text content",
        "./docs/manual.md",
        "More text content..."
      ],
      "namespace": "my-docs"
    }
    ```
- **Document List**: Displays uploaded documents/namespaces with counts.
- **Namespace Selection**: Toggles to enable/disable specific namespaces for chat context.
- **Document Filtering**: View documents by namespace using `/llm/rag/documents` endpoint.

#### C. MCP Section (Model Context Protocol)
Interface para gestionar las herramientas (tools) disponibles del sistema.
- **Lista de Herramientas**: Muestra todas las herramientas MCP registradas en el sistema.
- **Toggles On/Off**: Cada herramienta tiene un checkbox/toggle para activarla o desactivarla.
- **Estado Visual**: Indica qué herramientas están actualmente activas.
- **Comportamiento**: 
  - Cuando al menos una herramienta está activada, el chat enviará `use_tools=true` y `available_tools=[...]`.
  - Cuando ninguna herramienta está activada, el chat funciona sin herramientas (`use_tools=false`).
  - Las herramientas seleccionadas determinan exactamente qué capacidades tiene el agente en la conversación.
- **Información de Herramientas**: Al hacer hover sobre una herramienta, muestra un tooltip con:
  - Nombre de la herramienta
  - Descripción breve de su funcionalidad
  - Esquema de parámetros (opcional, para usuarios avanzados)

## Component Details by Tab

### Chat Tab
**Purpose**: Primary interface for conversation with the LLM.

**Components**:
- **Message List** (Main Area):
  - User messages (aligned right, styled differently).
  - Assistant messages (aligned left).
  - Timestamps (relative: "2 minutes ago").
  - Loading indicator while waiting for response.
- **Input Box** (Bottom):
  - Multi-line text area with auto-expand.
  - Send button (icon or "Send" text).
  - Character/token counter.
- **Actions**:
  - Clear conversation (with confirmation).
  - Export conversation (JSON/Markdown).

### Short-term Memory Tab
**Purpose**: Display recent conversation buffer stored in memory.

**Components**:
- **Timeline View**:
  - Chronological list of recent messages (last 10-20).
  - Each entry shows: timestamp, role (user/assistant), content preview.
  - Click to expand full message.
- **Metadata Panel**:
  - Session start time.
  - Message count.
  - Buffer size in tokens.

### Long-term Memory Tab
**Purpose**: Visualize persistent memory across sessions.

**Components**:
- **Memory Type Selector** (Top):
  - Tabs or buttons: Semantic | Episodic | Profile | Procedural.
- **Semantic Memory View**:
  - Card grid of stored facts.
  - Each card: fact text, source (conversation reference), timestamp.
  - Search/filter functionality.
- **Episodic Memory View**:
  - Timeline of conversation summaries.
  - Grouped by date.
  - Click to expand full summary.
- **Profile Memory View**:
  - Key-value table of user preferences and information.
  - Editable fields (future enhancement).
- **Procedural Memory View**:
  - List of learned patterns and workflows.
  - Pattern name, frequency count, last used timestamp.

### RAG Results Tab
**Purpose**: Show retrieved document chunks and their relevance scores.

**Components**:
- **Query Info Header**:
  - Original query text.
  - Timestamp of query.
  - Number of chunks retrieved.
- **Chunk List** (Main Area):
  - Each chunk displayed as a card with:
    - **Score Bar**: Visual indicator (0.0 to 1.0) with color gradient (red → yellow → green).
    - **Content**: Text preview (first 200 chars) with "Read more" expansion.
    - **Metadata**: Source file, namespace, page/section number.
    - **Actions**: Copy text, view full document context.
  - Sorted by score (highest first).
- **Namespace Filter**:
  - Filter chunks by namespace.

### Context Window Tab
**Purpose**: Display complete context sent to LLM for transparency and debugging.

**Components**:
- **Token Usage Indicator** (Top):
  - Progress bar: Used tokens / Max tokens.
  - Color-coded: Green (<70%), Yellow (70-90%), Red (>90%).
  - Breakdown by component.
- **Context Components** (Collapsible Sections):
  - **System Prompt**: 
    - Code block with syntax highlighting.
    - Token count.
  - **Memory Context**:
    - Combined memory text.
    - Token count.
    - Breakdown by memory type (if available).
  - **RAG Context**:
    - Retrieved chunks text.
    - Token count.
    - Number of chunks included.
  - **Conversation History**:
    - JSON or formatted view of messages array.
    - Token count.
- **Actions**:
  - Copy full context.
  - Download as JSON.
  - "Optimize Context" button (future: suggests reducing context size).

## API Integration

The frontend interacts with the backend API (default: `http://localhost:8000`). Below is the mapping of UI components to API endpoints defined in `docs/API.md`.

**⚠️ CRITICAL ARCHITECTURE PATTERN:**

The backend manages ALL conversation history and context via `session_id`. The frontend should:
- ✅ **Send only the current user message** in the `messages` array to `/llm/chat`
- ✅ **Store full conversation locally** for UI display (in state/store)
- ✅ **Let the backend reconstruct context** from its memory system

**Do NOT send the full conversation history** to the backend. This causes context leakage when memory is disabled.

### Chat Tab (Main Interface)
- **Send Message**: `POST /llm/chat`
  - **Payload**:
    - `messages`: **Array with single current user message** (NOT full history).
    - `session_id`: Current session identifier (backend uses this to retrieve context).
    - `memory_types`: Array of enabled types from the Memory Sidebar.
    - `rag_namespaces`: Array of enabled namespaces from the RAG Sidebar.
  - **Response**: Includes `response`, `session_id`, `context_text`, `context_tokens`, and `rag_sources`.
    ```json
    {
      "response": "FastAPI is a modern web framework...",
      "session_id": "uuid-123",
      "context_text": "## Recent Conversation\n...\n\n## Relevant Knowledge Base Documents\n...",
      "context_tokens": 245,
      "rag_sources": [
        {
          "content": "FastAPI documentation...",
          "score": 0.92,
          "doc_id": "fastapi_intro",
          "namespace": "docs",
          "chunk_index": 0
        }
      ]
    }
    ```
- **Load History**: `GET /llm/memory/history`
  - **Params**: `session_id`.

### Short-term Memory Tab
- **Get Buffer**: `GET /llm/memory/history`
  - **Params**: `session_id`, `limit` (e.g., last 10 messages).
  - **Display**: List of recent messages with timestamps, roles (user/assistant), and content.

### Long-term Memory Tab
- **Get Memory Context**: `POST /llm/memory/context`
  - **Payload**: `session_id`, `memory_types` (array of enabled types).
  - **Response**: Returns structured memory data:
    - `semantic_facts`: Array of stored facts with metadata.
    - `episodic_summary`: Conversation summaries with timestamps.
    - `user_profile`: Key-value pairs of user preferences/info.
    - `procedural_patterns`: Learned patterns and workflows.
  - **Display**: Organized sections for each memory type with expandable cards.

### RAG Results Tab
- **Get RAG Sources**: Data included in `/llm/chat` response
  - **Source**: Extract `rag_sources` field from the last chat response.
  - **Data Structure**:
    ```json
    {
      "rag_sources": [
        {
          "content": "Retrieved text content...",
          "score": 0.92,
          "doc_id": "fastapi_intro",
          "namespace": "docs",
          "chunk_index": 0
        }
      ]
    }
    ```
  - **Display**: 
    - List of chunks sorted by score (descending).
    - Each chunk shows: similarity score (as progress bar), content preview, source doc_id, namespace, and chunk_index.
    - Query text can be extracted from last user message.

### Context Window Tab
- **Get Full Context**: Data included in `/llm/chat` response
  - **Source**: Extract `context_text` and `context_tokens` fields from the last chat response.
  - **Data Structure**:
    ```json
    {
      "context_text": "## Recent Conversation\n[User]: Hello\n[Assistant]: Hi!\n\n## Relevant Knowledge Base Documents\n### Document 1\nFastAPI is...",
      "context_tokens": 245
    }
    ```
  - **Display**:
    - Token usage indicator (progress bar: `context_tokens` / `max_context_tokens`).
    - Render `context_text` with markdown formatting.
    - Collapsible sections based on markdown headers (##).
    - Syntax highlighting for code blocks if present.
    - Copy and download actions.

**Note**: Both RAG Results and Context Window tabs now use data from the `/llm/chat` response. No additional API calls needed. The frontend should store the last chat response to populate these tabs.

### Memory Sidebar
- **Get Configuration**: `GET /config/session/{session_id}`
  - Retrieves current memory settings to populate initial toggle states.
- **Update Configuration**: `PUT /config/memory`
  - **Payload**: `enabled` (bool), `types` (array of strings).
  - Called when toggles are changed.

### RAG Sidebar
- **Upload Files**: `POST /llm/rag/documents`
  - **Payload**: `documents` (file paths or content), `namespace`.
  - Triggered by the Drag and Drop action.
- **Configure RAG**: `PUT /config/rag`
  - **Payload**: `enabled` (bool), `namespaces` (array).
  - Called when selecting/deselecting documents (mapped to namespaces).

### MCP Sidebar
- **Get Available Tools**: `GET /mpc/tools` o `GET /mpc/tools/names`
  - **Response**: Lista de herramientas disponibles con sus metadatos.
  - **Llamar**: Al cargar el componente del sidebar.
  - **Display**: 
    - Crear un toggle/checkbox por cada herramienta.
    - Mostrar nombre y descripción breve.
    - Añadir tooltip con información detallada.
- **Get Tool Details**: `GET /mpc/tools/{tool_name}`
  - **Response**: Información detallada de una herramienta específica.
  - **Uso**: Para tooltips o modales informativos.
- **Integration with Chat**: 
  - Al enviar mensaje en Chat, incluir:
    - `use_tools`: `true` si hay herramientas seleccionadas, `false` si no.
    - `available_tools`: Array con nombres de herramientas activas (ej: `["calculator", "get_current_datetime"]`).
    - `tool_choice`: `"auto"` (dejar que el LLM decida cuándo usar las herramientas).
  - **Estado Local**: Mantener array de `selectedTools` en estado del componente.
  - **Sincronización**: Los toggles actualizan `selectedTools`, y este se pasa al endpoint `/llm/chat`.
- **Tool Results Display**:
  - En respuesta del chat, mostrar visualmente cuando se usaron herramientas:
    - `tools_used` (bool): Indica si se usaron herramientas.
    - `tool_calls` (array): Lista de llamadas realizadas.
    - `tool_results` (array): Resultados de las ejecuciones.
  - Considerar añadir badge o indicador en mensajes del asistente cuando incluyen uso de herramientas.

### Header Action Buttons
- **Reset Session**: **(NEW ENDPOINT NEEDED)** `POST /session/reset`
  - **Payload**: `current_session_id` (string).
  - **Response**:
    ```json
    {
      "success": true,
      "new_session_id": "uuid-new-session",
      "message": "Session reset successfully. Short-term memory cleared."
    }
    ```
  - **Backend Actions**:
    - Generate new session ID.
    - Clear short-term memory (conversation buffer) for current session.
    - Preserve long-term memory and RAG data.
    - Return new session ID to frontend.

- **Delete All**: `POST /session/reset-all`
  - **Payload**: `confirmation` (string, must be "DELETE" - case-sensitive).
  - **Response**:
    ```json
    {
      "success": true,
      "message": "All data deleted. System restored to initial state.",
      "deleted": {
        "sessions": 15,
        "memory_entries": 234,
        "rag_documents": 45,
        "vector_count": 1230
      }
    }
    ```
  - **Backend Actions**:
    - Delete all conversation history from MySQL.
    - Delete all memory entries (semantic, episodic, profile, procedural).
    - Delete all RAG vectors from Pinecone (all namespaces).
    - Delete all session configurations.
    - Truncate/reset all database tables.
    - Reinitialize default system configuration.

## API Suggestions & Requirements

To fully support the described frontend features, the following API enhancements are suggested:

### 3. Document-Level Toggling ✅ IMPLEMENTADO (Estrategia Playground)

**Solución para Playground (<10 documentos):** Usar **1 namespace por documento** es la estrategia óptima.

**Implementación Actual:**
- ✅ Backend ya soporta namespace por documento en `POST /llm/rag/documents`
- ✅ Chat endpoint ya filtra por múltiples namespaces en `POST /llm/chat`
- ✅ Frontend puede mapear 1 toggle = 1 documento = 1 namespace

**Ejemplo de Flujo:**

```javascript
// Frontend: Upload con namespace = filename
const uploadDocument = async (file) => {
  const namespace = file.name.replace(/\.[^/.]+$/, ""); // Remove extension
  
  await fetch('/llm/rag/documents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      documents: [file.path],
      namespace: `doc-${namespace}`  // Namespace único por documento
    })
  });
};

// Frontend: Toggles por documento en RAG Sidebar
const RAGSection = () => {
  const [selectedNamespaces, setSelectedNamespaces] = useState([]);
  
  return (
    <div>
      {documents.map(doc => (
        <label key={doc.namespace}>
          <input
            type="checkbox"
            checked={selectedNamespaces.includes(doc.namespace)}
            onChange={(e) => toggleNamespace(doc.namespace, e.target.checked)}
          />
          {doc.filename}
        </label>
      ))}
    </div>
  );
};

// Frontend: Chat con namespaces seleccionados
const sendMessage = async (message) => {
  await fetch('/llm/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: [{role: 'user', content: message}],
      use_rag: true,
      rag_namespaces: selectedNamespaces  // Array de namespaces seleccionados
    })
  });
};
```

**Ventajas para Playground:**
- ✅ Implementación simple (no requiere document IDs adicionales)
- ✅ UI intuitiva (1 checkbox = 1 documento)
- ✅ Backend ya soporta múltiples namespaces
- ✅ Perfecto para 3-10 documentos
- ✅ Cada documento puede habilitarse/deshabilitarse independientemente

**Nota:** Para producción con cientos de documentos, considerar agrupar por categorías (docs, api-reference, tutorials) o usar filtrado por document ID.

### 8. MCP Endpoints ✅

Los endpoints MCP permiten listar y gestionar las herramientas disponibles en el sistema.

#### 8.1 Listar Todas las Herramientas

**Endpoint disponible:** `GET /mpc/tools`

Retorna todas las herramientas MCP registradas en el sistema con sus metadatos.

**Respuesta esperada:**
```json
{
  "tools": [
    {
      "name": "get_current_datetime",
      "description": "Get the current date and time",
      "schema": {
        "type": "object",
        "properties": {},
        "required": []
      }
    },
    {
      "name": "calculator",
      "description": "Perform mathematical calculations",
      "schema": {
        "type": "object",
        "properties": {
          "expression": {
            "type": "string",
            "description": "Mathematical expression to evaluate"
          }
        },
        "required": ["expression"]
      }
    }
  ]
}
```

**Uso en UI:**
- Llamar al cargar el componente MCP del sidebar
- Mostrar cada herramienta con un toggle
- Guardar el estado de herramientas seleccionadas en el estado del frontend

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/mpc/tools"
```

#### 8.2 Obtener Nombres de Herramientas (Simplificado)

**Endpoint disponible:** `GET /mpc/tools/names`

Retorna solo los nombres de las herramientas para una carga más rápida.

**Respuesta esperada:**
```json
{
  "tool_names": [
    "get_current_datetime",
    "calculator",
    "web_search"
  ]
}
```

**Uso en UI:**
- Alternativa ligera para inicializar el sidebar MCP
- Útil si solo necesitas los nombres sin metadata completa

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/mpc/tools/names"
```

#### 8.3 Obtener Información de Herramienta Específica

**Endpoint disponible:** `GET /mpc/tools/{tool_name}`

Retorna información detallada de una herramienta específica.

**URL de ejemplo:**
```
GET /mpc/tools/calculator
```

**Respuesta esperada:**
```json
{
  "name": "calculator",
  "description": "Perform mathematical calculations",
  "schema": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string",
        "description": "Mathematical expression to evaluate"
      }
    },
    "required": ["expression"]
  },
  "examples": [
    {
      "expression": "2 + 2",
      "result": "4"
    }
  ]
}
```

**Uso en UI:**
- Mostrar información detallada al hacer hover o click en info icon
- Tooltip con descripción y parámetros

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/mpc/tools/calculator"
```

#### 8.4 Integración con Chat

**Endpoint de chat:** `POST /llm/chat`

Cuando hay herramientas activadas en el sidebar, el frontend debe incluir estos parámetros:

```json
{
  "messages": [...],
  "use_tools": true,
  "available_tools": ["get_current_datetime", "calculator"],
  "tool_choice": "auto"
}
```

**Parámetros:**
- `use_tools` (bool): `true` si hay al menos una herramienta activada, `false` si todas están desactivadas
- `available_tools` (array[string]): Array con los nombres de las herramientas activadas en el sidebar
- `tool_choice` (string, opcional): "auto" permite al LLM decidir cuándo usar las herramientas

**Lógica del Frontend:**
```javascript
// En el componente MCP Sidebar
const [selectedTools, setSelectedTools] = useState([]);

// Al enviar mensaje en Chat
const sendMessage = async (message) => {
  const payload = {
    messages: [...messages, { role: 'user', content: message }],
    use_tools: selectedTools.length > 0,
    available_tools: selectedTools,
    tool_choice: 'auto'
  };
  
  const response = await chatService.sendMessage(payload);
  // ...
};
```

**Nota:** Los endpoints `/mpc/tools`, `/mpc/tools/names`, y `/mpc/tools/{tool_name}` ya están disponibles según la documentación de la API. No se requieren nuevos endpoints para esta funcionalidad.

## User Flows

### Flow 1: Starting a New Conversation
1. User lands on Chat tab (default).
2. Right sidebar loads with default configuration (Memory: enabled, RAG: disabled).
3. User types a message and sends.
4. Frontend calls `POST /llm/chat` with current config.
5. Response appears in Chat tab.
6. Context Window tab updates automatically with token usage.

### Flow 2: Enabling RAG for Context
1. User clicks RAG section in sidebar.
2. Drags and drops files into the upload area.
3. Frontend calls `POST /llm/rag/documents` for each file.
4. Document list updates showing uploaded files grouped by namespace.
5. User toggles on specific namespaces.
6. Frontend calls `PUT /config/rag` with enabled namespaces.
7. Next message sent includes RAG context.
8. **RAG Results tab appears** after first query with RAG enabled.
9. User clicks RAG Results tab to see retrieved chunks and scores.

### Flow 3: Viewing Memory State
1. User enables semantic memory in sidebar.
2. Frontend calls `PUT /config/memory`.
3. User has conversation (several messages exchanged).
4. **Short-term Memory tab appears** (since memory is enabled).
5. User clicks Short-term Memory tab to see recent buffer.
6. After multiple sessions, **Long-term Memory tab appears**.
7. User clicks Long-term Memory tab, selects "Semantic" subtab.
8. Views stored facts extracted from conversations.

### Flow 4: Debugging Context Overflow
1. User sends a message and gets truncated response.
2. User clicks **Context Window tab**.
3. Sees token usage at 95% (red indicator).
4. Expands each section to see breakdown:
   - System Prompt: 300 tokens
   - Memory: 1200 tokens
   - RAG: 1800 tokens
   - History: 700 tokens
5. User decides to disable some memory types or reduce RAG chunks.
6. Adjusts settings in sidebar.
7. Sends message again with reduced context.

### Flow 4bis: Using MCP Tools
1. User wants to enable calculator functionality for mathematical queries.
2. User opens **MCP Section** in right sidebar.
3. Sees list of available tools (loaded from `GET /mpc/tools`):
   - ☐ get_current_datetime
   - ☐ calculator
   - ☐ web_search
4. User clicks on **calculator** checkbox to enable it.
5. Checkbox state changes to checked ☑.
6. Frontend updates `selectedTools` array: `["calculator"]`.
7. User types message: "What is 234 * 567?"
8. Frontend calls `POST /llm/chat` with:
   ```json
   {
     "messages": [...],
     "use_tools": true,
     "available_tools": ["calculator"],
     "tool_choice": "auto"
   }
   ```
9. Backend processes with agent that can call calculator tool.
10. Response includes:
    - `tools_used`: true
    - `tool_calls`: [{"tool_name": "calculator", "input": {"expression": "234 * 567"}, ...}]
    - `tool_results`: [{"tool_name": "calculator", "output": "132678", ...}]
    - `response`: "The result of 234 × 567 is 132,678."
11. Chat message displays normally, optionally with badge "🔧 Tool Used: calculator".
12. User can hover over badge to see tool execution details.
13. To disable tools, user unchecks calculator box.
14. Next messages will be sent with `use_tools: false`.

### Flow 5: Resetting Current Session
1. User has been chatting and wants to start fresh topic.
2. User clicks **Reset Session** button (🔄 icon) in top right.
3. Confirmation dialog appears: "Reset session? This will clear current conversation but preserve long-term memory."
4. User clicks "Confirm".
5. Frontend calls `POST /session/reset` with current session ID.
6. Backend generates new session ID and clears short-term buffer.
7. Frontend receives new session ID.
8. Chat interface clears.
9. User starts new conversation with clean slate.
10. Long-term memory (facts learned from previous sessions) remains available.

### Flow 6: Nuclear Reset (Delete All)
1. User wants to completely reset system (e.g., switching projects, testing, cleanup).
2. User clicks **Delete All** button (💀 skull icon) in top right.
3. Strong warning dialog appears:
   - "⚠️ WARNING: This will permanently delete ALL data:"
   - "• All conversations (all sessions)"
   - "• All long-term memory"
   - "• All uploaded RAG documents"
   - "• All vector embeddings"
   - "• All database records"
   - "Type 'DELETE' to confirm this action."
4. User types "DELETE" in confirmation input.
5. User clicks "Confirm Deletion".
6. Frontend calls `DELETE /system/reset-all` with confirmation.
7. Backend performs nuclear reset:
   - Clears Pinecone index.
   - Truncates MySQL tables.
   - Resets system configuration.
8. Frontend receives success response with deletion counts.
9. Application resets to initial state (like first launch).
10. User can now start completely fresh.

## Implementation Recommendations

### State Management
**Option 1: Zustand (Recommended for simplicity)**
```javascript
// store/chatStore.js
import { create } from 'zustand';

export const useChatStore = create((set) => ({
  messages: [],
  sessionId: null,
  activeTab: 'chat',
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  setActiveTab: (tab) => set({ activeTab: tab }),
}));
```

**Option 2: Redux Toolkit (For complex state)**
```javascript
// store/chatSlice.js
import { createSlice } from '@reduxjs/toolkit';

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    sessionId: null,
    loading: false,
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
  },
});
```

### API Service Examples

**Chat Service:**
```javascript
// services/chatService.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const chatService = {
  /**
   * Send a chat message to the backend.
   * 
   * IMPORTANT ARCHITECTURE NOTE:
   * - messages array should contain ONLY the current user message
   * - Backend manages conversation history via session_id
   * - Do NOT send full conversation history in messages array
   * 
   * @param {Array} messages - Single-element array with current user message
   * @param {Object} config - Configuration for memory, RAG, tools
   */
  sendMessage: async (messages, config) => {
    // Validate that messages contains only one message (current user input)
    if (messages.length !== 1) {
      console.warn('⚠️ Messages array should contain only the current message');
    }
    
    const response = await axios.post(`${API_BASE_URL}/llm/chat`, {
      messages,  // Single message only - backend handles history
      session_id: config.sessionId,
      use_memory: config.memory.enabled,
      memory_types: config.memory.types,
      use_rag: config.rag.enabled,
      rag_namespaces: config.rag.namespaces,
    });
    return response.data;
  },
  
  getHistory: async (sessionId, limit = 100) => {
    const response = await axios.get(`${API_BASE_URL}/llm/memory/history`, {
      params: { session_id: sessionId, limit },
    });
    return response.data;
  },
};
```

**Session Service:**
```javascript
// services/sessionService.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const sessionService = {
  resetSession: async (currentSessionId) => {
    const response = await axios.post(`${API_BASE_URL}/session/reset`, {
      current_session_id: currentSessionId,
    });
    return response.data;
  },
  
  deleteAll: async (confirmation) => {
    if (confirmation !== 'DELETE') {
      throw new Error('Invalid confirmation string');
    }
    
    const response = await axios.delete(`${API_BASE_URL}/system/reset-all`, {
      data: { confirmation },
    });
    return response.data;
  },
};
```

**MCP Service:**
```javascript
// services/mcpService.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const mcpService = {
  // Get all available tools
  getTools: async () => {
    const response = await axios.get(`${API_BASE_URL}/mpc/tools`);
    return response.data;
  },
  
  // Get tool names only (lightweight)
  getToolNames: async () => {
    const response = await axios.get(`${API_BASE_URL}/mpc/tools/names`);
    return response.data;
  },
  
  // Get detailed info for a specific tool
  getToolInfo: async (toolName) => {
    const response = await axios.get(`${API_BASE_URL}/mpc/tools/${toolName}`);
    return response.data;
  },
};
```

**Chat Hook Example:**
```javascript
// hooks/useChat.js
import { useState } from 'react';
import { chatService } from '../services/chatService';

export const useChat = (sessionId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (content, config) => {
    setLoading(true);
    try {
      // Add user message to local state (for UI display)
      const newMessage = { role: 'user', content };
      setMessages((prev) => [...prev, newMessage]);
      
      // ✅ CORRECT: Send only the new message to backend
      // Backend handles context via session_id
      const response = await chatService.sendMessage(
        [newMessage],  // Only current message - NOT full history
        config
      );
      
      // Add assistant response to local state (for UI display)
      const assistantMessage = { 
        role: 'assistant', 
        content: response.response 
      };
      setMessages((prev) => [...prev, assistantMessage]);
      
      return response;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return { messages, loading, sendMessage };
};
```

**MCP Hook:**
```javascript
// hooks/useMCP.js
import { useState, useEffect } from 'react';
import { mcpService } from '../services/mcpService';

export const useMCP = () => {
  const [tools, setTools] = useState([]);
  const [selectedTools, setSelectedTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load available tools on mount
  useEffect(() => {
    const loadTools = async () => {
      try {
        setLoading(true);
        const data = await mcpService.getTools();
        setTools(data.tools || []);
      } catch (err) {
        console.error('Failed to load MCP tools:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    loadTools();
  }, []);

  // Toggle tool selection
  const toggleTool = (toolName) => {
    setSelectedTools((prev) => {
      if (prev.includes(toolName)) {
        return prev.filter((name) => name !== toolName);
      } else {
        return [...prev, toolName];
      }
    });
  };

  // Check if a tool is selected
  const isToolSelected = (toolName) => {
    return selectedTools.includes(toolName);
  };

  // Get config for chat request
  const getToolsConfig = () => {
    return {
      use_tools: selectedTools.length > 0,
      available_tools: selectedTools,
      tool_choice: 'auto',
    };
  };

  return {
    tools,
    selectedTools,
    loading,
    error,
    toggleTool,
    isToolSelected,
    getToolsConfig,
  };
};
```

## Testing Strategy

### Unit Tests
- Component rendering tests (React Testing Library).
- State management logic tests.
- Utility function tests (token counter, formatters).

### Integration Tests
- API service tests (with mock server).
- User flow tests (Cypress or Playwright).
- Tab navigation and state persistence.

### E2E Tests
- Full conversation flow.
- File upload and RAG configuration.
- Memory toggle and persistence.
- Context window visualization.

## Development Phases

### Phase 1: Core Chat Interface (Week 1-2)
- [ ] Setup Vite + React/Vue project.
- [ ] Implement Layout components (Header, Sidebar, Main).
- [ ] Build Chat tab with message list and input.
- [ ] Connect to `POST /llm/chat` endpoint.
- [ ] Basic session management.

### Phase 2: Memory Integration (Week 3)
- [ ] Implement Memory sidebar section with toggles.
- [ ] Connect to `PUT /config/memory` endpoint.
- [ ] Build Short-term Memory tab.
- [ ] Build Long-term Memory tab with subtabs.
- [ ] Connect to `POST /llm/memory/context` endpoint.

### Phase 3: RAG Integration (Week 4)
- [ ] Implement RAG sidebar section.
- [ ] Build file uploader with drag & drop.
- [ ] Connect to `POST /llm/rag/documents` endpoint.
- [ ] Implement document list with toggles.
- [ ] Build RAG Results tab.

### Phase 4: Context Window & Polish (Week 5)
- [ ] Build Context Window tab.
- [ ] Display context from `/llm/chat` response (context_text and context_tokens fields).
- [ ] Implement token usage visualization.
- [ ] Add syntax highlighting for code blocks.
- [ ] Polish UI/UX with animations and feedback.
- [ ] Add error handling and loading states.
- [ ] Responsive design for mobile/tablet.

### Phase 5: Testing & Documentation (Week 6)
- [ ] Write unit tests for components.
- [ ] Write integration tests for API services.
- [ ] E2E tests for critical flows.
- [ ] User documentation.
- [ ] Deployment setup.

### Phase 6: MCP Tools & Session Management (Week 7)
- [ ] Implement MCP Section in sidebar with tool toggles.
- [ ] Connect to `GET /mpc/tools` endpoint.
- [ ] Display tool results in chat when tools are used.
- [ ] Implement Reset Session button with confirmation dialog.
- [ ] Connect to `POST /session/reset` endpoint.
- [ ] Implement Delete All button with strong warning.
- [ ] Connect to `POST /session/reset-all` endpoint.
- [ ] Add confirmation input (type "DELETE" to confirm - case sensitive).
- [ ] Test session reset preserves long-term data.
- [ ] Test delete all clears everything correctly.
- [ ] Add loading states and success/error feedback.

## Getting Started

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0 (or pnpm/yarn)
- Backend server running at `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file and configure
cp .env.example .env
# Edit .env with your API URL if different from default

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Development Commands

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Format code
npm run format
```

### Testing Backend Connection

Once the dev server is running, open browser console and test:

```javascript
// Test health endpoint
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
```

## Environment Configuration

The `.env.example` file is provided as a template. Copy it to `.env` and adjust values as needed:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Feature Flags
VITE_ENABLE_MCP=true
VITE_ENABLE_DEBUG_MODE=true

# Session Configuration
VITE_DEFAULT_SESSION_TIMEOUT=3600000  # 1 hour in ms
```

**Environment Variables:**
- `VITE_API_URL`: Backend API base URL (default: http://localhost:8000)
- `VITE_ENABLE_MCP`: Enable MCP tools section (default: true)
- `VITE_ENABLE_DEBUG_MODE`: Enable console logging for API calls (default: true)
- `VITE_DEFAULT_SESSION_TIMEOUT`: Session timeout in milliseconds

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions (macOS/iOS)

## Accessibility Considerations

- Keyboard navigation for all interactive elements.
- ARIA labels for screen readers.
- Color contrast ratios meeting WCAG AA standards.
- Focus indicators for tab navigation.
- Alt text for any icons or images.
