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

## Referencia de API

Para documentación detallada de los endpoints de configuración y ejemplos de uso, consulta [API.md](API.md).

Los endpoints relevantes son:
- `GET /config/status`: Estado del sistema
- `GET /config/session/{session_id}`: Configuración de sesión
- `POST /config/session`: Crear/Actualizar configuración
- `DELETE /config/session/{session_id}`: Resetear configuración
- `POST /llm/chat`: Uso de parámetros de configuración en tiempo de ejecución


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
