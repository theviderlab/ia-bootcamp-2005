# Guía de Validación: API Updates

Esta guía te ayudará a validar todos los cambios realizados en la API, documentación y tests.

## 🚀 Pre-requisitos

Antes de comenzar, asegúrate de tener:

```bash
# 1. Variables de entorno configuradas
export OPENAI_API_KEY="tu-clave-openai"
export PINECONE_API_KEY="tu-clave-pinecone"
export PINECONE_ENVIRONMENT="tu-environment"
export PINECONE_INDEX_NAME="tu-index"

# O crear archivo .env en la raíz del proyecto
cat > .env << EOF
OPENAI_API_KEY=tu-clave-openai
PINECONE_API_KEY=tu-clave-pinecone
PINECONE_ENVIRONMENT=tu-environment
PINECONE_INDEX_NAME=tu-index
EOF

# 2. Dependencias instaladas
uv sync

# 3. Base de datos MySQL corriendo
# Verifica con: mysql -u root -p -e "SHOW DATABASES;"
```

## ✅ Paso 1: Validar el Código

### 1.1 Verificar que no hay errores de sintaxis

```bash
# Formatear código
make format

# Verificar linting
make lint

# Debería mostrar: "All checks passed!"
```

### 1.2 Ejecutar tests unitarios

```bash
# Tests unitarios
make test-unit

# Debería pasar todos los tests sin errores
```

### 1.3 Iniciar el servidor

```bash
# Iniciar servidor en modo desarrollo
uv run uvicorn agentlab.api.main:app --reload

# Debería mostrar:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

En otra terminal, verifica que el servidor responde:

```bash
# Health check
curl http://localhost:8000/health

# Debería retornar: {"status":"healthy"}

# Verificar endpoint raíz actualizado
curl http://localhost:8000/ | jq

# Debería mostrar estructura con memory y config endpoints
```

## ✅ Paso 2: Validar Nuevos Endpoints

### 2.1 Verificar endpoint DELETE namespace

```bash
# Crear un namespace de test
curl -X POST "http://localhost:8000/llm/rag/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["Test document for deletion"],
    "namespace": "delete-test"
  }'

# Eliminar el namespace
curl -X DELETE "http://localhost:8000/llm/rag/namespace/delete-test"

# Debería retornar:
# {
#   "success": true,
#   "namespace": "delete-test",
#   "message": "Namespace 'delete-test' deleted successfully"
# }
```

### 2.2 Verificar endpoints de configuración

```bash
# 1. Obtener status del sistema
curl http://localhost:8000/config/status | jq

# 2. Crear configuración de sesión
curl -X POST "http://localhost:8000/config/session" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-validation-session",
    "memory": {"enabled": true, "types": ["semantic"]},
    "rag": {"enabled": false}
  }' | jq

# 3. Obtener configuración de sesión
curl "http://localhost:8000/config/session/test-validation-session" | jq

# 4. Actualizar memory toggles
curl -X PUT "http://localhost:8000/config/memory" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "types": ["semantic", "episodic"]
  }' | jq

# 5. Actualizar RAG toggles
curl -X PUT "http://localhost:8000/config/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "namespaces": ["docs"],
    "top_k": 3
  }' | jq

# 6. Eliminar configuración de sesión
curl -X DELETE "http://localhost:8000/config/session/test-validation-session" | jq
```

### 2.3 Verificar endpoints de memoria

```bash
# Crear una conversación de test
SESSION_ID="memory-validation-$(date +%s)"

curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"messages\": [{\"role\": \"user\", \"content\": \"Hello, test message\"}],
    \"session_id\": \"$SESSION_ID\"
  }" | jq

# 1. Obtener contexto de memoria
curl -X POST "http://localhost:8000/llm/memory/context" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"max_tokens\": 2000
  }" | jq

# 2. Obtener historial
curl "http://localhost:8000/llm/memory/history?session_id=$SESSION_ID&limit=10" | jq

# 3. Obtener estadísticas
curl "http://localhost:8000/llm/memory/stats?session_id=$SESSION_ID" | jq

# 4. Búsqueda semántica (requiere Pinecone)
curl -X POST "http://localhost:8000/llm/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test message",
    "top_k": 3
  }' | jq

# 5. Limpiar sesión
curl -X DELETE "http://localhost:8000/llm/memory/session/$SESSION_ID" | jq
```

## ✅ Paso 3: Ejecutar Tests de Postman

### 3.1 Instalar Newman (si no está instalado)

```bash
npm install -g newman
```

### 3.2 Ejecutar colección principal

```bash
cd tests/api/postman/collections

# Ejecutar todos los tests
newman run Agent_Lab_API.postman_collection.json \
  --env-var "base_url=http://localhost:8000" \
  --env-var "test_namespace=postman-test-$(date +%s)"

# Debería mostrar:
# ✓ All tests passed
# Tests: 51 passed
```

### 3.3 Ejecutar colección de configuración

```bash
# Ejecutar tests de configuración
newman run Configuration_Management_Tests.postman_collection.json \
  --env-var "base_url=http://localhost:8000"

# Debería mostrar:
# ✓ All tests passed
# Tests: 16 passed
```

### 3.4 Generar reporte HTML (opcional)

```bash
# Instalar reporter
npm install -g newman-reporter-htmlextra

# Generar reporte
newman run Agent_Lab_API.postman_collection.json \
  --env-var "base_url=http://localhost:8000" \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export test-report.html

