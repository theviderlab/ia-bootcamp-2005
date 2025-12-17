# Newman CLI - Command Line Execution

Guía para ejecutar las pruebas de Postman usando Newman desde la línea de comandos.

## 📦 Instalación de Newman

### Windows (PowerShell)
```powershell
npm install -g newman
newman --version
```

### Linux/Mac
```bash
npm install -g newman
newman --version
```

### Verificar instalación
```bash
newman --version
# Output esperado: 6.0.0 (o superior)
```

## 🚀 Comandos de Ejecución

### 1. Ejecución Básica

```bash
newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json \
  -e tests/api/postman/environments/development.postman_environment.json
```

### 2. Con Delay Entre Requests

```bash
newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json \
  -e tests/api/postman/environments/development.postman_environment.json \
  --delay-request 100
```

**Nota**: Delay de 100ms recomendado para evitar sobrecarga del servidor.

### 3. Con Múltiples Reportes

```bash
newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json \
  -e tests/api/postman/environments/development.postman_environment.json \
  --reporters cli,json,html \
  --reporter-json-export results/newman-report.json \
  --reporter-html-export results/newman-report.html
```

### 4. Con Timeout Personalizado

```bash
newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json \
  -e tests/api/postman/environments/development.postman_environment.json \
  --timeout-request 30000 \
  --delay-request 100
```

**Nota**: Timeout de 30s necesario para requests a LLM que pueden tardar.

### 5. Modo Verbose (Debugging)

```bash
newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json \
  -e tests/api/postman/environments/development.postman_environment.json \
  --verbose
```

### 6. Ejecutar Solo Una Carpeta

```bash
newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json \
  -e tests/api/postman/environments/development.postman_environment.json \
  --folder "1. Health & Connectivity"
```

## 🎯 Scripts de Automatización

### PowerShell Script (Windows)

Crear archivo `run-postman-tests.ps1`:

```powershell
# run-postman-tests.ps1
param(
    [string]$Environment = "development"
)

Write-Host "🚀 Starting API Tests..." -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow

# Verificar que el servidor está corriendo
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ API Server is running" -ForegroundColor Green
} catch {
    Write-Host "❌ API Server is not running. Start it with: uv run uvicorn agentlab.api.main:app --reload" -ForegroundColor Red
    exit 1
}

# Crear directorio de resultados si no existe
New-Item -ItemType Directory -Force -Path "results" | Out-Null

# Ejecutar Newman
newman run "tests/api/postman/collections/Agent_Lab_API.postman_collection.json" `
  -e "tests/api/postman/environments/$Environment.postman_environment.json" `
  --delay-request 100 `
  --timeout-request 30000 `
  --reporters cli,json,html `
  --reporter-json-export "results/newman-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json" `
  --reporter-html-export "results/newman-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').html"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Some tests failed. Check the report." -ForegroundColor Red
    exit 1
}
```

**Uso:**
```powershell
.\run-postman-tests.ps1
# O con ambiente específico:
.\run-postman-tests.ps1 -Environment production
```

### Bash Script (Linux/Mac)

Crear archivo `run-postman-tests.sh`:

```bash
#!/bin/bash
# run-postman-tests.sh

ENVIRONMENT="${1:-development}"

echo "🚀 Starting API Tests..."
echo "Environment: $ENVIRONMENT"

# Verificar que el servidor está corriendo
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API Server is running"
else
    echo "❌ API Server is not running. Start it with: uv run uvicorn agentlab.api.main:app --reload"
    exit 1
fi

# Crear directorio de resultados
mkdir -p results

# Timestamp para reportes
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Ejecutar Newman
newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json \
  -e "tests/api/postman/environments/${ENVIRONMENT}.postman_environment.json" \
  --delay-request 100 \
  --timeout-request 30000 \
  --reporters cli,json,html \
  --reporter-json-export "results/newman-report-${TIMESTAMP}.json" \
  --reporter-html-export "results/newman-report-${TIMESTAMP}.html"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    exit 0
else
    echo ""
    echo "❌ Some tests failed. Check the report."
    exit 1
fi
```

**Uso:**
```bash
chmod +x run-postman-tests.sh
./run-postman-tests.sh
# O con ambiente específico:
./run-postman-tests.sh production
```

## 📊 Formatos de Reporte

### CLI Reporter (Default)
Output directo en consola con colores.

```bash
newman run ... --reporters cli
```

### JSON Reporter
Archivo JSON con resultados estructurados.

```bash
newman run ... \
  --reporters json \
  --reporter-json-export results/report.json
```

**Estructura JSON:**
```json
{
  "collection": {...},
  "environment": {...},
  "run": {
    "stats": {
      "requests": {"total": 27, "failed": 0},
      "tests": {"total": 89, "failed": 0},
      "assertions": {"total": 89, "failed": 0}
    },
    "timings": {...},
    "executions": [...]
  }
}
```

