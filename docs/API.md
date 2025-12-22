# Agent Lab API Documentation

**Version:** 1.0.0  
**Last Updated:** December 21, 2025

Esta documentación describe los endpoints de la API para interactuar con el sistema Agent Lab, que incluye generación de texto con LLM, sistema RAG (Retrieval-Augmented Generation), gestión de memoria conversacional, herramientas MCP (Model Context Protocol), y configuración dinámica.

---

## Tabla de Contenidos

### [1. Introducción](#1-introducción)
- [1.1 Configuración](#11-configuración)
- [1.2 Variables de Entorno](#12-variables-de-entorno)
- [1.3 Iniciar el Servidor](#13-iniciar-el-servidor)
- [1.4 Códigos de Estado HTTP](#14-códigos-de-estado-http)

### [2. Endpoints Base](#2-endpoints-base)
- [2.1 Health Check](#21-health-check)
- [2.2 Root / Información de API](#22-root--información-de-api)

### [3. Endpoints LLM](#3-endpoints-llm)
- [3.1 Generar Texto](#31-generar-texto)
- [3.2 Chat](#32-chat)

### [4. Endpoints RAG](#4-endpoints-rag)
- [4.1 Consultar Base de Conocimiento](#41-consultar-base-de-conocimiento)
- [4.2 Agregar Documentos](#42-agregar-documentos)
- [4.3 Agregar Directorio](#43-agregar-directorio)
- [4.4 Listar Namespaces](#44-listar-namespaces)
- [4.5 Listar Documentos](#45-listar-documentos)
- [4.6 Obtener Estadísticas de Namespace](#46-obtener-estadísticas-de-namespace)
- [4.7 Eliminar Namespace](#47-eliminar-namespace)

### [5. Endpoints de Memoria](#5-endpoints-de-memoria)
- [5.1 Obtener Contexto de Memoria](#51-obtener-contexto-de-memoria)
- [5.2 Obtener Historial de Conversación](#52-obtener-historial-de-conversación)
- [5.3 Obtener Estadísticas de Memoria](#53-obtener-estadísticas-de-memoria)
- [5.4 Búsqueda Semántica en Memoria](#54-búsqueda-semántica-en-memoria)
- [5.5 Limpiar Memoria de Sesión](#55-limpiar-memoria-de-sesión)

### [6. Endpoints de Configuración](#6-endpoints-de-configuración)
- [6.1 Obtener Estado de Configuración](#61-obtener-estado-de-configuración)
- [6.2 Obtener Configuración de Sesión](#62-obtener-configuración-de-sesión)
- [6.3 Actualizar Configuración de Sesión](#63-actualizar-configuración-de-sesión)
- [6.4 Eliminar Configuración de Sesión](#64-eliminar-configuración-de-sesión)
- [6.5 Actualizar Toggles de Memoria](#65-actualizar-toggles-de-memoria)
- [6.6 Actualizar Toggles de RAG](#66-actualizar-toggles-de-rag)

### [7. Endpoints de Sesión](#7-endpoints-de-sesión)
- [7.1 Resetear Sesión Individual](#71-resetear-sesión-individual)
- [7.2 Reset Total del Sistema](#72-reset-total-del-sistema)

### [8. Endpoints MCP](#8-endpoints-mcp)
- [8.1 Listar Herramientas](#81-listar-herramientas)
- [8.2 Obtener Nombres de Herramientas](#82-obtener-nombres-de-herramientas)
- [8.3 Obtener Información de Herramienta](#83-obtener-información-de-herramienta)

---

## 1. Introducción

### 1.1 Configuración

Antes de usar la API, asegúrate de tener las variables de entorno necesarias configuradas.

### 1.2 Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
# OpenAI (Requerido para LLM y Embeddings)
OPENAI_API_KEY=tu-clave-openai

# Pinecone (Requerido para RAG y Memoria Semántica)
PINECONE_API_KEY=tu-clave-pinecone
PINECONE_ENVIRONMENT=tu-environment
PINECONE_INDEX_NAME=tu-index

# Base de Datos (Requerido para Memoria)
# Asegúrate de que tu instancia MySQL esté corriendo
```

**Verificación de Base de Datos:**

```bash
mysql -u root -p -e "SHOW DATABASES;"
```

### 1.3 Iniciar el Servidor

```bash
# Desde la raíz del proyecto
uv run uvicorn agentlab.api.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

### 1.4 Códigos de Estado HTTP

- `200`: Éxito
- `400`: Error de validación o parámetros inválidos
- `404`: Recurso no encontrado (ej: directorio no existe, sesión no encontrada)
- `422`: Error de validación de Pydantic (campos requeridos, tipos incorrectos)
- `500`: Error interno del servidor (ej: fallo en la generación del LLM, error de Pinecone)

---

## 2. Endpoints Base

### 2.1 Health Check

**GET** `/health`

Verifica que el servidor esté funcionando.

**Respuesta:**
```json
{
  "status": "healthy"
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/health"
```

---

### 2.2 Root / Información de API

**GET** `/`

Información sobre la API y sus endpoints disponibles.

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
      "add_directory": "/llm/rag/directory",
      "list_namespaces": "/llm/rag/namespaces",
      "list_documents": "/llm/rag/documents",
      "delete_namespace": "/llm/rag/namespace/{namespace}",
      "namespace_stats": "/llm/rag/namespace/{namespace}/stats"
    },
    "memory": {
      "context": "/llm/memory/context",
      "history": "/llm/memory/history/{session_id}",
      "stats": "/llm/memory/stats/{session_id}",
      "search": "/llm/memory/search",
      "clear": "/llm/memory/session/{session_id}"
    },
    "config": {
      "status": "/config/status",
      "get_session": "/config/session/{session_id}",
      "update_session": "/config/session",
      "delete_session": "/config/session/{session_id}",
      "update_memory": "/config/memory",
      "update_rag": "/config/rag"
    },
    "session": {
      "reset": "/session/reset",
      "reset_all": "/session/reset-all"
    },
    "mpc": {
      "list_tools": "/mpc/tools",
      "tool_names": "/mpc/tools/names",
      "get_tool": "/mpc/tools/{tool_name}"
    }
  }
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/"
```

---

## 3. Endpoints LLM

### 3.1 Generar Texto

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
    "prompt": "Escribe un poema sobre Python",
    "temperature": 0.7
  }'
```

---

### 3.2 Chat

**POST** `/llm/chat`

Genera una respuesta de chat basada en el historial de conversación. Soporta memoria contextual, RAG, y ejecución de herramientas MCP.

**⚠️ ARQUITECTURA IMPORTANTE - Gestión de Mensajes:**

El array `messages` debe contener **ÚNICAMENTE el mensaje actual del usuario**. El backend gestiona automáticamente:
- ✅ **Historial de conversación**: Almacenado y recuperado vía `session_id`
- ✅ **Memoria de corto plazo**: Buffer de mensajes recientes
- ✅ **Memoria de largo plazo**: Hechos semánticos, episodios, perfil, patrones
- ✅ **Contexto RAG**: Documentos relevantes recuperados automáticamente

**Comportamiento con `use_memory`:**
- `use_memory=true`: Backend reconstruye contexto completo desde su sistema de memoria
- `use_memory=false`: Solo se usa el mensaje actual, sin contexto previo

**❌ ERROR COMÚN:** Enviar historial completo en `messages`
```json
// ❌ INCORRECTO - No hagas esto
{
  "messages": [
    {"role": "user", "content": "Hola, mi nombre es Juan"},
    {"role": "assistant", "content": "¡Hola Juan!"},
    {"role": "user", "content": "¿Cómo me llamo?"}  // Historial completo
  ],
  "use_memory": false  // Incluso con memoria desactivada, el LLM ve todo el historial
}
```

**✅ CORRECTO:** Solo enviar mensaje actual
```json
// ✅ CORRECTO - Arquitectura adecuada
{
  "messages": [
    {"role": "user", "content": "¿Cómo me llamo?"}  // Solo mensaje actual
  ],
  "session_id": "mi-sesion-123",  // Backend recupera contexto desde aquí
  "use_memory": true  // Backend decide qué contexto incluir
}
```

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "¿Cuáles son las ventajas de FastAPI?"}
  ],
  "session_id": "mi-sesion-123",
  "temperature": 0.7,
  "max_tokens": 500,
  "use_memory": true,
  "use_rag": false,
  "memory_types": ["semantic", "episodic"],
  "rag_namespaces": ["docs"],
  "rag_top_k": 5,
  "max_context_tokens": 4000,
  "context_priority": "balanced",
  "use_tools": false,
  "tool_choice": "auto",
  "available_tools": null,
  "max_tool_iterations": 5
}
```

**Parámetros Básicos:**
- `messages` (array, requerido): **Array con un solo elemento** - el mensaje actual del usuario
  - Cada mensaje debe tener `role` ("user") y `content` (string)
  - **NO incluir historial completo** - el backend gestiona el contexto vía `session_id`
- `session_id` (string, opcional): ID de sesión para rastrear la conversación y gestionar memoria. Si no se proporciona, se crea uno nuevo automáticamente
- `temperature` (float, opcional): Control de aleatoriedad (0.0 a 1.0). Default: 0.7
- `max_tokens` (int, opcional): Máximo número de tokens a generar. Default: 500

**Parámetros de Contexto:**
- `use_memory` (bool, opcional): Habilitar contexto de memoria. Default: true
- `use_rag` (bool, opcional): Habilitar recuperación RAG. Default: false
- `memory_types` (array[string], opcional): Tipos específicos de memoria a incluir: "semantic", "episodic", "profile", "procedural". Si no se especifica, usa todos.
- `rag_namespaces` (array[string], opcional): Namespaces específicos de Pinecone para buscar. Si no se especifica, busca en todos.
- `rag_top_k` (int, opcional): Número de documentos RAG a recuperar (1-20). Default: 5
- `max_context_tokens` (int, opcional): Máximo de tokens para el contexto combinado (100-8000). Default: 4000
- `context_priority` (string, opcional): Prioridad de contexto: "memory" (priorizar memoria), "rag" (priorizar RAG), o "balanced" (equilibrado). Default: "balanced"

**Parámetros de Herramientas MCP:**
- `use_tools` (bool, opcional): Habilitar ejecución de herramientas MCP. Default: false
- `tool_choice` (string, opcional): Control de selección de herramientas: "auto" (LLM decide), "none" (sin herramientas), o nombre específico de herramienta. Default: "auto"
- `available_tools` (array[string], opcional): Lista de nombres de herramientas específicas a habilitar. Si no se especifica, todas las herramientas registradas están disponibles. Ejemplos: ["get_current_datetime"], ["calculator", "web_search"]
- `max_tool_iterations` (int, opcional): Máximo número de iteraciones del agente con herramientas (1-20). Default: 5

**Respuesta:**
```json
{
  "response": "Las principales ventajas de FastAPI son...",
  "session_id": "mi-sesion-123",
  "context_text": "## Memoria Conversacional\n\n- El usuario preguntó sobre FastAPI...\n\n## Documentos Relevantes (RAG)\n\n...",
  "context_tokens": 1250,
  "rag_sources": [
    {
      "content": "FastAPI es un framework moderno...",
      "metadata": {
        "source": "docs/fastapi.md",
        "namespace": "docs"
      },
      "score": 0.89,
      "chunk_index": 0
    }
  ],
  "tools_used": false,
  "tool_calls": null,
  "tool_results": null,
  "agent_steps": null
}
```

**Campos de Respuesta:**
- `response` (string): La respuesta generada por el LLM
- `session_id` (string): ID de sesión (generado o proporcionado)
- `context_text` (string): Contexto completo enviado al LLM, formateado como texto plano con secciones markdown
- `context_tokens` (int): Número exacto de tokens del contexto (calculado con tiktoken)
- `rag_sources` (array): Lista de documentos RAG utilizados con sus scores de similitud
- `tools_used` (bool): Indica si se utilizaron herramientas en la respuesta
- `tool_calls` (array|null): Lista de llamadas a herramientas realizadas (si `use_tools=true`)
- `tool_results` (array|null): Lista de resultados de ejecución de herramientas (si `use_tools=true`)
- `agent_steps` (array|null): Pasos del agente durante el razonamiento (si `use_tools=true`)

**Ejemplo con curl (básico):**
```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hola"}],
    "session_id": "test-123"
  }'
```

**Ejemplo con memoria + RAG:**
```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "¿Qué es FastAPI?"}],
    "session_id": "test-123",
    "use_memory": true,
    "use_rag": true,
    "rag_namespaces": ["docs"],
    "context_priority": "balanced"
  }'
```

**Ejemplo con herramientas MCP:**
```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "¿Qué hora es?"}],
    "session_id": "test-123",
    "use_tools": true,
    "available_tools": ["get_current_datetime"]
  }'
```

---

## 4. Endpoints RAG

### 4.1 Consultar Base de Conocimiento

**POST** `/llm/rag/query`

Consulta el sistema RAG (Retrieval-Augmented Generation) para obtener respuestas basadas en documentos indexados.

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
  "answer": "FastAPI es un framework web moderno y de alto rendimiento...",
  "sources": [
    {
      "content": "FastAPI es un framework...",
      "metadata": {"source": "docs/intro.md"},
      "score": 0.92
    }
  ],
  "query": "¿Qué es FastAPI?",
  "error_message": null
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué es FastAPI?",
    "top_k": 5,
    "namespace": "docs"
  }'
```

---

### 4.2 Agregar Documentos

**POST** `/llm/rag/documents`

Agrega documentos al sistema RAG. Los documentos pueden ser texto plano o rutas a archivos. Archivos soportados: `.txt`, `.md`, `.log`.

**Request Body:**
```json
{
  "documents": [
    "Este es un texto directo que quiero agregar a RAG.",
    "./docs/manual.md",
    "./data/info.txt"
  ],
  "namespace": "mi-namespace",
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
  "message": "Documents added successfully",
  "documents_added": 3
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/llm/rag/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["./docs/manual.md", "Texto directo a indexar"],
    "namespace": "docs",
    "chunk_size": 1000
  }'
```

---

### 4.3 Agregar Directorio

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
  "message": "Directory processed successfully",
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

---

### 4.4 Listar Namespaces

**GET** `/llm/rag/namespaces`

Lista todos los namespaces disponibles en el sistema RAG con información sobre el número de documentos, chunks y última actualización.

**Respuesta:**
```json
{
  "namespaces": [
    {
      "name": "docs",
      "document_count": 25,
      "chunk_count": 150,
      "last_updated": "2025-12-21T10:30:00.000000"
    },
    {
      "name": "default",
      "document_count": 10,
      "chunk_count": 45,
      "last_updated": "2025-12-20T15:20:00.000000"
    }
  ]
}
```

**Campos de respuesta:**
- `namespaces` (array): Lista de namespaces disponibles
  - `name` (string): Nombre del namespace ("default" para namespace vacío)
  - `document_count` (int): Número de documentos únicos
  - `chunk_count` (int): Número total de chunks/vectores
  - `last_updated` (string): Timestamp ISO de última actualización

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/llm/rag/namespaces"
```

**Casos de uso:**
- Explorar qué namespaces están disponibles
- Verificar el estado de la base de conocimiento
- Interfaz de usuario para seleccionar namespaces

---

### 4.5 Listar Documentos

**GET** `/llm/rag/documents`

Lista todos los documentos en la base de conocimiento con sus metadatos. Soporta filtrado por namespace y paginación.

**Query Parameters:**
- `namespace` (string, opcional): Filtrar por namespace específico. Use "default" para el namespace vacío.
- `limit` (int, opcional): Número máximo de documentos a retornar (1-1000). Default: 100
- `offset` (int, opcional): Número de documentos a saltar para paginación. Default: 0

**URL de ejemplo:**
```
GET /llm/rag/documents?namespace=docs&limit=50&offset=0
```

**Respuesta:**
```json
{
  "documents": [
    {
      "id": "doc-uuid-123",
      "source": "docs/fastapi.md",
      "namespace": "docs",
      "chunk_count": 8,
      "uploaded_at": "2025-12-21T10:30:00.000000"
    },
    {
      "id": "doc-uuid-456",
      "source": "docs/python.md",
      "namespace": "docs",
      "chunk_count": 12,
      "uploaded_at": "2025-12-21T09:15:00.000000"
    }
  ],
  "total_count": 25,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

**Campos de respuesta:**
- `documents` (array): Lista de documentos
  - `id` (string): ID único del documento
  - `source` (string): Ruta o identificador del documento
  - `namespace` (string): Namespace del documento
  - `chunk_count` (int): Número de chunks del documento
  - `uploaded_at` (string): Timestamp ISO de carga
- `total_count` (int): Número total de documentos que coinciden con el filtro
- `limit` (int): Límite aplicado
- `offset` (int): Offset aplicado
- `has_more` (bool): Indica si hay más documentos disponibles

**Ejemplos con curl:**

```bash
# Listar todos los documentos (primera página)
curl "http://localhost:8000/llm/rag/documents?limit=100&offset=0"

# Filtrar por namespace específico
curl "http://localhost:8000/llm/rag/documents?namespace=docs&limit=50"

# Paginación - segunda página
curl "http://localhost:8000/llm/rag/documents?limit=50&offset=50"
```

**Casos de uso:**
- Explorar documentos cargados
- Auditoría de la base de conocimiento
- Implementar búsqueda en el frontend

---

### 4.6 Obtener Estadísticas de Namespace

**GET** `/llm/rag/namespace/{namespace}/stats`

Obtiene estadísticas detalladas de un namespace específico en Pinecone.

**Path Parameters:**
- `namespace` (string, requerido): El namespace a consultar

**URL de ejemplo:**
```
GET /llm/rag/namespace/docs/stats
```

**Respuesta:**
```json
{
  "success": true,
  "namespace": "docs",
  "vector_count": 150,
  "dimension": 1536,
  "exists": true
}
```

**Campos de respuesta:**
- `success` (bool): Indica si la operación fue exitosa
- `namespace` (string): Nombre del namespace consultado
- `vector_count` (int): Número de vectores en el namespace
- `dimension` (int): Dimensión de los vectores
- `exists` (bool): Si el namespace existe en Pinecone

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/llm/rag/namespace/docs/stats"
```

**Casos de uso:**
- Verificar si un namespace existe antes de consultar
- Monitorear el crecimiento de un namespace
- Debugging de operaciones RAG

---

### 4.7 Eliminar Namespace

**DELETE** `/llm/rag/namespace/{namespace}`

Elimina todos los documentos y vectores asociados a un namespace específico en Pinecone.

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

---

## 5. Endpoints de Memoria

### 5.1 Obtener Contexto de Memoria

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
  "context_text": "## Historial Reciente\n\n...\n\n## Hechos Clave\n\n...",
  "token_count": 1850,
  "memory_types_included": ["semantic", "episodic", "profile"],
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

---

### 5.2 Obtener Historial de Conversación

**GET** `/llm/memory/history/{session_id}`

Recupera el historial completo de mensajes de una conversación con timestamps y metadata.

**Path Parameters:**
- `session_id` (string, requerido): ID de la sesión

**Query Parameters:**
- `limit` (int, opcional): Número máximo de mensajes a retornar (1-1000). Default: 50

**URL de ejemplo:**
```
GET /llm/memory/history/mi-sesion-123?limit=50
```

**Respuesta:**
```json
{
  "session_id": "mi-sesion-123",
  "messages": [
    {
      "role": "user",
      "content": "Hola",
      "timestamp": "2025-12-21T10:00:00.000000"
    },
    {
      "role": "assistant",
      "content": "Hola, ¿en qué puedo ayudarte?",
      "timestamp": "2025-12-21T10:00:05.000000"
    }
  ],
  "total_count": 24
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/llm/memory/history/mi-sesion-123?limit=50"
```

---

### 5.3 Obtener Estadísticas de Memoria

**GET** `/llm/memory/stats/{session_id}`

Recupera estadísticas detalladas sobre el uso de memoria para una sesión.

**Path Parameters:**
- `session_id` (string, requerido): ID de la sesión

**URL de ejemplo:**
```
GET /llm/memory/stats/mi-sesion-123
```

**Respuesta:**
```json
{
  "session_id": "mi-sesion-123",
  "short_term": {
    "message_count": 24,
    "token_count": 1200
  },
  "long_term": {
    "semantic_facts": 15,
    "episodic_summaries": 3,
    "profile_entries": 8,
    "procedural_patterns": 2
  }
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/llm/memory/stats/mi-sesion-123"
```

---

### 5.4 Búsqueda Semántica en Memoria

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
      "content": "El usuario preguntó sobre pytest...",
      "metadata": {
        "session_id": "sesion-456",
        "timestamp": "2025-12-20T14:30:00"
      },
      "score": 0.91
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
    "query": "preguntas sobre testing",
    "top_k": 5
  }'
```

**Nota:** Requiere que `PINECONE_API_KEY` esté configurada.

---

### 5.5 Limpiar Memoria de Sesión

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
  "deleted": {
    "messages": 24,
    "semantic_facts": 15,
    "episodic_summaries": 3,
    "profile_entries": 8
  }
}
```

**Ejemplo con curl:**
```bash
curl -X DELETE "http://localhost:8000/llm/memory/session/mi-sesion-123"
```

---

## 6. Endpoints de Configuración

### 6.1 Obtener Estado de Configuración

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
      "provider": "OpenAI",
      "model": "gpt-4"
    },
    "memory": {
      "available": true,
      "storage": "MySQL",
      "semantic_search": true
    },
    "rag": {
      "available": true,
      "vector_db": "Pinecone",
      "embedding_model": "text-embedding-ada-002"
    },
    "mcp": {
      "available": true,
      "registered_tools": 5
    }
  },
  "defaults": {
    "memory": {
      "enabled": true,
      "types": ["semantic", "episodic", "profile", "procedural"]
    },
    "rag": {
      "enabled": false,
      "top_k": 5
    },
    "context": {
      "max_tokens": 4000,
      "priority": "balanced"
    }
  }
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/config/status"
```

---

### 6.2 Obtener Configuración de Sesión

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
    "namespaces": ["docs"],
    "top_k": 5
  },
  "preferences": {
    "context_priority": "balanced",
    "max_context_tokens": 4000
  },
  "created_at": "2025-12-21T10:00:00.000000",
  "updated_at": "2025-12-21T10:30:00.000000"
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/config/session/mi-sesion-123"
```

---

### 6.3 Actualizar Configuración de Sesión

**POST** `/config/session`

Crea o actualiza la configuración de una sesión.

**Request Body:**
```json
{
  "session_id": "mi-sesion-123",
  "memory": {
    "enabled": true,
    "types": ["semantic", "episodic"]
  },
  "rag": {
    "enabled": true,
    "namespaces": ["docs"],
    "top_k": 5
  },
  "preferences": {
    "context_priority": "balanced",
    "max_context_tokens": 4000
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
  "message": "Session configuration updated successfully",
  "config": {
    "memory": {"enabled": true, "types": ["semantic", "episodic"]},
    "rag": {"enabled": true, "namespaces": ["docs"], "top_k": 5}
  }
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/config/session" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "mi-sesion-123",
    "memory": {"enabled": true}
  }'
```

---

### 6.4 Eliminar Configuración de Sesión

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

---

### 6.5 Actualizar Toggles de Memoria

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
    "types": ["semantic", "episodic"]
  }'
```

---

### 6.6 Actualizar Toggles de RAG

**PUT** `/config/rag`

Actualiza la configuración global de RAG o de una sesión específica.

**Request Body:**
```json
{
  "session_id": "mi-sesion-123",
  "enabled": true,
  "namespaces": ["docs"],
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
    "namespaces": ["docs"],
    "top_k": 5
  }
}
```

**Ejemplo con curl:**
```bash
curl -X PUT "http://localhost:8000/config/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "mi-sesion-123",
    "enabled": true,
    "namespaces": ["docs"]
  }'
```

---

## 7. Endpoints de Sesión

### 7.1 Resetear Sesión

**POST** `/session/reset`

**Sin parámetros requeridos**

Borra **TODO** el historial de chat de **TODAS las sesiones** y crea una nueva sesión con configuración por defecto. Preserva la memoria de largo plazo (hechos semánticos, episodios, perfil de usuario, patrones procedimentales) y los documentos RAG.

**⚠️ Comportamiento:** Este endpoint elimina el historial de chat de **todas las sesiones**, no solo la sesión actual. El sistema está diseñado para trabajar con una sesión activa a la vez.

**Request Body:**
No requiere body (envía `{}` o déjalo vacío).

**Respuesta:**
```json
{
  "success": true,
  "new_session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Session reset successfully. Chat history cleared (15 messages)."
}
```

**Campos de respuesta:**
- `success` (bool): Indica si el reset fue exitoso
- `new_session_id` (string): UUID de la nueva sesión generada y persistida en `session_configs`
- `message` (string): Mensaje descriptivo con el número de mensajes eliminados

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/session/reset" \
  -H "Content-Type: application/json"
```

**Casos de Uso:**
- Iniciar una conversación completamente nueva sin historial previo
- Limpiar el contexto conversacional sin afectar documentos RAG
- El frontend lo usa en la inicialización de la app

**Qué se elimina:**
- ✅ Todo el historial de mensajes de chat (todas las sesiones)

**Qué se preserva:**
- ✅ Memoria de largo plazo (semántica, episódica, perfil, procedural)
- ✅ Documentos RAG y vectores en Pinecone
- ✅ Configuración de sesión (se crea nueva con defaults)

**Diferencia con `/session/reset-all`:**
- `/session/reset`: Solo elimina historial de chat
- `/session/reset-all`: Elimina TODO (chat, memoria, RAG, configuraciones)

---

### 7.2 Reset Total del Sistema

**POST** `/session/reset-all`

Opción nuclear: Elimina TODOS los datos del sistema de forma permanente e irreversible.

**⚠️ ADVERTENCIA:** Esta operación elimina:
- Todo el historial de conversaciones (todas las sesiones)
- Toda la memoria de largo plazo (semántica, episódica, perfil, procedimental)
- Todos los documentos y vectores RAG
- Todas las configuraciones de sesión

**Request Body:**
```json
{
  "confirmation": "DELETE"
}
```

**Parámetros:**
- `confirmation` (string, requerido): Debe ser exactamente "DELETE" (case-sensitive) para confirmar la operación.

**Respuesta:**
```json
{
  "success": true,
  "message": "System reset completed successfully",
  "deleted": {
    "sessions": 5,
    "messages": 150,
    "memory_entries": 85,
    "rag_documents": 42,
    "vector_count": 320
  }
}
```

**Campos de respuesta:**
- `success` (bool): Indica si la operación fue exitosa
- `message` (string): Mensaje descriptivo
- `deleted` (object): Contadores de elementos eliminados
  - `sessions` (int): Número de sesiones únicas eliminadas
  - `messages` (int): Número de mensajes de chat eliminados
  - `memory_entries` (int): Entradas de memoria de largo plazo eliminadas
  - `rag_documents` (int): Documentos RAG eliminados
  - `vector_count` (int): Número de vectores eliminados de Pinecone

**Errores:**

**400 - Confirmación inválida:**
```json
{
  "detail": "Invalid confirmation. Must be exactly 'DELETE' to proceed."
}
```

**500 - Error del servidor:**
```json
{
  "detail": "Failed to reset system: [error details]"
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/session/reset-all" \
  -H "Content-Type: application/json" \
  -d '{
    "confirmation": "DELETE"
  }'
```

**⚠️ CONSIDERACIONES IMPORTANTES:**

1. **Esta operación es IRREVERSIBLE**: No hay forma de recuperar los datos una vez eliminados.

2. **Requiere confirmación exacta**: El string "DELETE" debe ser exacto (case-sensitive).

3. **Funciona sin Pinecone**: Si Pinecone no está configurado, el endpoint seguirá funcionando pero `vector_count` será 0.

4. **Errores parciales**: Si alguna parte de la eliminación falla (por ejemplo, Pinecone), la operación continúa con las otras partes. Revisa los logs del servidor para detalles.

5. **No afecta configuración**: Las variables de entorno (`.env`) y la estructura de la base de datos (tablas) NO se eliminan.

**Casos de uso legítimos:**
- Testing y desarrollo local
- Limpiar datos de prueba
- Restaurar sistema a estado inicial
- Preparación para demo

**NO usar en producción a menos que**:
- Tengas backups completos
- Entiendas completamente las consecuencias
- Tengas autorización explícita

---

## 8. Endpoints MCP

### 8.1 Listar Herramientas

**GET** `/mpc/tools`

Obtiene la lista completa de herramientas MCP registradas con sus descripciones y esquemas de entrada.

**Respuesta:**
```json
{
  "tools": [
    {
      "name": "get_current_datetime",
      "description": "Get the current date and time",
      "input_schema": {
        "type": "object",
        "properties": {
          "timezone": {
            "type": "string",
            "description": "Timezone name (e.g., 'America/New_York')"
          }
        }
      }
    },
    {
      "name": "calculator",
      "description": "Perform mathematical calculations",
      "input_schema": {
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
  ],
  "count": 2
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/mpc/tools"
```

---

### 8.2 Obtener Nombres de Herramientas

**GET** `/mpc/tools/names`

Obtiene solo los nombres de las herramientas MCP registradas. Útil para construir listas de selección.

**Respuesta:**
```json
{
  "tool_names": [
    "get_current_datetime",
    "calculator",
    "web_search",
    "file_reader",
    "weather_api"
  ],
  "count": 5
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/mpc/tools/names"
```

---

### 8.3 Obtener Información de Herramienta

**GET** `/mpc/tools/{tool_name}`

Obtiene información detallada de una herramienta MCP específica.

**Path Parameters:**
- `tool_name` (string, requerido): Nombre de la herramienta

**URL de ejemplo:**
```
GET /mpc/tools/get_current_datetime
```

**Respuesta:**
```json
{
  "name": "get_current_datetime",
  "description": "Get the current date and time in a specified timezone",
  "input_schema": {
    "type": "object",
    "properties": {
      "timezone": {
        "type": "string",
        "description": "Timezone name (e.g., 'America/New_York'). Defaults to UTC.",
        "default": "UTC"
      }
    }
  },
  "examples": [
    {
      "input": {"timezone": "America/New_York"},
      "output": "2025-12-21 10:30:00 EST"
    }
  ]
}
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/mpc/tools/get_current_datetime"
```

---

## Apéndice A: Ejemplos Completos

### Ejemplo 1: Chat Básico sin Contexto

```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hola, ¿cómo estás?"}
    ],
    "use_memory": false,
    "use_rag": false
  }'
```

### Ejemplo 2: Chat con Memoria

```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "¿De qué hablamos anteriormente?"}
    ],
    "session_id": "mi-sesion-123",
    "use_memory": true,
    "memory_types": ["semantic", "episodic"]
  }'
```

### Ejemplo 3: Chat con RAG

```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "¿Qué dice la documentación sobre FastAPI?"}
    ],
    "use_rag": true,
    "rag_namespaces": ["docs"],
    "rag_top_k": 5
  }'
```

### Ejemplo 4: Chat con Herramientas MCP

```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "¿Qué hora es en Nueva York?"}
    ],
    "use_tools": true,
    "available_tools": ["get_current_datetime"]
  }'
```

### Ejemplo 5: Chat Completo (Memoria + RAG + Herramientas)

```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Usando la documentación y lo que sabes de mí, calcula cuánto tiempo llevo programando"}
    ],
    "session_id": "mi-sesion-123",
    "use_memory": true,
    "use_rag": true,
    "use_tools": true,
    "rag_namespaces": ["docs"],
    "available_tools": ["calculator", "get_current_datetime"],
    "context_priority": "balanced"
  }'
```

---

## Apéndice B: Flujo de Trabajo Típico

### 1. Configuración Inicial

```bash
# 1. Verificar estado del sistema
curl "http://localhost:8000/config/status"

# 2. Agregar documentos RAG
curl -X POST "http://localhost:8000/llm/rag/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory": "./docs", "namespace": "docs"}'

# 3. Verificar documentos cargados
curl "http://localhost:8000/llm/rag/namespaces"
```

### 2. Conversación con Contexto

```bash
# 4. Primera interacción (crear sesión)
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hola, soy Juan y me gusta Python"}],
    "session_id": "juan-session-1",
    "use_memory": true
  }'

# 5. Segunda interacción (con memoria)
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "¿Cuál es mi lenguaje favorito?"}],
    "session_id": "juan-session-1",
    "use_memory": true
  }'

# 6. Consulta con RAG
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "¿Qué dice la documentación sobre FastAPI?"}],
    "session_id": "juan-session-1",
    "use_memory": true,
    "use_rag": true,
    "rag_namespaces": ["docs"]
  }'
```

### 3. Monitoreo y Gestión

```bash
# 7. Ver estadísticas de memoria
curl "http://localhost:8000/llm/memory/stats/juan-session-1"

# 8. Ver historial completo
curl "http://localhost:8000/llm/memory/history/juan-session-1?limit=100"

# 9. Resetear sesión (mantener memoria largo plazo)
curl -X POST "http://localhost:8000/session/reset" \
  -H "Content-Type: application/json" \
  -d '{"current_session_id": "juan-session-1"}'
```

---

## Apéndice C: Mejores Prácticas

### 1. Gestión de Sesiones

- **Usa IDs de sesión únicos** por usuario/conversación
- **Resetea sesiones** cuando empiece un nuevo contexto conversacional
- **Limpia sesiones antiguas** periódicamente para optimizar la base de datos

### 2. Optimización de RAG

- **Organiza documentos por namespace** según tema/proyecto
- **Usa chunk_size apropiado**: 500-1000 para textos técnicos, 1000-2000 para narrativos
- **Ajusta top_k según necesidad**: 3-5 para respuestas precisas, 10-15 para exploración amplia

### 3. Configuración de Memoria

- **Habilita tipos específicos** según el caso de uso:
  - `semantic`: Para hechos y conocimiento
  - `episodic`: Para resumen de conversaciones largas
  - `profile`: Para información del usuario
  - `procedural`: Para patrones y workflows
  
### 4. Uso de Herramientas MCP

- **Especifica available_tools** para limitar el alcance y reducir confusión
- **Ajusta max_tool_iterations** según complejidad: 3-5 para tareas simples, 10-15 para complejas
- **Usa tool_choice="none"** cuando no quieras que el LLM use herramientas

### 5. Control de Tokens

- **Ajusta max_context_tokens** según tu modelo:
  - GPT-3.5: 4000-8000
  - GPT-4: 8000-16000
  - Claude: 16000-32000
  
- **Usa context_priority** estratégicamente:
  - `"memory"`: Para conversaciones personales
  - `"rag"`: Para Q&A basado en documentos
  - `"balanced"`: Para uso general

---

## Apéndice D: Troubleshooting

### Error 500: Pinecone Connection Failed

**Causa:** API key de Pinecone inválida o index no existe

**Solución:**
```bash
# Verificar variables de entorno
echo $PINECONE_API_KEY
echo $PINECONE_INDEX_NAME

# Verificar en .env
cat .env | grep PINECONE
```

### Error 422: Validation Error

**Causa:** Parámetros inválidos o faltantes

**Solución:**
- Verifica que `messages` sea un array con objetos `{role, content}`
- Verifica que los tipos de datos coincidan (int, string, bool)
- Revisa la documentación del endpoint específico

### Error 404: Session Not Found

**Causa:** Sesión no existe o fue eliminada

**Solución:**
- Crea una nueva sesión con el endpoint `/llm/chat`
- Verifica el session_id es correcto
- Usa `/llm/memory/history/{session_id}` para verificar existencia

### RAG no retorna resultados relevantes

**Causa:** Documentos no indexados o query muy específica

**Solución:**
- Verifica documentos cargados: `GET /llm/rag/documents`
- Aumenta `rag_top_k` para explorar más resultados
- Reformula la query con términos más generales
- Verifica el namespace correcto

### Memoria no recuerda conversaciones previas

**Causa:** `use_memory=false` o sesión diferente

**Solución:**
- Asegúrate de usar `use_memory=true`
- Verifica que usas el mismo `session_id`
- Revisa estadísticas: `GET /llm/memory/stats/{session_id}`

---

**Fin de la documentación - Agent Lab API v1.0**
