# Postman API Tests - Documentation Index

Índice completo de documentación para las pruebas de API de Agent Lab con Postman.

## 📚 Documentación Disponible

### 🚀 Quick Start
- **[QUICKSTART.md](QUICKSTART.md)** - Guía de inicio rápido (5 minutos)
  - Setup inicial en 4 pasos
  - Verificación básica
  - Troubleshooting común

### 📖 Documentación Completa
- **[README.md](README.md)** - Documentación completa del proyecto (450+ líneas)
  - Estructura detallada de la colección
  - Configuración paso a paso
  - Variables de ambiente y colección
  - Scripts de validación
  - Mejores prácticas
  - Troubleshooting extensivo

### 🎯 Guías Específicas
- **[NEWMAN_GUIDE.md](NEWMAN_GUIDE.md)** - Ejecución desde línea de comandos
  - Instalación de Newman
  - Comandos básicos y avanzados
  - Scripts de automatización (PowerShell & Bash)
  - Integración con CI/CD (GitHub Actions, GitLab CI)
  - Reportes (CLI, JSON, HTML)

### 📊 Ejemplos y Referencias
- **[EXAMPLE_EXECUTION.md](EXAMPLE_EXECUTION.md)** - Output esperado de ejecución exitosa
  - Collection Runner output completo
  - Métricas de performance
  - Distribución de tiempos de respuesta
  - Assertions summary
  - Variables finales

### 📝 Documentación Técnica
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Resumen de implementación
  - Archivos creados
  - Estructura de la colección
  - Características implementadas
  - Decisiones de diseño
  - Cobertura de tests

## 📂 Estructura de Archivos

```
tests/api/
├── README.md                          # Documentación principal ⭐
├── QUICKSTART.md                      # Inicio rápido (5 min) ⚡
├── NEWMAN_GUIDE.md                    # Guía de Newman CLI 🖥️
├── EXAMPLE_EXECUTION.md               # Output esperado 📊
├── IMPLEMENTATION_SUMMARY.md          # Resumen técnico 📝
├── postman/
│   ├── collections/
│   │   └── Agent_Lab_API.postman_collection.json    # 27 requests, 7 carpetas
│   ├── environments/
│   │   ├── development.postman_environment.json     # Localhost:8000
│   │   └── production.postman_environment.json      # Production
│   └── globals/
│       └── workspace.postman_globals.json           # Variables globales
└── fixtures/
    ├── sample_doc_1.txt                             # Python best practices
    ├── sample_doc_2.md                              # FastAPI overview
    └── sample_doc_3.txt                             # SOLID principles
```

## 🎯 Flujo de Lectura Recomendado

### Para Usuarios Nuevos

1. **[QUICKSTART.md](QUICKSTART.md)** (5 min)
   - Setup básico e importación
   - Primera ejecución

2. **[README.md](README.md)** - Sección "Configuración Inicial" (10 min)
   - Entender estructura
   - Configurar variables

3. **Ejecutar tests** en Postman (5 min)
   - Ver cómo funcionan
   - Revisar test scripts

4. **[EXAMPLE_EXECUTION.md](EXAMPLE_EXECUTION.md)** (opcional)
   - Comparar resultados

### Para Automatización/CI/CD

1. **[QUICKSTART.md](QUICKSTART.md)** (5 min)
   - Verificar funcionamiento básico

2. **[NEWMAN_GUIDE.md](NEWMAN_GUIDE.md)** (15 min)
   - Instalación de Newman
   - Scripts de automatización
   - Integración con CI/CD

3. **[README.md](README.md)** - Sección "Troubleshooting" (5 min)
   - Resolver problemas comunes

### Para Desarrolladores que Agregan Tests

1. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** (15 min)
   - Entender decisiones de diseño
   - Ver patrones implementados

2. **[README.md](README.md)** - Secciones técnicas (20 min)
   - Scripts de validación
   - Variables de colección
   - Dependencias entre requests

3. **Revisar código de la colección** (30 min)
   - Abrir archivo JSON
   - Ver estructura de test scripts
   - Entender pre-request scripts

## 🔍 Búsqueda Rápida

### ¿Cómo hacer X?

