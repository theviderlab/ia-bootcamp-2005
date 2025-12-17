# LLM API Endpoints

Esta documentación describe los endpoints de la API para interactuar con el modelo de lenguaje (LangChainLLM).

## Configuración

Antes de usar la API, configura tu clave de API de OpenAI:

```bash
export OPENAI_API_KEY="tu-clave-api"
```

O crea un archivo `.env` en la raíz del proyecto:

```
OPENAI_API_KEY=tu-clave-api
```

## Iniciar el servidor

```bash
# Desde la raíz del proyecto
uv run uvicorn agentlab.api.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

## Endpoints disponibles

### 1. Health Check

**GET** `/health`

Verifica que el servidor esté funcionando.

**Respuesta:**
```json
{
  "status": "healthy"
}
```

### 2. Root

**GET** `/`

Información sobre la API y sus endpoints.

**Respuesta:**
```json
{
  "message": "Agent Lab API",
  "version": "0.1.0",
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "llm": {
      "generate": "/llm/generate",
      "chat": "/llm/chat"
    },
    "rag": {
      "query": "/llm/rag/query",
      "add_documents": "/llm/rag/documents",
      "add_directory": "/llm/rag/directory"
    },
    "memory": {
      "context": "/llm/memory/context",
      "history": "/llm/memory/history",
      "stats": "/llm/memory/stats",
      "search": "/llm/memory/search",
      "clear": "/llm/memory/session/{session_id}"
    },
    "config": {
      "status": "/config/status",
      "get_session": "/config/session/{session_id}",
      "update_session": "/config/session",
      "delete_session": "/config/session/{session_id}"
    },
    "mpc": {
      "create_instance": "/mpc/instances",
      "delete_instance": "/mpc/instances/{instance_id}",
      "get_instance": "/mpc/instances/{instance_id}",
      "list_instances": "/mpc/instances"
    }
  }
}
```

### 3. Generar Texto

**POST** `/llm/generate`

Genera texto a partir de un prompt usando el modelo de lenguaje.

**Request Body:**
```json
{
  "prompt": "Escribe un poema sobre Python",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Parámetros:**
- `prompt` (string, requerido): El texto de entrada para generar la respuesta
- `temperature` (float, opcional): Control de aleatoriedad (0.0 a 1.0). Default: 0.7
- `max_tokens` (int, opcional): Máximo número de tokens a generar. Default: 1000

**Respuesta:**
```json
{
  "text": "En bits y bytes se escribe,\nPython el lenguaje que vive...",
  "prompt": "Escribe un poema sobre Python"
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "¿Qué es Python?",
    "temperature": 0.5,
    "max_tokens": 200
  }'
```

### 4. Chat

**POST** `/llm/chat`

Genera una respuesta de chat basada en el historial de conversación.

**Request Body:**
```json
{
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente útil y amigable."
    },
    {
      "role": "user",
      "content": "¿Qué es FastAPI?"
    },
    {
      "role": "assistant",
      "content": "FastAPI es un framework web moderno para Python..."
    },
    {
      "role": "user",
      "content": "¿Cuáles son sus ventajas?"
    }
  ],
  "session_id": "opcional-id-de-sesion",
  "temperature": 0.7,
  "max_tokens": 500,
  "use_memory": true,
  "use_rag": false,
  "memory_types": ["semantic", "episodic"],
  "rag_namespaces": ["docs", "api"],
  "rag_top_k": 5,
  "max_context_tokens": 4000,
  "context_priority": "balanced"
}
```

**Parámetros:**
- `messages` (array, requerido): Lista de mensajes de la conversación
  - Cada mensaje debe tener:
    - `role`: "user", "assistant", o "system"
    - `content`: El contenido del mensaje
- `session_id` (string, opcional): ID de sesión para rastrear la conversación y gestionar memoria
- `temperature` (float, opcional): Control de aleatoriedad (0.0 a 1.0). Default: 0.7
- `max_tokens` (int, opcional): Máximo número de tokens a generar. Default: 500

**Parámetros avanzados de contexto:**
- `use_memory` (bool, opcional): Habilitar contexto de memoria. Default: true
- `use_rag` (bool, opcional): Habilitar recuperación RAG. Default: false
- `memory_types` (array[string], opcional): Tipos específicos de memoria a incluir: "semantic", "episodic", "profile", "procedural". Si no se especifica, usa todos.
- `rag_namespaces` (array[string], opcional): Namespaces específicos de Pinecone para buscar. Si no se especifica, busca en todos.
- `rag_top_k` (int, opcional): Número de documentos RAG a recuperar (1-20). Default: 5
- `max_context_tokens` (int, opcional): Máximo de tokens para el contexto combinado (100-8000). Default: 4000
- `context_priority` (string, opcional): Prioridad de contexto: "memory" (priorizar memoria), "rag" (priorizar RAG), o "balanced" (equilibrado). Default: "balanced"

**Respuesta:**
```json
{
  "response": "Las principales ventajas de FastAPI son...",
  "session_id": "uuid-generado-o-proporcionado"
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "Eres un asistente conciso."},
      {"role": "user", "content": "Explica SOLID"}
    ],
    "temperature": 0.5,
    "max_tokens": 300
  }'
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hola, ¿cómo estás?"}
    ]
  }'
```

### 5. RAG Query

**POST** `/llm/rag/query`

Consulta el sistema RAG (Retrieval-Augmented Generation) para obtener respuestas basadas en documentos indexados en la base de conocimiento.

**Request Body:**
```json
{
  "query": "¿Qué es FastAPI y cuáles son sus características principales?",
  "top_k": 5,
  "namespace": "documentacion"
}
```

**Parámetros:**
- `query` (string, requerido): La pregunta o consulta a realizar sobre la base de conocimiento
- `top_k` (int, opcional): Número de documentos relevantes a recuperar (1-20). Default: 5
- `namespace` (string, opcional): Namespace específico para buscar. Si no se proporciona, busca en todos los namespaces

**Respuesta:**
```json
{
  "success": true,
  "response": "FastAPI es un framework web moderno y de alto rendimiento para Python 3.7+. Sus características principales incluyen...",
  "sources": [
    {
      "content": "FastAPI es un framework web...",
      "metadata": {
        "source": "docs/fastapi_intro.md",
        "chunk_index": 0
      },
      "score": 0.89
    }
  ],
  "error_message": null
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cómo implementar autenticación?",
    "top_k": 3
  }'
```

### 6. Agregar Documentos a RAG

**POST** `/llm/rag/documents`

Agrega documentos al sistema RAG. Los documentos pueden ser texto plano o rutas a archivos. Los archivos soportados incluyen: `.txt`, `.md`, `.log`.

**Request Body:**
```json
{
  "documents": [
    "Este es un documento de texto plano sobre Python.",
    "/ruta/al/archivo.md",
    "/ruta/al/archivo.txt"
  ],
  "namespace": "documentacion",
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

**Parámetros:**
- `documents` (array, requerido): Lista de textos o rutas de archivos a agregar
- `namespace` (string, opcional): Namespace para organizar los documentos
- `chunk_size` (int, opcional): Máximo de caracteres por fragmento (100-4000). Default: 1000
- `chunk_overlap` (int, opcional): Caracteres de superposición entre fragmentos (0-1000). Default: 200

**Respuesta:**
```json
{
  "success": true,
  "message": "Successfully added 3 documents",
  "documents_added": 3
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/rag/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Python es un lenguaje de programación interpretado.",
      "./docs/README.md"
    ],
    "namespace": "tutoriales"
  }'
