# Dynamic Configuration System

Sistema de configuración dinámica para habilitar/deshabilitar componentes de memoria y RAG en tiempo de ejecución.

## Características Principales

### 1. **Control Granular de Memoria**

Puedes habilitar/deshabilitar tipos específicos de memoria:

- **Short-term**: Buffer de conversación reciente
- **Semantic**: Extracción de hechos semánticos
- **Episodic**: Resúmenes episódicos temporales
- **Profile**: Construcción de perfil de usuario
- **Procedural**: Detección de patrones de interacción

### 2. **Control de RAG por Namespace**

- Habilitar/deshabilitar RAG completamente
- Especificar namespaces específicos a consultar
- Control de cantidad de documentos a recuperar (top_k)

### 3. **Configuración por Sesión**

- Configuraciones persistidas en base de datos
- Asociadas a `session_id`
- Cada sesión puede tener configuración diferente

### 4. **Degradación Graceful**

- Servicios retornan `None` si no están disponibles
- Warnings en lugar de errores
- Chat funciona sin memoria o RAG si están deshabilitados

## Variables de Entorno

### RAG

```bash
# Habilitar/deshabilitar RAG globalmente
ENABLE_RAG=true  # default: true

# Configuración de Pinecone (requerida si RAG está habilitado)
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=index_name
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

### Memoria

```bash
# Control global de memoria long-term
ENABLE_LONG_TERM=true  # default: true

# Tipos específicos de memoria
ENABLE_SEMANTIC_MEMORY=true  # default: true
ENABLE_EPISODIC_MEMORY=true  # default: true
ENABLE_PROFILE_MEMORY=true   # default: true
ENABLE_PROCEDURAL_MEMORY=true  # default: true

# Estrategia de almacenamiento semántico
SEMANTIC_STORAGE=hybrid  # mysql | pinecone | hybrid (default: hybrid)
```

## API Endpoints

### 1. **GET /config/status**

Obtener estado actual del sistema (servicios disponibles, warnings).

**Response:**
```json
{
  "memory_available": true,
  "rag_available": false,
  "current_config": {
    "session_id": "default",
    "memory": {
      "enable_short_term": true,
      "enable_semantic": true,
      "enable_episodic": true,
      "enable_profile": true,
      "enable_procedural": true
    },
    "rag": {
      "enable_rag": false,
      "namespaces": [],
      "top_k": 5
    }
  },
  "warnings": [
    "RAG service unavailable. Check Pinecone configuration."
  ],
  "dependencies": {
    "llm": true,
    "memory": true,
    "rag": false,
    "openai": true,
    "pinecone": false
  }
}
```

### 2. **GET /config/session/{session_id}**

Obtener configuración de una sesión específica.

**Response:**
```json
{
  "config": {
    "session_id": "my-session-123",
    "memory": {
      "enable_short_term": true,
      "enable_semantic": true,
      "enable_episodic": false,
      "enable_profile": true,
      "enable_procedural": false
    },
    "rag": {
      "enable_rag": true,
      "namespaces": ["product_docs", "user_manual"],
      "top_k": 10
    }
  },
  "message": "Configuration retrieved successfully"
}
```

### 3. **POST /config/session**

Crear o actualizar configuración de sesión.

**Request:**
```json
{
  "session_id": "my-session-123",
  "memory": {
    "enable_semantic": true,
    "enable_episodic": false
  },
  "rag": {
    "enable_rag": true,
    "namespaces": ["docs", "tutorials"],
    "top_k": 5
  }
}
```

**Response:**
```json
{
  "config": { /* configuración actualizada */ },
  "message": "Configuration updated successfully"
}
```

### 4. **DELETE /config/session/{session_id}**

Eliminar configuración de sesión (vuelve a defaults).

**Response:**
```json
{
  "message": "Configuration for session my-session-123 deleted successfully"
}
```

## Uso en el Endpoint /llm/chat

### Configuración por Request

El endpoint `/llm/chat` ahora acepta parámetros de configuración runtime:

```json
POST /llm/chat
{
  "messages": [
    {"role": "user", "content": "¿Qué es FastAPI?"}
  ],
  "session_id": "my-session",
  
  // Toggles principales
  "use_memory": true,
  "use_rag": true,
  
  // Configuración de memoria
  "memory_types": ["semantic", "profile"],
  
  // Configuración de RAG
  "rag_namespaces": ["fastapi_docs", "python_docs"],
  "rag_top_k": 5,
  
  // Configuración de contexto
  "max_context_tokens": 4000,
  "context_priority": "balanced",  // "memory" | "rag" | "balanced"
  
  // Parámetros LLM
  "temperature": 0.7,
  "max_tokens": 500
}
```

### Ejemplos de Uso

#### 1. Chat sin memoria ni RAG (básico)

```bash
curl -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "use_memory": false,
    "use_rag": false
  }'
```

#### 2. Chat solo con memoria short-term

```bash
curl -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What did we discuss?"}],
    "session_id": "my-session",
    "use_memory": true,
    "use_rag": false
  }'
