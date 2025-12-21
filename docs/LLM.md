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

### 1. Inicialización con Parámetros por Defecto

```python
from agentlab.core.llm_interface import LangChainLLM

# Inicializar con parámetros por defecto
llm = LangChainLLM(
    model_name="gpt-3.5-turbo",
    temperature=0.7,      # Temperatura por defecto para esta instancia
    max_tokens=1000       # Tokens máximos por defecto para esta instancia
)

# Generar texto usando los valores por defecto de la instancia
response = llm.generate(prompt="Explica qué es machine learning")
print(response)
```

### 2. Generación de Texto con Override de Parámetros

```python
from agentlab.core.llm_interface import LangChainLLM

# Inicializar el LLM con defaults
llm = LangChainLLM(model_name="gpt-3.5-turbo")

# Generar texto con parámetros personalizados (sobrescriben los defaults)
response = llm.generate(
    prompt="Explica qué es machine learning",
    temperature=0.7,
    max_tokens=500
)

print(response)
```

### 3. Chat con Historial

```python
from datetime import datetime
from agentlab.core.llm_interface import LangChainLLM
from agentlab.models import ChatMessage

# Inicializar el LLM con configuración para respuestas concisas
llm = LangChainLLM(
    model_name="gpt-3.5-turbo",
    temperature=0.5,
    max_tokens=300
)

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

# Generar respuesta usando los defaults de la instancia
response = llm.chat(messages)
print(response)
```

### 4. Chat con Override de Parámetros

```python
from datetime import datetime
from agentlab.core.llm_interface import LangChainLLM
from agentlab.models import ChatMessage

# Inicializar con defaults
llm = LangChainLLM(model_name="gpt-3.5-turbo")

messages = [
    ChatMessage(
        role="system",
        content="Eres un asistente técnico conciso.",
        timestamp=datetime.now()
    ),
    ChatMessage(
        role="user",
        content="Explica los principios SOLID.",
        timestamp=datetime.now()
    ),
]

# Generar respuesta con parámetros personalizados
response = llm.chat(
    messages,
    temperature=0.3,  # Más determinístico
    max_tokens=200    # Respuesta concisa
)
print(response)
```

### 5. Usando GPT-4

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
LangChainLLM(
    model_name: str = "gpt-3.5-turbo",
    api_key: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1000
)
```

**Parámetros:**
- `model_name`: Nombre del modelo a usar (ej: "gpt-3.5-turbo", "gpt-4")
- `api_key`: API key de OpenAI (opcional, usa variable de entorno por defecto)
- `temperature`: Temperatura por defecto para esta instancia (0.0 - 1.0)
- `max_tokens`: Máximo de tokens por defecto para esta instancia (1 - 4000)

**Raises:**
- `ValueError`: Si no se proporciona API key o parámetros están fuera de rango

**Ejemplo:**
```python
# Instancia con valores por defecto
llm = LangChainLLM()

# Instancia con parámetros personalizados
llm = LangChainLLM(
    model_name="gpt-4",
    temperature=0.5,
    max_tokens=500
)
```

#### `generate()`

```python
generate(
    prompt: str,
    temperature: float | None = None,
    max_tokens: int | None = None
) -> str
```

Genera texto a partir de un prompt.

**Parámetros:**
- `prompt`: Texto de entrada para el modelo
- `temperature`: Temperatura de muestreo (0.0 - 1.0). Si no se proporciona, usa el valor de la instancia
- `max_tokens`: Máximo de tokens a generar. Si no se proporciona, usa el valor de la instancia

**Returns:** Texto generado por el modelo

**Raises:**
- `ValueError`: Si el prompt está vacío o parámetros están fuera de rango
- `RuntimeError`: Si la generación falla

**Ejemplo:**
```python
# Usar defaults de la instancia
response = llm.generate("¿Qué es Python?")