```

### 7. Agregar Directorio a RAG

**POST** `/llm/rag/directory`

Agrega todos los documentos de un directorio al sistema RAG. Busca recursivamente archivos soportados y los indexa con chunking y metadata.

**Request Body:**
```json
{
  "directory": "./docs",
  "namespace": "documentacion",
  "recursive": true,
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

**Parámetros:**
- `directory` (string, requerido): Ruta al directorio que contiene los documentos
- `namespace` (string, opcional): Namespace para organizar los documentos
- `recursive` (bool, opcional): Buscar en subdirectorios recursivamente. Default: true
- `chunk_size` (int, opcional): Máximo de caracteres por fragmento (100-4000). Default: 1000
- `chunk_overlap` (int, opcional): Caracteres de superposición entre fragmentos (0-1000). Default: 200

**Respuesta:**
```json
{
  "success": true,
  "message": "Successfully added 15 documents from directory",
  "documents_added": 15
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/rag/directory" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "./docs",
    "namespace": "docs",
    "recursive": true
  }'
```

### 7bis. Eliminar Namespace RAG

**DELETE** `/llm/rag/namespace/{namespace}`

Elimina todos los documentos y vectores asociados a un namespace específico en Pinecone. Útil para limpieza y testing.

**Path Parameters:**
- `namespace` (string, requerido): El namespace a eliminar

**URL de ejemplo:**
```
DELETE /llm/rag/namespace/test-namespace
```

**Respuesta:**
```json
{
  "success": true,
  "namespace": "test-namespace",
  "message": "Namespace 'test-namespace' deleted successfully"
}
```

**Ejemplo con curl:**
```bash
curl -X DELETE "http://localhost:8000/llm/rag/namespace/test-namespace"
```

**⚠️ Advertencia:** Esta operación es irreversible. Todos los documentos en el namespace serán eliminados permanentemente.

### 8. Gestión de Memoria (Memory Operations)

Los endpoints de memoria permiten gestionar el contexto conversacional, recuperar historiales, obtener estadísticas y realizar búsquedas semánticas.

#### 8.1 Obtener Contexto de Memoria

**POST** `/llm/memory/context`

Recupera el contexto de memoria completo para una sesión, incluyendo buffer de corto plazo, hechos semánticos, perfil de usuario, resumen episódico y patrones procedimentales.

**Request Body:**
```json
{
  "session_id": "uuid-de-sesion",
  "max_tokens": 2000,
  "memory_types": ["semantic", "episodic", "profile"]
}
```

**Parámetros:**
- `session_id` (string, requerido): ID de la sesión de conversación
- `max_tokens` (int, opcional): Máximo de tokens para el contexto (100-8000). Default: 2000
- `memory_types` (array[string], opcional): Tipos específicos de memoria: "semantic", "episodic", "profile", "procedural". Si no se especifica, retorna todos.

**Respuesta:**
```json
{
  "session_id": "uuid-de-sesion",
  "context": {
    "short_term": "Últimos 5 mensajes de la conversación...",
    "semantic_facts": ["El usuario está aprendiendo Python", "Le interesa FastAPI"],
    "user_profile": {
      "experience_level": "intermediate",
      "interests": ["python", "apis", "testing"]
    },
    "episodic_summary": "El usuario ha preguntado sobre testing en Python y mejores prácticas...",
    "procedural_patterns": ["Prefiere ejemplos con código", "Solicita validaciones"]
  },
  "token_count": 1847,
  "truncated": false
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/memory/context" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "mi-sesion-123",
    "max_tokens": 2000
  }'
```

#### 8.2 Obtener Historial de Conversación

**GET** `/llm/memory/history`

Recupera el historial completo de mensajes de una conversación con timestamps y metadata.

**Query Parameters:**
- `session_id` (string, requerido): ID de la sesión
- `limit` (int, opcional): Número máximo de mensajes a retornar (1-1000). Default: 100
- `offset` (int, opcional): Número de mensajes a saltar para paginación. Default: 0

**URL de ejemplo:**
```
GET /llm/memory/history?session_id=mi-sesion-123&limit=50&offset=0
```

**Respuesta:**
```json
{
  "session_id": "mi-sesion-123",
  "messages": [
    {
      "role": "user",
      "content": "¿Qué es FastAPI?",
      "timestamp": "2025-12-17T10:30:00.123456",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "FastAPI es un framework web moderno...",
      "timestamp": "2025-12-17T10:30:02.456789",
      "metadata": {"tokens_used": 150}
    }
  ],
  "total_messages": 24,
  "has_more": false
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/llm/memory/history?session_id=mi-sesion-123&limit=50"
```

#### 8.3 Obtener Estadísticas de Memoria

**GET** `/llm/memory/stats`

Recupera estadísticas detalladas sobre el uso de memoria para una sesión.

**Query Parameters:**
- `session_id` (string, requerido): ID de la sesión

**URL de ejemplo:**
```
GET /llm/memory/stats?session_id=mi-sesion-123
```

**Respuesta:**
```json
{
  "session_id": "mi-sesion-123",
  "message_count": 24,
  "total_tokens": 12500,
  "semantic_facts_count": 15,
  "profile_attributes": 8,
  "first_message": "2025-12-17T08:00:00.000000",
  "last_message": "2025-12-17T11:45:00.123456",
  "memory_types": {
    "semantic": {"enabled": true, "facts": 15},
    "episodic": {"enabled": true, "summaries": 3},
    "profile": {"enabled": true, "attributes": 8},
    "procedural": {"enabled": true, "patterns": 5}
  }
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/llm/memory/stats?session_id=mi-sesion-123"
```

#### 8.4 Búsqueda Semántica en Memoria

**POST** `/llm/memory/search`

Busca en la memoria semántica usando similitud vectorial. **Requiere configuración de Pinecone**.

**Request Body:**
```json
{
  "query": "preguntas sobre testing en Python",
  "top_k": 5,
  "session_id": null
}
```

**Parámetros:**
- `query` (string, requerido): Consulta de búsqueda semántica
- `top_k` (int, opcional): Número de resultados a retornar (1-20). Default: 5
- `session_id` (string, opcional): Filtrar por sesión específica. Si es null, busca en todas las sesiones.

**Respuesta:**
```json
{
  "query": "preguntas sobre testing en Python",
  "results": [
    {
      "content": "¿Cómo hacer testing en Python con pytest?",
      "session_id": "sesion-abc",
      "timestamp": "2025-12-17T09:15:00.000000",
      "score": 0.92,
      "metadata": {
        "message_type": "user_query",
        "topic": "testing"
      }
    }
  ],
  "total_results": 5
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "preguntas sobre APIs REST",
    "top_k": 3
  }'
```

**Nota:** Este endpoint requiere que `PINECONE_API_KEY` esté configurada. Si no está disponible, retornará un error 500.

#### 8.5 Limpiar Memoria de Sesión

**DELETE** `/llm/memory/session/{session_id}`

Elimina todos los datos de memoria asociados a una sesión específica.

**Path Parameters:**
- `session_id` (string, requerido): ID de la sesión a limpiar

**URL de ejemplo:**
```
DELETE /llm/memory/session/mi-sesion-123
```

**Respuesta:**
```json
{
  "success": true,
  "session_id": "mi-sesion-123",
  "message": "Memory cleared successfully",
  "items_deleted": {
    "messages": 24,
    "semantic_facts": 15,
    "profile_data": 8,
    "vector_embeddings": 24
  }
}
```

**Ejemplo con curl:**
```bash
curl -X DELETE "http://localhost:8000/llm/memory/session/mi-sesion-123"
```

### 9. Gestión de Configuración (Configuration Management)

Los endpoints de configuración permiten gestionar settings de sesión, toggles de memoria y RAG, y obtener el estado del sistema.

#### 9.1 Obtener Estado de Configuración

**GET** `/config/status`

Obtiene el estado actual de configuración del sistema, incluyendo servicios disponibles y configuraciones globales.

**Respuesta:**
```json
{
  "system": {
    "version": "0.1.0",
    "environment": "development"
  },
  "services": {
    "llm": {
      "available": true,
      "model": "gpt-4",
      "provider": "openai"
    },
    "memory": {
      "available": true,
      "database": "mysql",
      "vector_store": "pinecone"
    },
    "rag": {
      "available": true,
      "index_name": "agentlab-knowledge",
      "dimension": 1536
    }
  },
  "default_config": {
    "memory": {
      "enabled": true,
      "types": ["semantic", "episodic", "profile", "procedural"]
    },
    "rag": {
      "enabled": false,
      "default_top_k": 5,
      "default_namespace": null
    }
  }
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/config/status"
```

#### 9.2 Obtener Configuración de Sesión

**GET** `/config/session/{session_id}`

Obtiene la configuración específica de una sesión.

**Path Parameters:**
- `session_id` (string, requerido): ID de la sesión

**URL de ejemplo:**
```
GET /config/session/mi-sesion-123
```

**Respuesta:**
```json
{
  "session_id": "mi-sesion-123",
  "memory": {
    "enabled": true,
    "types": ["semantic", "episodic"]
  },
  "rag": {
    "enabled": true,
    "namespaces": ["docs", "api"],
    "top_k": 5
  },
  "preferences": {
    "context_priority": "balanced",
    "max_context_tokens": 4000
  },
  "created_at": "2025-12-17T08:00:00.000000",
  "updated_at": "2025-12-17T10:30:00.000000"
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/config/session/mi-sesion-123"
```

#### 9.3 Actualizar Configuración de Sesión

**POST** `/config/session`

Crea o actualiza la configuración de una sesión.

**Request Body:**
```json
{
  "session_id": "mi-sesion-123",
  "memory": {
    "enabled": true,
    "types": ["semantic", "profile"]
  },
  "rag": {
    "enabled": true,
    "namespaces": ["docs"],
    "top_k": 3
  },
  "preferences": {
    "context_priority": "memory",
    "max_context_tokens": 3000
  }
}
```

**Parámetros:**
- `session_id` (string, requerido): ID de la sesión
- `memory` (object, opcional): Configuración de memoria
  - `enabled` (bool): Habilitar memoria
  - `types` (array[string]): Tipos de memoria a usar
- `rag` (object, opcional): Configuración RAG
  - `enabled` (bool): Habilitar RAG
  - `namespaces` (array[string]): Namespaces a buscar
  - `top_k` (int): Número de documentos a recuperar
- `preferences` (object, opcional): Preferencias generales
  - `context_priority` (string): "memory", "rag", o "balanced"
  - `max_context_tokens` (int): Máximo de tokens de contexto

**Respuesta:**
```json
{
  "success": true,
  "session_id": "mi-sesion-123",
  "message": "Configuration updated successfully",
  "config": {
    "memory": {"enabled": true, "types": ["semantic", "profile"]},
    "rag": {"enabled": true, "namespaces": ["docs"], "top_k": 3},
    "preferences": {"context_priority": "memory", "max_context_tokens": 3000}
  }
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/config/session" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "mi-sesion-123",
    "memory": {"enabled": true, "types": ["semantic"]},
    "rag": {"enabled": false}
  }'
```

#### 9.4 Eliminar Configuración de Sesión

**DELETE** `/config/session/{session_id}`

Elimina la configuración personalizada de una sesión. La sesión volverá a usar configuración por defecto.

**Path Parameters:**
- `session_id` (string, requerido): ID de la sesión

**URL de ejemplo:**
```
DELETE /config/session/mi-sesion-123
```

**Respuesta:**
```json
{
  "success": true,
  "session_id": "mi-sesion-123",
  "message": "Session configuration deleted. Session will use default configuration."
}
```

**Ejemplo con curl:**
```bash
curl -X DELETE "http://localhost:8000/config/session/mi-sesion-123"
```

#### 9.5 Actualizar Toggles de Memoria

**PUT** `/config/memory`

Actualiza la configuración global de memoria o de una sesión específica.

**Request Body:**
```json
{
  "session_id": "mi-sesion-123",
  "enabled": true,
  "types": ["semantic", "episodic", "profile"]
}
```

**Parámetros:**
- `session_id` (string, opcional): ID de sesión. Si no se proporciona, actualiza configuración global.
- `enabled` (bool, requerido): Habilitar/deshabilitar memoria
- `types` (array[string], opcional): Tipos de memoria a habilitar

**Respuesta:**
```json
{
  "success": true,
  "message": "Memory configuration updated",
  "config": {
    "enabled": true,
    "types": ["semantic", "episodic", "profile"]
  }
}
```

**Ejemplo con curl:**
```bash
curl -X PUT "http://localhost:8000/config/memory" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "mi-sesion-123",
    "enabled": true,
    "types": ["semantic"]
  }'
```

#### 9.6 Actualizar Toggles de RAG

**PUT** `/config/rag`

Actualiza la configuración global de RAG o de una sesión específica.

**Request Body:**
```json
{
  "session_id": "mi-sesion-123",
  "enabled": true,
  "namespaces": ["docs", "api"],
  "top_k": 5
}
```

**Parámetros:**
- `session_id` (string, opcional): ID de sesión. Si no se proporciona, actualiza configuración global.
- `enabled` (bool, requerido): Habilitar/deshabilitar RAG
- `namespaces` (array[string], opcional): Namespaces específicos a buscar
- `top_k` (int, opcional): Número de documentos a recuperar

**Respuesta:**
```json
{
  "success": true,
  "message": "RAG configuration updated",
  "config": {
    "enabled": true,
    "namespaces": ["docs", "api"],
    "top_k": 5
  }
}
```

**Ejemplo con curl:**
```bash
curl -X PUT "http://localhost:8000/config/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "namespaces": ["docs"],
    "top_k": 3
  }'
```

## Códigos de Estado HTTP

- `200`: Éxito
- `400`: Error de validación o parámetros inválidos
- `404`: Recurso no encontrado (ej: directorio no existe, sesión no encontrada)
- `422`: Error de validación de Pydantic (campos requeridos, tipos incorrectos)
- `500`: Error interno del servidor (ej: fallo en la generación del LLM, error de Pinecone)
- `501`: No implementado (endpoints MPC)

## Formatos de Respuesta de Error

La API utiliza formatos de error estándar de FastAPI:

### Error Simple (400, 404, 500)

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Ejemplo - 404 Not Found:**
```json
{
  "detail": "Session not found: abc-123"
}
```

**Ejemplo - 500 Internal Server Error:**
```json
{
  "detail": "Failed to initialize RAG service. Please ensure Pinecone and OpenAI API keys are configured."
}
```

### Error de Validación Pydantic (422)

Cuando faltan campos requeridos o los tipos son incorrectos:

```json
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "temperature"],
      "msg": "ensure this value is less than or equal to 1.0",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 1.0}
    }
  ]
}
```

**Campos en error de validación:**
- `loc` (array): Ubicación del error (["body", "field_name"] para request body)
- `msg` (string): Mensaje descriptivo del error
- `type` (string): Tipo de error de validación
- `ctx` (object, opcional): Contexto adicional (ej: límites de valores)

**Ejemplos comunes de validación:**

1. **Campo requerido faltante:**
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

2. **Tipo incorrecto:**
```json
{
  "detail": [
    {
      "loc": ["body", "top_k"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

3. **Valor fuera de rango:**
```json
{
  "detail": [
    {
      "loc": ["body", "max_tokens"],
      "msg": "ensure this value is less than or equal to 8000",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 8000}
    }
  ]
}
```

4. **Array vacío cuando se requiere mínimo:**
```json
{
  "detail": [
    {
      "loc": ["body", "messages"],
      "msg": "ensure this value has at least 1 items",
      "type": "value_error.list.min_items",
      "ctx": {"limit_value": 1}
    }
  ]
}
```

### Manejo de Errores en Cliente

**Python:**
```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/llm/generate",
        json={"prompt": "test"}
    )
    response.raise_for_status()  # Lanza excepción si status >= 400
    result = response.json()
