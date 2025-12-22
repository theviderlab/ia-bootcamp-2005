# Backend-as-Source-of-Truth Architecture - Implementation Complete

## Architectural Change

Cambio fundamental en la arquitectura del sistema para eliminar inconsistencias en la configuración de Memory, RAG y MCP Tools.

**Antes**: El frontend pasaba parámetros de configuración (`use_memory`, `use_rag`, `memory_types`, `rag_namespaces`, etc.) en cada request.

**Ahora**: El backend lee toda la configuración directamente desde la tabla `session_configs` en la base de datos. El frontend solo envía mensajes y parámetros de generación.

### Ventajas

✅ **Fuente única de verdad**: La base de datos es la autoridad para toda la configuración  
✅ **Sin inconsistencias**: No hay desincronización entre frontend y backend  
✅ **Código más simple**: Frontend no necesita gestionar estado complejo de configuración  
✅ **Más robusto**: Cambios de configuración aplican inmediatamente sin problemas de closures/state  
✅ **Mejor UX**: Los toggles en UI afectan directamente el siguiente mensaje sin necesidad de refresh

## Cambios Implementados

### Backend - [src/agentlab/api/routes/chat_routes.py](src/agentlab/api/routes/chat_routes.py)

#### 1. Simplificación de `ChatRequest` (líneas 139-166)

**Eliminados** todos los campos de configuración:
- ❌ `use_memory`, `use_rag`, `use_tools`
- ❌ `memory_types`, `rag_namespaces`, `rag_top_k`
- ❌ `tool_names`, `max_tool_iterations`

**Mantenidos** solo parámetros de generación:
- ✅ `messages`, `session_id`
- ✅ `temperature`, `max_tokens`
- ✅ `max_context_tokens`, `context_priority`

```python
class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.
    
    Configuration (memory, RAG, tools) is read from session_configs table in database.
    Only generation parameters are passed in the request.
    """
    messages: list[dict[str, str]] = Field(...)
    session_id: str | None = Field(None)
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(500, gt=0, le=4000)
    max_context_tokens: int = Field(4000, ge=100, le=8000)
    context_priority: str = Field("balanced")
```

#### 2. Refactorización del endpoint `/chat` (líneas 360-470)

**Inicialización de servicios** (línea 361-364):
```python
# Get services (always initialize - will check DB config to determine usage)
llm = get_llm()
memory_service = get_memory_service()
rag_service = get_rag_service()
```

**Lectura de configuración desde DB** (líneas 366-393):
```python
# Load session configuration from database (SINGLE SOURCE OF TRUTH)
session_config = None
memory_config = None
rag_config = None
mcp_tools_config = None

try:
    session_config = get_session_config(session_id)
    if session_config:
        memory_config = session_config.get("memory_config", {})
        rag_config = session_config.get("rag_config", {})
        mcp_tools_config = session_config.get("mcp_tools_config", {})
        print(f"✅ Loaded session config from DB for session: {session_id}")
        print(f"   Memory config: {memory_config}")
        print(f"   RAG config: {rag_config}")
        print(f"   MCP Tools config: {mcp_tools_config}")
except Exception as e:
    print(f"⚠️  Could not load session config from DB: {e}")
    # Use default disabled configs
    memory_config = {}
    rag_config = {"enabled": False}
    mcp_tools_config = {"enabled": False}
```

**Procesamiento de Memory** (líneas 395-413):
```python
# Determine if memory is enabled from DB config
memory_enabled = False
if memory_config:
    memory_enabled = (
        memory_config.get("enable_short_term", False) or
        memory_config.get("enable_semantic", False) or
        memory_config.get("enable_episodic", False) or
        memory_config.get("enable_profile", False) or
        memory_config.get("enable_procedural", False)
    )

# Store user message in memory (if enabled)
if memory_service and memory_enabled and chat_messages:
    last_msg = chat_messages[-1]
    if last_msg.role == "user":
        memory_service.add_message(session_id, last_msg)
        print(f"💾 Stored user message in memory")

# Retrieve memory context (if enabled)
memory_context = None
if memory_service and memory_enabled:
    try:
        print(f"🧠 Retrieving memory context with config: {memory_config}")
        memory_context = memory_service.get_context(
            session_id=session_id,
            memory_config=memory_config
        )
    except Exception as e:
        print(f"⚠️  Memory retrieval failed: {e}")
```

