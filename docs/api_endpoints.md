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
    "generate": "/api/llm/generate",
    "chat": "/api/llm/chat",
    "health": "/health",
    "docs": "/docs"
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
  "session_id": "opcional-id-de-sesion"
}
```

**Parámetros:**
- `messages` (array, requerido): Lista de mensajes de la conversación
  - Cada mensaje debe tener:
    - `role`: "user", "assistant", o "system"
    - `content`: El contenido del mensaje
- `session_id` (string, opcional): ID de sesión para rastrear la conversación

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
      {"role": "user", "content": "Hola, ¿cómo estás?"}
    ]
  }'
```

## Códigos de Estado HTTP

- `200`: Éxito
- `400`: Error de validación o parámetros inválidos
- `422`: Error de validación de Pydantic
- `500`: Error interno del servidor (ej: fallo en la generación del LLM)

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