except requests.exceptions.HTTPError as e:
    if response.status_code == 422:
        # Error de validación Pydantic
        errors = response.json()["detail"]
        for error in errors:
            print(f"Campo {error['loc']}: {error['msg']}")
    else:
        # Otro error HTTP
        print(f"Error {response.status_code}: {response.json()['detail']}")
except requests.exceptions.RequestException as e:
    print(f"Error de conexión: {e}")
```

**JavaScript:**
```javascript
try {
  const response = await fetch('http://localhost:8000/llm/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: [] })
  });
  
  if (!response.ok) {
    const error = await response.json();
    if (response.status === 422) {
      // Error de validación
      error.detail.forEach(err => {
        console.error(`Field ${err.loc.join('.')}: ${err.msg}`);
      });
    } else {
      // Otro error
      console.error(`Error ${response.status}: ${error.detail}`);
    }
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error('Request failed:', error);
}
```

## Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Ejemplos con Python

### Generar texto

```python
import requests

response = requests.post(
    "http://localhost:8000/llm/generate",
    json={
        "prompt": "Explica qué es machine learning",
        "temperature": 0.7,
        "max_tokens": 500
    }
)

result = response.json()
print(result["text"])
```

### Chat

```python
import requests

response = requests.post(
    "http://localhost:8000/llm/chat",
    json={
        "messages": [
            {"role": "system", "content": "Eres un experto en Python"},
            {"role": "user", "content": "¿Cómo funcionan los decoradores?"}
        ]
    }
)