```

#### 3. Chat con RAG específico por namespace

```bash
curl -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "How to use FastAPI?"}],
    "use_memory": false,
    "use_rag": true,
    "rag_namespaces": ["fastapi_docs"],
    "rag_top_k": 3
  }'
```

#### 4. Chat con memoria + RAG combinados

```bash
curl -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Based on what I told you, recommend a framework"}],
    "session_id": "my-session",
    "use_memory": true,
    "use_rag": true,
    "rag_namespaces": ["frameworks"],
    "context_priority": "balanced"
  }'
```

## Arquitectura

### Context Builder

El `ContextBuilder` combina información de memoria y RAG:

```python
from agentlab.core.context_builder import ContextBuilder

builder = ContextBuilder(max_tokens=4000)

# Combinar contextos
combined_context = builder.build_context(
    memory_context=memory_context,
    rag_result=rag_result,
    prioritize="balanced"  # "memory" | "rag" | "balanced"
)

# Formatear para prompt
formatted_text = builder.format_for_prompt(combined_context)
```

### Estructura de Contexto Combinado

```python
@dataclass
class CombinedContext:
    # Memoria
    short_term_history: str
    semantic_facts: list[str] | None
    user_profile: dict[str, Any] | None
    episodic_summary: str
    procedural_patterns: list[str] | None
    
    # RAG
    rag_documents: list[dict[str, Any]] | None
    rag_context: str
    
    # Metadata
    total_tokens_estimated: int
    truncated: bool
    truncation_strategy: str | None
    warnings: list[str] | None
```

## Persistencia de Configuración

Las configuraciones se guardan en la tabla `session_configs`:

```sql
CREATE TABLE session_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    memory_config JSON NOT NULL,
    rag_config JSON NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id)
);
```

## Estrategias de Truncamiento (Futuro)

Actualmente el `ContextBuilder` estima tokens pero no trunca. Futuras estrategias:

1. **Priority-based**: Truncar según `context_priority`
   - `"memory"`: Mantener toda la memoria, truncar RAG
   - `"rag"`: Mantener todo el RAG, truncar memoria
   - `"balanced"`: Distribuir equitativamente

2. **Recency-based**: Priorizar información más reciente

3. **Relevance-based**: Usar scores de similitud para mantener lo más relevante

## Testing

### Unit Tests

```bash
# Tests de context builder
uv run pytest tests/unit/test_context_builder.py -v

# Tests de config models
uv run pytest tests/unit/test_config_models.py -v

# Tests de CRUD
uv run pytest tests/unit/test_session_config_crud.py -v
```

### Postman Tests

Actualizar la colección Postman agregando tests para:

1. GET /config/status
2. GET /config/session/{session_id}
3. POST /config/session
4. DELETE /config/session/{session_id}
5. POST /llm/chat con diferentes combinaciones de configuración

## Ejemplo de Flujo Completo

```python
# 1. Crear sesión con configuración personalizada
POST /config/session
{
  "session_id": "user-123",
  "memory": {
    "enable_semantic": true,
    "enable_profile": true,
    "enable_episodic": false
  },
  "rag": {
    "enable_rag": true,
    "namespaces": ["product_docs"],
    "top_k": 5
  }
}

# 2. Iniciar conversación
POST /llm/chat
{
  "messages": [{"role": "user", "content": "I'm interested in your product"}],
  "session_id": "user-123",
  "use_memory": true,
  "use_rag": true
}

# 3. Continuar conversación (usa configuración guardada)
POST /llm/chat
{
  "messages": [
    {"role": "user", "content": "I'm interested in your product"},
    {"role": "assistant", "content": "Great! Let me help you..."},
    {"role": "user", "content": "What are the pricing options?"}
  ],
  "session_id": "user-123",
  "use_memory": true,
  "use_rag": true,
  "rag_namespaces": ["pricing"]  // Override para este request
}

# 4. Ver configuración actual
GET /config/session/user-123

# 5. Actualizar solo RAG namespaces
PUT /config/rag?session_id=user-123
{
  "enable_rag": true,
  "namespaces": ["pricing", "features"],
  "top_k": 10
}

# 6. Cleanup al final
DELETE /config/session/user-123
```

## Validación de Dependencias

El sistema valida automáticamente dependencias:

- **OPENAI_API_KEY**: Requerida para LLM
- **Database**: Requerida para memoria
- **PINECONE_API_KEY**: Requerida para RAG con Pinecone
- **ENABLE_RAG**: Flag para deshabilitar RAG

Si falta una dependencia:
- El servicio retorna `None`
- Se registra warning
- El chat continúa sin ese componente

## Roadmap

- [ ] Implementar estrategias de truncamiento inteligente
- [ ] Agregar métricas de uso de contexto
- [ ] Dashboard frontend para visualizar configuraciones
- [ ] Webhooks para notificar cambios de configuración
- [ ] Templates de configuración predefinidos
- [ ] Batch updates de configuración