# Override de parámetros
response = llm.generate("¿Qué es Python?", temperature=0.2, max_tokens=100)
```

#### `chat()`

```python
chat(
    messages: list[ChatMessage],
    temperature: float | None = None,
    max_tokens: int | None = None
) -> str
```

Genera una respuesta de chat basada en el historial de conversación.

**Parámetros:**
- `messages`: Lista de objetos `ChatMessage` con el historial
- `temperature`: Temperatura de muestreo (0.0 - 1.0). Si no se proporciona, usa el valor de la instancia
- `max_tokens`: Máximo de tokens a generar. Si no se proporciona, usa el valor de la instancia

**Returns:** Respuesta generada por el asistente

**Raises:**
- `ValueError`: Si la lista de mensajes está vacía o parámetros están fuera de rango
- `RuntimeError`: Si la generación falla

**Ejemplo:**
```python
# Usar defaults de la instancia
response = llm.chat(messages)

# Override de parámetros
response = llm.chat(messages, temperature=0.3, max_tokens=200)
```

#### `chat_with_tools()`

```python
async chat_with_tools(
    messages: list[ChatMessage],
    tools: list[Any],
    temperature: float | None = None,
    max_tokens: int | None = None,
    max_iterations: int = 5,
) -> tuple[str, list[AgentStep], list[ToolResult]]
```

Genera una respuesta de chat con capacidad de llamar herramientas MCP usando un patrón ReAct agent.

**Parámetros:**
- `messages`: Lista de objetos `ChatMessage` con el historial
- `tools`: Lista de herramientas LangChain disponibles para el LLM
- `temperature`: Temperatura de muestreo (0.0 - 1.0). Si no se proporciona, usa el valor de la instancia
- `max_tokens`: Máximo de tokens a generar. Si no se proporciona, usa el valor de la instancia
- `max_iterations`: Máximo número de iteraciones del agente (default: 5)

**Returns:** Tupla de (respuesta_final, pasos_del_agente, resultados_de_herramientas)
- `respuesta_final` (str): Respuesta final generada después de usar herramientas
- `pasos_del_agente` (list[AgentStep]): Lista de pasos de razonamiento del agente
- `resultados_de_herramientas` (list[ToolResult]): Lista de resultados de ejecución de herramientas

**Raises:**
- `ValueError`: Si los mensajes están vacíos o no hay herramientas disponibles
- `RuntimeError`: Si la generación falla

**Ejemplo:**
```python
from agentlab.mcp import get_registry

# Obtener herramientas
registry = get_registry()
langchain_tools = registry.get_langchain_tools()

# Chat con herramientas
response, agent_steps, tool_results = await llm.chat_with_tools(
    messages=messages,
    tools=langchain_tools,
    max_iterations=5
)

print(f"Respuesta: {response}")
print(f"Herramientas usadas: {len(tool_results)}")
for step in agent_steps:
    print(f"Paso {step.step_number}: {step.tool_name}")
```

**Flujo del Agente:**
1. El LLM recibe el historial de conversación con herramientas vinculadas
2. Si el LLM decide usar una herramienta, genera un `tool_call`
3. La herramienta se ejecuta a través del `MCPToolRegistry`
4. El resultado se añade al historial como `ToolMessage`
5. El LLM continúa hasta dar una respuesta final o alcanzar `max_iterations`

**Notas:**
- El método es asíncrono (usa `async`/`await`)
- Las herramientas deben estar registradas en el `MCPToolRegistry`
- Los resultados incluyen timestamps y metadata para tracking
- El agente se detiene automáticamente si el LLM da una respuesta sin herramientas

## Testing

Ejecutar tests unitarios:

```bash
uv run pytest tests/unit/test_llm_interface.py -v

# Tests específicos de herramientas
uv run pytest tests/unit/test_llm_with_tools.py -v
```

Ejecutar tests de integración (requiere `OPENAI_API_KEY`):

```bash
uv run pytest tests/integration/test_chat_tools_integration.py -v
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
