# LangChainLLM Implementation

## Descripción

Implementación de interfaz LLM usando LangChain para interactuar con modelos de OpenAI (GPT-3.5, GPT-4, etc.).

## Características

- ✅ Generación de texto simple
- ✅ Conversaciones de chat con historial
- ✅ Parámetros configurables (temperature, max_tokens)
- ✅ Soporte para múltiples roles (user, assistant, system)
- ✅ Manejo robusto de errores

## Instalación

Las dependencias ya están incluidas en el proyecto:

```bash
uv sync
```

## Configuración

Configure su API key de OpenAI:

```bash
# Linux/Mac
export OPENAI_API_KEY="tu-api-key-aquí"

# Windows (CMD)
set OPENAI_API_KEY=tu-api-key-aquí

# Windows (PowerShell)
$env:OPENAI_API_KEY="tu-api-key-aquí"
```

O use un archivo `.env`:

```
OPENAI_API_KEY=tu-api-key-aquí
```

## Uso Básico

### 1. Generación de Texto Simple

```python
from agentlab.core.llm_interface import LangChainLLM

# Inicializar el LLM
llm = LangChainLLM(model_name="gpt-3.5-turbo")

# Generar texto
response = llm.generate(
    prompt="Explica qué es machine learning",
    temperature=0.7,
    max_tokens=500
)

print(response)
```

### 2. Chat con Historial

```python
from datetime import datetime
from agentlab.core.llm_interface import LangChainLLM
from agentlab.models import ChatMessage

# Inicializar el LLM
llm = LangChainLLM(model_name="gpt-3.5-turbo")

# Crear historial de conversación
messages = [
    ChatMessage(
        role="system",
        content="Eres un asistente útil y amigable.",
        timestamp=datetime.now()
    ),
    ChatMessage(
        role="user",
        content="¿Cuál es la capital de Francia?",
        timestamp=datetime.now()
    ),
    ChatMessage(
        role="assistant",
        content="La capital de Francia es París.",
        timestamp=datetime.now()
    ),
    ChatMessage(
        role="user",
        content="¿Y cuál es su población?",
        timestamp=datetime.now()
    ),
]

# Generar respuesta
response = llm.chat(messages)
print(response)
```

### 3. Usando GPT-4

```python
# Usar GPT-4 en lugar de GPT-3.5
llm = LangChainLLM(model_name="gpt-4")

response = llm.generate("Escribe un poema corto sobre Python")
print(response)
```

### 4. Parámetros Personalizados

```python
# Temperatura baja para respuestas más determinísticas
response = llm.generate(
    prompt="Lista 5 lenguajes de programación",
    temperature=0.2,  # Más determinístico
    max_tokens=100
)

# Temperatura alta para respuestas más creativas
response = llm.generate(
    prompt="Inventa un nombre para una startup de IA",
    temperature=0.9,  # Más creativo
    max_tokens=50
)
```

## API Reference

### `LangChainLLM`

#### Constructor

```python
LangChainLLM(model_name: str = "gpt-3.5-turbo", api_key: str | None = None)
```

**Parámetros:**
- `model_name`: Nombre del modelo a usar (ej: "gpt-3.5-turbo", "gpt-4")
- `api_key`: API key de OpenAI (opcional, usa variable de entorno por defecto)

**Raises:**
- `ValueError`: Si no se proporciona API key

#### `generate()`

```python
generate(prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str
```

Genera texto a partir de un prompt.

**Parámetros:**
- `prompt`: Texto de entrada para el modelo
- `temperature`: Temperatura de muestreo (0.0 - 1.0)
- `max_tokens`: Máximo de tokens a generar

**Returns:** Texto generado por el modelo

**Raises:**
- `ValueError`: Si el prompt está vacío
- `RuntimeError`: Si la generación falla

#### `chat()`

```python
chat(messages: list[ChatMessage]) -> str
```

Genera una respuesta de chat basada en el historial de conversación.

**Parámetros:**
- `messages`: Lista de objetos `ChatMessage` con el historial

**Returns:** Respuesta generada por el asistente

**Raises:**
- `ValueError`: Si la lista de mensajes está vacía
- `RuntimeError`: Si la generación falla

## Testing

Ejecutar tests unitarios:

```bash
uv run pytest tests/unit/test_llm_interface.py -v
```

## Ejemplo Completo

Ejecutar el script de ejemplo:

```bash
uv run python -m agentlab.examples.llm_example
```

## Notas Importantes

1. **API Key**: Asegúrese de configurar `OPENAI_API_KEY` antes de usar
2. **Costos**: Las llamadas a la API de OpenAI tienen costo
3. **Rate Limits**: OpenAI tiene límites de tasa según su plan
4. **Modelos**: Diferentes modelos tienen diferentes capacidades y costos

## Manejo de Errores

```python
try:
    llm = LangChainLLM()
    response = llm.generate("Tu prompt aquí")
except ValueError as e:
    print(f"Error de configuración: {e}")
except RuntimeError as e:
    print(f"Error de generación: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
```

## Mejores Prácticas

1. **Temperature**:
   - 0.0 - 0.3: Respuestas determinísticas y consistentes
   - 0.4 - 0.7: Balance entre creatividad y consistencia
   - 0.8 - 1.0: Respuestas creativas y variadas

2. **Max Tokens**:
   - Ajuste según sus necesidades
   - Recuerde que afecta el costo

3. **System Messages**:
   - Use mensajes de sistema para establecer el comportamiento del asistente
   - Colóquelos al inicio de la conversación

4. **Context Window**:
   - GPT-3.5-turbo: ~4K tokens
   - GPT-4: ~8K - 32K tokens (según variante)
   - Gestione el historial para no exceder límites

## Troubleshooting

### Error: "OpenAI API key is required"
**Solución**: Configure la variable de entorno `OPENAI_API_KEY`

### Error: Rate limit exceeded
**Solución**: Espere antes de hacer más requests o actualice su plan de OpenAI

### Error: Invalid API key
**Solución**: Verifique que su API key sea correcta y activa

## Arquitectura

La implementación sigue principios SOLID:

- **Single Responsibility**: Cada método tiene una responsabilidad clara
- **Dependency Inversion**: Usa abstracciones (Protocol) en lugar de implementaciones concretas
- **Interface Segregation**: Métodos específicos para diferentes operaciones

## Próximas Mejoras

- [ ] Soporte para streaming de respuestas
- [ ] Integración con más proveedores (Anthropic, Cohere)
- [ ] Cache de respuestas
- [ ] Métricas y logging
- [ ] Retry automático en caso de errores transitorios