result = response.json()
print(f"Session: {result['session_id']}")
print(f"Response: {result['response']}")
```

### RAG Query

```python
import requests

# Consultar la base de conocimiento
response = requests.post(
    "http://localhost:8000/llm/rag/query",
    json={
        "query": "¿Qué es SOLID y cuáles son sus principios?",
        "top_k": 5,
        "namespace": "documentacion"
    }
)

result = response.json()
if result["success"]:
    print(f"Respuesta: {result['response']}")
    print(f"\nFuentes ({len(result['sources'])}):\n")
    for i, source in enumerate(result['sources'], 1):
        print(f"{i}. {source['metadata'].get('source', 'Unknown')} (score: {source.get('score', 0):.2f})")
else:
    print(f"Error: {result['error_message']}")
```

### Agregar documentos a RAG

```python
import requests

# Agregar documentos individuales
response = requests.post(
    "http://localhost:8000/llm/rag/documents",
    json={
        "documents": [
            "Python es un lenguaje de programación de alto nivel.",
            "./docs/python_intro.md",
            "./docs/fastapi_guide.txt"
        ],
        "namespace": "tutoriales",
        "chunk_size": 1000,
        "chunk_overlap": 200
    }
)

result = response.json()
print(f"Documentos agregados: {result['documents_added']}")
print(result['message'])
```

### Agregar directorio a RAG

```python
import requests

