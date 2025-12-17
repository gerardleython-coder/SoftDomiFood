# 🧪 Entorno de Testing Automatizado

Infraestructura de testing automatizado usando contenedores Docker para el sistema de pedidos de domicilio.

## 📋 Descripción

Este módulo proporciona un entorno aislado y reproducible para ejecutar pruebas automatizadas de la API FastAPI. Utiliza Docker para garantizar consistencia entre diferentes entornos de desarrollo.

## 🏗️ Arquitectura

```
prueba-restaurante/
├── qa_automated/              # Directorio de testing
│   ├── Dockerfile.qa          # Imagen Docker para testing
│   ├── run_qa.sh              # Script de ejecución
│   ├── README.md              # Este archivo
│   └── tests/                 # Tests (crear según necesidad)
│       ├── test_auth.py
│       ├── test_products.py
│       ├── test_orders.py
│       └── conftest.py
│
├── api/                       # API FastAPI (código fuente)
└── docker-compose.yml         # Configuración de servicios
```

## 🚀 Uso Rápido

### Prerrequisitos

- Docker instalado y funcionando
- Bash (Linux/Mac) o Git Bash/WSL (Windows)
- Acceso a la raíz del repositorio

### Ejecución Básica

Desde la **raíz del repositorio**, ejecutar:

**Linux/Mac/WSL:**
```bash
# Dar permisos de ejecución (solo primera vez)
chmod +x qa_automated/run_qa.sh

# Ejecutar todas las pruebas
./qa_automated/run_qa.sh
```

**Windows (PowerShell):**
```powershell
# Ejecutar todas las pruebas
.\qa_automated\run_qa.ps1
```

**Windows (Git Bash/WSL):**
```bash
# Usar el script bash
bash qa_automated/run_qa.sh
```

### Ejecución con Opciones Personalizadas

**Linux/Mac/WSL:**
```bash
# Ejecutar pruebas específicas
./qa_automated/run_qa.sh tests/test_auth.py

# Ejecutar con más verbosidad
./qa_automated/run_qa.sh -v -s

# Ejecutar solo tests marcados como "smoke"
./qa_automated/run_qa.sh -m smoke

# Ejecutar sin coverage
./qa_automated/run_qa.sh --no-cov

# Ejecutar con reporte HTML de coverage
./qa_automated/run_qa.sh --cov=/app/api --cov-report=html
```

**Windows (PowerShell):**
```powershell
# Ejecutar pruebas específicas
.\qa_automated\run_qa.ps1 tests/test_auth.py

# Ejecutar con más verbosidad
.\qa_automated\run_qa.ps1 -v -s

# Ejecutar solo tests marcados como "smoke"
.\qa_automated\run_qa.ps1 -m smoke

# Ejecutar sin coverage
.\qa_automated\run_qa.ps1 --no-cov

# Ejecutar con reporte HTML de coverage
.\qa_automated\run_qa.ps1 --cov=/app/api --cov-report=html
```

## 📁 Estructura de Archivos

### `Dockerfile.qa`

**Propósito:** Define el entorno aislado de pruebas.

**Características:**
- Basado en Python 3.11-slim
- Instala dependencias de la API (`api/requirements.txt`)
- Instala herramientas de testing (pytest, pytest-asyncio, httpx)
- Copia todo el proyecto a `/app` dentro del contenedor
- Ejecuta pruebas desde `/app/qa_automated/`

**Puntos clave anti-error:**
- ✅ Usa `COPY . /app` para copiar todo el proyecto
- ✅ Referencia explícita a `/app/qa_automated/` en CMD
- ✅ Rutas absolutas para evitar problemas de rutas relativas

### `run_qa.sh` / `run_qa.ps1`

**Propósito:** Scripts para ejecución externa desde la raíz del repositorio.

**Características:**
- Valida que se ejecute desde la raíz del proyecto
- Construye la imagen Docker con contexto desde la raíz
- Ejecuta el contenedor con volumen montado
- Maneja errores y limpieza de contenedores
- Disponible en Bash (Linux/Mac/WSL) y PowerShell (Windows)

**Puntos clave anti-error:**
- ✅ Usa `docker build -f qa_automated/Dockerfile.qa .` (contexto desde raíz)
- ✅ Detecta automáticamente la raíz del proyecto
- ✅ Valida existencia de archivos clave antes de ejecutar
- ✅ Rutas absolutas calculadas dinámicamente