**Procesamiento de RAG** (líneas 415-457):
```python
# Retrieve RAG context (if enabled in DB)
rag_result = None
rag_enabled = rag_config.get("enabled", False) if rag_config else False

if rag_service and rag_enabled and chat_messages:
    try:
        # Extract RAG parameters from DB config
        rag_namespaces = rag_config.get("namespaces", [])
        rag_top_k = rag_config.get("top_k", 5)
        
        print(f"🔍 Performing RAG retrieval with DB config: namespaces={rag_namespaces}, top_k={rag_top_k}")
        
        # Use last user message as query
        user_query = next(
            (msg.content for msg in reversed(chat_messages) if msg.role == "user"),
            ""
        )
        
        if user_query:
            if rag_namespaces:
                # Query each namespace separately and combine results
                all_sources = []
                for namespace in rag_namespaces:
                    ns_result = rag_service.query(
                        user_query,
                        top_k=rag_top_k,
                        namespace=namespace
                    )
                    if ns_result.success and ns_result.sources:
                        all_sources.extend(ns_result.sources)
                
                # Create combined result
                if all_sources:
                    rag_result = rag_service.query(user_query, top_k=0)
                    rag_result.sources = all_sources[:rag_top_k]
                    print(f"✅ RAG retrieval successful: {len(rag_result.sources)} sources")
            else:
                # Query all namespaces
                rag_result = rag_service.query(user_query, top_k=rag_top_k)
                if rag_result and rag_result.success:
                    print(f"✅ RAG retrieval successful: {len(rag_result.sources)} sources")
    except Exception as e:
        print(f"⚠️  RAG retrieval failed: {e}")
elif not rag_enabled:
    print(f"📊 RAG is disabled in session config")
```

**Procesamiento de MCP Tools** (líneas 502-515):
```python
# Determine if tools are enabled from DB config
tools_enabled = mcp_tools_config.get("enabled", False) if mcp_tools_config else False
tool_names = mcp_tools_config.get("selected_tools", None) if mcp_tools_config else None
max_tool_iterations = mcp_tools_config.get("max_iterations", 5) if mcp_tools_config else 5

# Generate response - with or without tools (based on DB config)
if tools_enabled:
    print(f"🔧 Using tools from DB config: {tool_names}, max_iterations={max_tool_iterations}")
    response_text, agent_steps, tool_results = await llm.chat_with_tools(
        final_messages,
        tool_names=tool_names,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        max_iterations=max_tool_iterations
    )
```

### Frontend - [frontend/src/hooks/useChat.js](frontend/src/hooks/useChat.js)

#### Simplificación completa del hook

**Eliminado**:
- ❌ Import de `memoryService`
- ❌ Toda la lógica de lectura de config desde backend (80+ líneas)
- ❌ Processing de memory config y RAG config
- ❌ Construction de `finalConfig` con merge de valores