| Pregunta | Documento | Sección |
|----------|-----------|---------|
| ¿Cómo importar en Postman? | [QUICKSTART.md](QUICKSTART.md) | Setup Rápido → 1. Importar |
| ¿Cómo configurar API keys? | [README.md](README.md) | Configuración Inicial → 2. Configurar Variables |
| ¿Cómo ejecutar desde CLI? | [NEWMAN_GUIDE.md](NEWMAN_GUIDE.md) | Comandos de Ejecución |
| ¿Cómo integrar con GitHub Actions? | [NEWMAN_GUIDE.md](NEWMAN_GUIDE.md) | Integración con CI/CD |
| ¿Qué hacer si falla un test? | [README.md](README.md) | Troubleshooting |
| ¿Cómo agregar un nuevo test? | [README.md](README.md) | Contribuir |
| ¿Cómo funciona el cleanup? | [README.md](README.md) | Limpieza Post-Ejecución |
| ¿Qué output esperar? | [EXAMPLE_EXECUTION.md](EXAMPLE_EXECUTION.md) | Todo el documento |
| ¿Por qué esta arquitectura? | [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Decisiones de Diseño |

## 📊 Estadísticas del Proyecto

```
Total Documentación:     5 archivos
Total Líneas:           ~1,800 líneas
Requests:               27
Test Scripts:           89 assertions
Carpetas:               7 (secuenciales)
Fixtures:               3 documentos (~92 líneas)
Ambientes:              2 (dev, prod)
```

## 🎓 Conceptos Clave

### Variables de Postman
- **Collection Variables**: Compartidas entre todos los requests de la colección
- **Environment Variables**: Específicas del ambiente (dev/prod)
- **Global Variables**: Compartidas entre todas las colecciones del workspace

### Test Scripts
Código JavaScript que se ejecuta después de cada request para validar respuestas.

### Pre-request Scripts
Código JavaScript que se ejecuta antes de cada request para preparar datos.

### Newman
CLI oficial de Postman para ejecutar colecciones desde terminal.

### Collection Runner
Herramienta de Postman para ejecutar múltiples requests secuencialmente.

## 🔗 Enlaces Externos

### Postman Learning
- [Postman Documentation](https://learning.postman.com/)
- [Writing Tests](https://learning.postman.com/docs/writing-scripts/test-scripts/)
- [Variables](https://learning.postman.com/docs/sending-requests/variables/)
- [Newman CLI](https://learning.postman.com/docs/running-collections/using-newman-cli/)

### API Documentation
- [Agent Lab API Endpoints](../../docs/api_endpoints.md)
- [RAG Implementation Guide](../../docs/rag_guide.md)
- [LLM Interface Guide](../../docs/llm_interface_guide.md)

### Project Documentation
- [Project README](../../README.md)
- [Agent Guidelines](../../AGENTS.md)
- [Python Unit Tests](../unit/test_chat_routes.py)

## ❓ FAQ

### ¿Necesito instalar Newman para usar Postman Desktop?
No, Newman es solo para ejecución CLI. Postman Desktop incluye Collection Runner integrado.

### ¿Puedo ejecutar solo algunos tests?
Sí, en Postman Desktop selecciona las carpetas/requests que quieras. En Newman usa `--folder`.

### ¿Los tests modifican datos de producción?
No si usas el ambiente "Development". El namespace de prueba (`postman-test`) está aislado.

### ¿Cuánto tardan los tests completos?
~45 segundos en total (varía según respuesta del LLM).

### ¿Necesito limpiar manualmente después de cada ejecución?
Idealmente sí, ejecutar carpeta "7. Cleanup". O usa namespace único por ejecución.

### ¿Puedo agregar más tests?
Sí, sigue los patrones existentes. Ver sección "Contribuir" en [README.md](README.md).

## 🆘 Soporte

### Pasos para Resolver Problemas

1. **Consultar Troubleshooting**: [README.md](README.md) → Troubleshooting
2. **Verificar Variables**: Ambiente configurado correctamente
3. **Check Logs**: Console logs en cada request
4. **Ejecutar Health Check**: Verificar que API está corriendo
5. **Tests Unitarios**: Ejecutar `make test-unit` para aislar problema

### Información Útil para Reportar Issues

```
- Sistema Operativo: Windows/Linux/Mac
- Versión de Postman: X.X.X
- Versión de Newman (si aplica): X.X.X
- Ambiente usado: Development/Production
- Request que falla: Nombre exacto
- Error message: Copiar output completo
- Variables de ambiente: Verificar que están configuradas
```

## 📅 Mantenimiento

### Actualizar Documentación

Cuando se agreguen nuevos endpoints o tests:

1. Actualizar [README.md](README.md)
2. Agregar request a la colección
3. Actualizar [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
4. Actualizar este índice si se agregan archivos nuevos

### Versionado

- **Colección**: Usar semantic versioning en el archivo JSON
- **Documentación**: Fecha de última actualización al final de cada archivo
- **Ambientes**: Incluir versión compatible en descripción

---

**Última actualización**: 2025-12-15  
**Versión de la documentación**: 1.0.0  
**Compatibilidad**: Postman 10.0+, Newman 6.0+