## 🧪 Escribiendo Tests

### Estructura Recomendada

```python
# qa_automated/tests/test_auth.py
import pytest
from httpx import AsyncClient
from api.main import app

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        assert response.status_code == 200
        assert "token" in response.json()
```

### Configuración de Tests (conftest.py)

```python
# qa_automated/tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from api.main import app

@pytest.fixture
def event_loop():
    """Crear event loop para tests asíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Cliente HTTP para tests"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

## 🔧 Configuración Avanzada

### Variables de Entorno para Testing

El contenedor puede recibir variables de entorno modificando `run_qa.sh`:

```bash
docker run --rm \
    -e DATABASE_URL="postgresql://test:test@localhost:5432/test_db" \
    -e JWT_SECRET="test-secret" \
    "$IMAGE_NAME" \
    pytest /app/qa_automated/ $PYTEST_ARGS
```

### Integración con CI/CD

Ejemplo para GitHub Actions:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run QA Tests
        run: ./qa_automated/run_qa.sh
```

## 📊 Reportes y Coverage

### Ver Reporte de Coverage

```bash
# Generar reporte HTML
./qa_automated/run_qa.sh --cov=/app/api --cov-report=html

# El reporte estará en: htmlcov/index.html
```

### Opciones de Reporte

- `--cov-report=term` - Reporte en terminal (por defecto)
- `--cov-report=html` - Reporte HTML
- `--cov-report=xml` - Reporte XML (para CI/CD)
- `--cov-report=json` - Reporte JSON

## 🐛 Troubleshooting

### Error: "Dockerfile no encontrado"

**Causa:** Ejecutando el script desde un directorio incorrecto.

**Solución:** Asegúrate de ejecutar desde la raíz del repositorio:
```bash
cd /ruta/al/repositorio/prueba-restaurante-
./qa_automated/run_qa.sh
```

### Error: "No module named 'api'"

**Causa:** El contexto de Docker no incluye el directorio `api/`.

**Solución:** Verifica que el `docker build` se ejecute desde la raíz:
```bash
# Verificar que estás en la raíz
ls api/requirements.txt  # Debe existir

# Ejecutar script
./qa_automated/run_qa.sh
```

### Error: "Permission denied" (Linux/Mac)

**Solución:** Dar permisos de ejecución:
```bash
chmod +x qa_automated/run_qa.sh
```

### Error: "Permission denied" (Windows)

**Solución:** Usar Git Bash o WSL, o ejecutar con PowerShell:
```powershell
bash qa_automated/run_qa.sh
```

## 📝 Mejores Prácticas

1. **Siempre ejecutar desde la raíz:** El script detecta automáticamente la raíz, pero es mejor estar ahí.

2. **Usar nombres descriptivos para tests:**
   ```python
   def test_user_cannot_login_with_invalid_credentials():
       # Test claro y descriptivo
   ```

3. **Organizar tests por módulo:**
   - `test_auth.py` - Tests de autenticación
   - `test_products.py` - Tests de productos
   - `test_orders.py` - Tests de pedidos

4. **Usar fixtures para datos de prueba:**
   ```python
   @pytest.fixture
   def sample_product():
       return {"name": "Test Product", "price": 10.0}
   ```

5. **Marcar tests según tipo:**
   ```python
   @pytest.mark.smoke
   @pytest.mark.integration
   def test_critical_flow():
       pass
   ```

## 🔗 Integración con el Proyecto

### Dependencias de Testing

Las dependencias de testing se instalan automáticamente en el Dockerfile:
- `pytest` - Framework de testing
- `pytest-asyncio` - Soporte para código asíncrono
- `pytest-cov` - Coverage reporting
- `httpx` - Cliente HTTP para testing de FastAPI
- `pytest-mock` - Mocking utilities

### Conexión a Base de Datos de Testing

Para tests que requieran base de datos, puedes usar:
- Base de datos en memoria (SQLite)
- Contenedor Docker separado para testing
- Mock de la base de datos

## 📚 Recursos Adicionales

- [Documentación de pytest](https://docs.pytest.org/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

---

**Última actualización:** Noviembre 2025  
**Versión:** 1.0.0

