# Quick Start Guide - Postman Tests

Guía rápida para empezar con las pruebas de Postman en 5 minutos.

## ⚡ Setup Rápido

### 1. Importar en Postman (2 min)

```bash
# Abrir Postman Desktop
# Import → Folder → Seleccionar: tests/api/postman/
# ✓ Importará colección + ambientes automáticamente
```

### 2. Configurar Ambiente (1 min)

1. Seleccionar ambiente: **"Agent Lab - Development"**
2. Editar variables:
   - `openai_api_key`: Tu API key de OpenAI (desde .env)
   - `pinecone_api_key`: Tu API key de Pinecone (desde .env)
   
**Nota:** `fixtures_path` existe pero no se usa en las pruebas. Las pruebas RAG envían contenido directamente, no paths de archivos. Ver [postman/RAG_TESTING_NOTES.md](postman/RAG_TESTING_NOTES.md) para detalles.

### 3. Iniciar Servidor (1 min)

```bash
# Desde raíz del proyecto
uv sync
uv run uvicorn agentlab.api.main:app --reload
```

### 4. Ejecutar Tests (1 min)

**Opción A - Runner:**
```
Click derecho en colección "Agent Lab API" → Run collection
Environment: Agent Lab - Development
Click "Run Agent Lab API"
```

**Opción B - Manual:**
```
Ejecutar carpetas en orden:
1. Health & Connectivity
2. LLM Basic Operations
3. Chat Operations
4. RAG - Setup
5. RAG - Query Operations
6. Error Scenarios
7. Cleanup
```

## ✅ Verificación

Si todo funciona:
```
✓ Health Check [200] ✅
✓ Generate - Success [200] ✅
✓ Add Single Document [200] ✅
✓ Query - Basic [200] ✅

Total: 27 requests
Passed: 27 (100%)
Failed: 0
```

## 🔧 Troubleshooting Común

| Problema | Solución |
|----------|----------|
| Connection refused | Verificar servidor corriendo: `uv run uvicorn agentlab.api.main:app --reload` |
| 500 - API key error | Configurar `openai_api_key` en ambiente |
| RAG queries fail | Ejecutar carpeta "4. RAG - Setup" primero |
| Directory not found | Crear directorio `data/initial_knowledge/` en raíz del proyecto (puede estar vacío) |

## 📚 Más Información

- **README Completo**: [tests/api/README.md](README.md)
- **RAG Testing Notes**: [postman/RAG_TESTING_NOTES.md](postman/RAG_TESTING_NOTES.md) - Explica cómo funcionan las pruebas RAG
- **API Docs**: [docs/api_endpoints.md](../../docs/api_endpoints.md)
- **Test Scripts**: Ver tab "Tests" en cada request

## 🧹 Limpieza

Después de ejecutar tests:
```
Ejecutar carpeta "7. Cleanup"
O manualmente en Pinecone: Eliminar namespace "postman-test"
```

---

¿Problemas? Ver [README.md](README.md) completo con troubleshooting detallado.