**Simplificado a** (líneas 40-75):
```javascript
const sendMessage = async (content, options = {}) => {
  if (!content.trim()) return;

  clearError();

  const userMessage = {
    role: 'user',
    content: content.trim(),
  };
  addMessage(userMessage);
  setLoading(true);

  try {
    const messagesForAPI = [{
      role: userMessage.role,
      content: userMessage.content,
    }];

    if (!sessionId) {
      throw new Error('No session ID available. Session should be initialized on app load.');
    }

    console.log('[useChat] Sending message with session_id:', sessionId);

    // Call chat service - backend reads config from DB
    const response = await chatService.sendMessage(messagesForAPI, {
      session_id: sessionId,
      temperature: options.temperature,
      max_tokens: options.max_tokens,
      max_context_tokens: options.max_context_tokens,
      context_priority: options.context_priority,
    });

    addMessage({
      role: 'assistant',
      content: response.response,
    });

    setContextData({
      context_text: response.context_text,
      context_tokens: response.context_tokens,
      token_breakdown: response.token_breakdown,
      max_context_tokens: response.max_context_tokens,
      rag_sources: response.rag_sources,
      tools_used: response.tools_used,
      tool_calls: response.tool_calls,
    });
    
    if (response.rag_sources && response.rag_sources.length > 0) {
      setRagSources(response.rag_sources);
    }

  } catch (err) {
    console.error('Failed to send message:', err);
    setError(err.message || 'Failed to send message. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

### Frontend - [frontend/src/services/chatService.js](frontend/src/services/chatService.js)

#### Simplificación de `sendMessage`

**Eliminados** todos los parámetros de configuración:
```javascript
// ❌ Eliminados:
useMemory, useRag, memoryTypes, ragNamespaces, ragTopK,
useTools, toolChoice, availableTools, maxToolIterations
```

**Simplificado a** (líneas 8-40):
```javascript
sendMessage: async (messages, config = {}) => {
  const {
    session_id = null,
    temperature = 0.7,
    max_tokens = 500,
    max_context_tokens = 4000,
    context_priority = 'balanced',
  } = config;

  const response = await apiClient.post(API_ENDPOINTS.chat, {
    messages,
    session_id,
    temperature,
    max_tokens,
    max_context_tokens,
    context_priority,
  });

  return response.data;
},
```

### Frontend - [frontend/src/components/Tabs/ChatTab.jsx](frontend/src/components/Tabs/ChatTab.jsx)

#### Simplificación del componente

**Eliminado**:
- ❌ Imports de `useCallback`, `useMemory`, `useRAG`, `useMCP`
- ❌ Hooks de configuración: `memoryEnabled`, `enabledTypes`, `ragEnabled`, `selectedNamespaces`, `toolsEnabled`, `selectedTools`
- ❌ `useCallback` con array de dependencias complejo
- ❌ Paso de parámetros de configuración a `sendMessage`

**Simplificado a** (líneas 1-31):
```javascript
import { useState } from 'react';
import { useChat } from '@hooks/useChat';
import { useDebounce } from '@utils/debounce';
import { MessageList } from '../Chat/MessageList';
import { InputBox } from '../Chat/InputBox';
import { ExportDialog } from '../Chat/ExportDialog';

/**
 * ChatTab Component
 * 
 * Configuration (memory, RAG, MCP tools) is managed by backend from database.
 * No need to pass configuration options - they are read from session_configs table.
 */
export const ChatTab = () => {
  const { messages, loading, error, sendMessage, clearError } = useChat();
  const [showExport, setShowExport] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  /**
   * Handle message send
   * Backend reads all configuration (memory, RAG, tools) from database
   */
  const handleSend = async (content) => {
    await sendMessage(content);
  };

  // ... rest of component
}
```

## Estructura de Datos en DB

### `session_configs.memory_config`
```json
{
  "enable_short_term": true,
  "enable_semantic": false,
  "enable_episodic": false,
  "enable_profile": false,
  "enable_procedural": false
}
```

### `session_configs.rag_config`
```json
{
  "enabled": true,
  "namespaces": ["LLM", "Memory"],
  "top_k": 5
}
```

### `session_configs.mcp_tools_config`
```json
{
  "enabled": true,
  "selected_tools": ["weather", "calculator"],
  "max_iterations": 5
}
```

## Flujo de Operación

```
1. Usuario activa RAG en UI
   ↓
2. Frontend: PUT /config/rag → {enabled: true, namespaces: ["LLM"]}
   ↓
3. Backend: Guarda en session_configs.rag_config
   ↓
4. Usuario envía mensaje
   ↓
5. Frontend: POST /llm/chat → {messages: [...], session_id: "..."}
   ↓
6. Backend: Lee session_configs WHERE session_id = "..."
   ↓
7. Backend: Extrae rag_config → {enabled: true, namespaces: ["LLM"]}
   ↓
8. Backend: Ejecuta RAG retrieval con config de DB
   ↓
9. Backend: Retorna response con rag_sources
   ↓