### HTML Reporter
Reporte visual interactivo en HTML.

```bash
newman run ... \
  --reporters html \
  --reporter-html-export results/report.html
```

Abrir en navegador:
```bash
# Windows
start results/report.html

# Linux
xdg-open results/report.html

# Mac
open results/report.html
```

## 🔧 Opciones Avanzadas

### Variables de Colección desde CLI

```bash
newman run ... \
  --env-var "base_url=http://staging.api.com" \
  --env-var "test_namespace=newman-test"
```

### Ignorar Redirects

```bash
newman run ... --ignore-redirects
```

### Deshabilitar SSL Verification (Dev only)

```bash
newman run ... --insecure
```

### Exportar Environment después de ejecución

```bash
newman run ... \
  --export-environment results/updated-environment.json
```

## 🚦 Integración con CI/CD

### GitHub Actions

Crear archivo `.github/workflows/api-tests.yml`:

```yaml
name: API Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Newman
        run: npm install -g newman newman-reporter-htmlextra
      
      - name: Setup Python & Start API
        run: |
          pip install uv
          uv sync
          uv run uvicorn agentlab.api.main:app &
          sleep 10
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
      
      - name: Run Newman Tests
        run: |
          newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json \
            -e tests/api/postman/environments/development.postman_environment.json \
            --delay-request 100 \
            --reporters cli,junit \
            --reporter-junit-export results/junit.xml
      
      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: results/junit.xml
```

### GitLab CI

Crear archivo `.gitlab-ci.yml`:

```yaml
api-tests:
  image: node:18
  stage: test
  services:
    - name: python:3.12
  before_script:
    - npm install -g newman
    - pip install uv
    - uv sync
    - nohup uv run uvicorn agentlab.api.main:app &
    - sleep 10
  script:
    - newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json
      -e tests/api/postman/environments/development.postman_environment.json
      --delay-request 100
      --reporters cli,junit
      --reporter-junit-export results/junit.xml
  artifacts:
    when: always
    reports:
      junit: results/junit.xml
```

## 📈 Monitoreo y Alertas

### Newman + Slack Webhook

```bash
newman run ... \
  --reporters cli \
  --bail \
  || curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"❌ API Tests Failed!"}' \
     $SLACK_WEBHOOK_URL
```

### Newman + Email (usando node)

Crear `send-results.js`:

```javascript
const nodemailer = require('nodemailer');
const fs = require('fs');

const results = JSON.parse(fs.readFileSync('results/report.json'));
const failed = results.run.stats.tests.failed;

if (failed > 0) {
  const transporter = nodemailer.createTransport({...});
  transporter.sendMail({
    from: 'api-tests@example.com',
    to: 'team@example.com',
    subject: '❌ API Tests Failed',
    text: `${failed} tests failed. Check the report.`
  });
}
```

## 🧪 Testing en Local

### Pre-ejecución Checklist

```bash
# 1. Verificar servidor
curl http://localhost:8000/health

# 2. Verificar variables de entorno
cat .env | grep -E "OPENAI_API_KEY|PINECONE_API_KEY"

# 3. Verificar fixtures
ls -la tests/api/fixtures/

# 4. Ejecutar tests
newman run tests/api/postman/collections/Agent_Lab_API.postman_collection.json \
  -e tests/api/postman/environments/development.postman_environment.json \
  --delay-request 100
```

## 🐛 Troubleshooting

### Error: ECONNREFUSED

**Problema**: No se puede conectar al servidor.

**Solución**:
```bash
# Verificar que el servidor está corriendo
curl http://localhost:8000/health

# Si no está corriendo, iniciarlo
uv run uvicorn agentlab.api.main:app --reload
```

### Error: Request timeout

**Problema**: Requests tardan más de lo esperado.

**Solución**:
```bash
# Aumentar timeout
newman run ... --timeout-request 60000
```

### Error: Cannot find module 'newman'

**Problema**: Newman no está instalado globalmente.

**Solución**:
```bash
npm install -g newman
```

### Warnings sobre SSL

**Problema**: Certificados SSL en desarrollo.

**Solución**:
```bash
# Solo para desarrollo
newman run ... --insecure
```

## 📚 Referencias

- **Newman Documentation**: https://learning.postman.com/docs/running-collections/using-newman-cli/
- **Newman Reporters**: https://github.com/postmanlabs/newman#reporters
- **Newman + CI/CD**: https://learning.postman.com/docs/running-collections/using-newman-cli/integration-with-jenkins/

---

**Nota**: Siempre ejecutar cleanup después de los tests para evitar acumulación de datos en Pinecone.