# Abrir reporte
# Windows: start test-report.html
# Linux: xdg-open test-report.html
# macOS: open test-report.html
```

## ✅ Paso 4: Validar Documentación

### 4.1 Verificar documentación actualizada

Abre `docs/api_endpoints.md` y verifica que contiene:

- ✅ Sección 4: Chat con 7 parámetros avanzados
- ✅ Sección 7bis: Eliminar Namespace RAG
- ✅ Sección 8: Gestión de Memoria (5 endpoints)
- ✅ Sección 9: Gestión de Configuración (6 endpoints)
- ✅ Sección "Formatos de Respuesta de Error"
- ✅ Endpoint raíz con estructura memory/config

### 4.2 Verificar que ejemplos funcionan

Copia y ejecuta algunos ejemplos de la documentación:

```bash
# Ejemplo de la sección Memory Operations
curl -X POST "http://localhost:8000/llm/memory/context" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "mi-sesion-123",
    "max_tokens": 2000
  }'

# Ejemplo de la sección Configuration Management
curl "http://localhost:8000/config/status"
```

### 4.3 Verificar Swagger UI

Abre en el navegador:
```
http://localhost:8000/docs
```

Verifica que aparecen todos los endpoints:
- ✅ /llm/memory/context (POST)
- ✅ /llm/memory/history (GET)
- ✅ /llm/memory/stats (GET)
- ✅ /llm/memory/search (POST)
- ✅ /llm/memory/session/{session_id} (DELETE)
- ✅ /config/status (GET)
- ✅ /config/session (POST)
- ✅ /config/session/{session_id} (GET, DELETE)
- ✅ /config/memory (PUT)
- ✅ /config/rag (PUT)
- ✅ /llm/rag/namespace/{namespace} (DELETE)

## ✅ Paso 5: Checklist Final

Marca cada item después de validarlo:

### Código
- [ ] `make format` ejecuta sin errores
- [ ] `make lint` ejecuta sin errores
- [ ] `make test-unit` todos los tests pasan
- [ ] Servidor inicia correctamente
- [ ] `/health` retorna `{"status":"healthy"}`
- [ ] Endpoint raíz retorna estructura con memory/config

### Endpoints Nuevos
- [ ] `DELETE /llm/rag/namespace/{namespace}` funciona
- [ ] `POST /llm/memory/context` funciona
- [ ] `GET /llm/memory/history` funciona
- [ ] `GET /llm/memory/stats` funciona
- [ ] `POST /llm/memory/search` funciona
- [ ] `DELETE /llm/memory/session/{session_id}` funciona
- [ ] `GET /config/status` funciona
- [ ] `GET /config/session/{session_id}` funciona
- [ ] `POST /config/session` funciona
- [ ] `DELETE /config/session/{session_id}` funciona
- [ ] `PUT /config/memory` funciona
- [ ] `PUT /config/rag` funciona

### Tests
- [ ] Newman instalado correctamente
- [ ] Colección principal ejecuta sin errores
- [ ] Colección de configuración ejecuta sin errores
- [ ] Tests: 51 passed (colección principal)
- [ ] Tests: 16 passed (colección configuración)

### Documentación
- [ ] `api_endpoints.md` contiene sección Memory Operations
- [ ] `api_endpoints.md` contiene sección Configuration Management
- [ ] `api_endpoints.md` contiene parámetros avanzados de chat
- [ ] `api_endpoints.md` contiene formatos de error
- [ ] Swagger UI muestra todos los endpoints
- [ ] Ejemplos de documentación funcionan

## 🎉 Validación Completa

Si todos los checkboxes están marcados, la actualización fue exitosa!

## 🐛 Troubleshooting

### Error: "Failed to initialize RAG service"
**Solución:** Verifica que `PINECONE_API_KEY` está configurada y que el índice existe.

```bash
# Verificar variables
echo $PINECONE_API_KEY
echo $PINECONE_INDEX_NAME

# Recrear índice si es necesario
# (código Python para crear índice)
```

### Error: "Database connection failed"
**Solución:** Verifica que MySQL está corriendo y las credenciales son correctas.

```bash
# Verificar MySQL
mysql -u root -p -e "SHOW DATABASES;"

# Verificar variables de DB en .env
cat .env | grep DB
```

### Error: Tests fallan en Newman
**Solución:** Asegúrate que el servidor está corriendo antes de ejecutar Newman.

```bash
# Terminal 1: Iniciar servidor
uv run uvicorn agentlab.api.main:app --reload

# Terminal 2: Ejecutar tests
newman run Agent_Lab_API.postman_collection.json \
  --env-var "base_url=http://localhost:8000"
```

### Error: "Module not found"
**Solución:** Reinstalar dependencias.

```bash
# Limpiar y reinstalar
rm -rf .venv
uv sync
```

## 📚 Documentos de Referencia

- [API Update Summary](./API_UPDATE_SUMMARY.md) - Resumen completo de cambios
- [API Endpoints](./api_endpoints.md) - Documentación completa de API
- [Configuration Tests README](../tests/api/postman/Configuration_Tests_README.md) - Guía de tests
- [AGENTS.md](../AGENTS.md) - Guía de desarrollo del proyecto

## 📞 Soporte

Si encuentras algún problema durante la validación:

1. Verifica que todas las variables de entorno están configuradas
2. Revisa los logs del servidor para mensajes de error
3. Ejecuta tests unitarios para verificar lógica de negocio
4. Consulta la documentación de cada componente

---

**¡Validación completada exitosamente! 🎊**