10. Frontend: Muestra respuesta con fuentes de RAG
```

## Testing Instructions

### Test 1: RAG Toggle
1. Abrir interfaz de chat
2. Ir a RAG tab → Enable RAG → Select namespace "LLM"
3. Ir a Chat tab → Enviar mensaje: "What is RAG?"
4. **Verificar en logs del backend**:
   ```
   ✅ Loaded session config from DB for session: xxx
      RAG config: {'enabled': True, 'namespaces': ['LLM'], 'top_k': 5}
   🔍 Performing RAG retrieval with DB config: namespaces=['LLM'], top_k=5
   ✅ RAG retrieval successful: X sources
   ```
5. **Verificar en frontend**: RAG Results tab muestra fuentes

### Test 2: Memory Toggle
1. Memory tab → Enable semantic memory
2. Chat tab → Enviar varios mensajes
3. **Verificar en logs del backend**:
   ```
   🧠 Retrieving memory context with config: {'enable_semantic': True, ...}
   💾 Stored user message in memory
   ```

### Test 3: MCP Tools
1. MCP tab → Enable tools → Select "weather"
2. Chat tab → Enviar: "What's the weather in Madrid?"
3. **Verificar en logs del backend**:
   ```
   🔧 Using tools from DB config: ['weather'], max_iterations=5
   ```

### Test 4: Cambios Rápidos
1. Enable RAG → Send message
2. Disable RAG → Send message
3. Enable memory → Send message
4. **Verificar**: Cada mensaje usa la config activa en ese momento

## Metrics de Simplificación

### Backend
- **Líneas eliminadas**: ~50 (parámetros de ChatRequest)
- **Líneas refactorizadas**: ~100 (lectura desde DB)
- **Complejidad**: Reducida (fuente única de verdad)

### Frontend
- **useChat.js**: 180 → 100 líneas (-44%)
- **chatService.js**: 81 → 50 líneas (-38%)
- **ChatTab.jsx**: 138 → 115 líneas (-17%)
- **Total eliminado**: ~134 líneas de código
- **Imports eliminados**: 4 (useCallback, useMemory, useRAG, useMCP, memoryService)

## Troubleshooting

### Issue: RAG no se activa
```bash
# Verificar config en DB
SELECT rag_config FROM session_configs WHERE session_id = 'xxx';

# Debe retornar: {"enabled": true, "namespaces": [...]}
```

### Issue: Backend no lee config
```bash
# Verificar logs del backend, debe mostrar:
✅ Loaded session config from DB for session: xxx
   RAG config: {'enabled': True, ...}

# Si no aparece, verificar get_session_config() en crud.py
```

### Issue: Frontend envía parámetros viejos
```bash
# Verificar request en Network tab
# Debe contener SOLO: messages, session_id, temperature, max_tokens
# NO debe contener: use_rag, use_memory, etc.
```

## Archivos Modificados

1. ✅ [src/agentlab/api/routes/chat_routes.py](src/agentlab/api/routes/chat_routes.py) - Endpoint `/chat` refactorizado
2. ✅ [frontend/src/hooks/useChat.js](frontend/src/hooks/useChat.js) - Hook simplificado
3. ✅ [frontend/src/services/chatService.js](frontend/src/services/chatService.js) - Service simplificado
4. ✅ [frontend/src/components/Tabs/ChatTab.jsx](frontend/src/components/Tabs/ChatTab.jsx) - Componente simplificado

## Próximos Pasos

1. **Testing completo** de todos los toggles (Memory, RAG, MCP)
2. **Validar edge cases**: Session sin config, servicios no disponibles
3. **Monitoreo de logs** para verificar flujo correcto
4. **Cleanup opcional**: Considerar si hooks useMemory, useRAG, useMCP aún son necesarios para UI state o si deben ser view-only

## Conclusión

Esta refactorización elimina la causa raíz de los problemas de sincronización:
- ✅ No más closures con valores stale
- ✅ No más useCallback con dependencias complejas
- ✅ No más race conditions entre updates de config
- ✅ Código más simple y mantenible
- ✅ Backend como única fuente de verdad

La configuración ahora fluye en una sola dirección:
```
UI Toggle → API Update → Database → API Read → Backend Action
```

Sin pasos intermedios que puedan causar inconsistencias.