# Agregar todos los documentos de un directorio
response = requests.post(
    "http://localhost:8000/llm/rag/directory",
    json={
        "directory": "./docs",
        "namespace": "documentacion",
        "recursive": True,
        "chunk_size": 1000,
        "chunk_overlap": 200
    }
)

result = response.json()
if result["success"]:
    print(f"✅ {result['message']}")
    print(f"Total documentos: {result['documents_added']}")
else:
    print(f"❌ Error al agregar directorio")
```

## Testing

Ejecutar los tests unitarios:

```bash
# Todos los tests
make test-unit

# Solo tests de API
uv run pytest tests/unit/test_chat_routes.py -v
```

## Notas

- La API usa una instancia global del LLM para eficiencia. En producción, se recomienda usar dependency injection de FastAPI.
- El `session_id` actualmente es solo para tracking. La gestión de estado de sesión se implementará en futuras iteraciones.
- Los errores de OpenAI (límite de rate, problemas de red, etc.) se capturan y devuelven como errores 500.

### Notas sobre RAG

- **Configuración requerida**: Los endpoints RAG requieren claves de API de Pinecone y OpenAI configuradas en el archivo `.env`:
  ```bash
  OPENAI_API_KEY=tu-clave-openai
  PINECONE_API_KEY=tu-clave-pinecone
  PINECONE_ENVIRONMENT=tu-environment
  PINECONE_INDEX_NAME=tu-index
  ```
- **Tipos de archivo soportados**: Actualmente `.txt`, `.md`, `.log`. Se pueden agregar más tipos registrando nuevos loaders.
- **Namespaces**: Usa namespaces para organizar documentos por categoría (ej: "docs", "tutoriales", "api").
- **Chunking**: Los documentos se dividen en fragmentos para mejor recuperación. Ajusta `chunk_size` y `chunk_overlap` según tus necesidades.
- **Embeddings**: Los documentos se convierten en embeddings usando el modelo de OpenAI configurado.
- **Búsqueda semántica**: El sistema usa búsqueda de similitud coseno para encontrar documentos relevantes.
- **Inicialización**: El servicio RAG se inicializa la primera vez que se usa y se mantiene en memoria. Si hay errores de configuración, todos los endpoints RAG fallarán con código 500.
