# ⚠️ Explicación: Por qué los Tests Funcionales están Pendientes

## 🔍 Problema Técnico

Los **Tests Funcionales** aparecen como **"Pendiente"** porque **no se pudieron ejecutar** debido a un problema de configuración de base de datos.

---

## 📋 Cadena de Dependencias

### 1. Los Tests Importan `api.main`

```python
# qa_automated/tests/test_funcionalidad_auth.py (línea 38)
from api.main import app
```

### 2. `api.main` Importa `database`

```python
# api/main.py (línea 8)
from database import engine, Base, get_db
```

### 3. `database.py` Requiere `DATABASE_URL`

Cuando Python importa `database.py`, este archivo **inmediatamente** intenta crear un engine de SQLAlchemy:

```python
# api/database.py (probablemente algo como esto)
from sqlalchemy.ext.asyncio import create_async_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "")  # Si no existe, es string vacío

# ⚠️ AQUÍ FALLA si DATABASE_URL está vacío
engine = create_async_engine(DATABASE_URL, echo=False)
```

### 4. Error al Inicializar

Si `DATABASE_URL` no está configurada o está vacía, SQLAlchemy lanza un error:

```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string ''
```

**Esto ocurre ANTES de que los tests siquiera comiencen a ejecutarse.**

---

## 🎯 ¿Por qué Ocurre Esto?

### Problema de Diseño

Los tests están diseñados para usar **mocks** (simulaciones) y **no deberían necesitar una base de datos real**. Sin embargo:

1. **La importación de `api.main` es síncrona** - Ocurre cuando Python carga el módulo
2. **`database.py` se ejecuta al importarse** - Crea el engine inmediatamente
3. **No hay forma de "mockear" antes de la importación** - El error ocurre antes de que los tests puedan configurar mocks

### Ejemplo del Flujo

```
1. pytest carga test_funcionalidad_auth.py
   ↓
2. Python ejecuta: from api.main import app
   ↓
3. Python ejecuta: from database import engine
   ↓
4. database.py intenta: engine = create_async_engine(DATABASE_URL)
   ↓
5. ❌ ERROR: DATABASE_URL está vacío
   ↓
6. Los tests NUNCA se ejecutan
```

---

## ✅ Soluciones Posibles

### Solución 1: Configurar Variables de Entorno (Rápida)

**Ejecutar con DATABASE_URL configurada:**

```powershell
docker run --rm `
  -v "${PWD}:/app" `
  -e DATABASE_URL="postgresql+asyncpg://test:test@localhost:5432/test_db" `
  -e JWT_SECRET="test-secret-key" `
  -e PYTHONPATH=/app:/app/api `
  salchipapas-qa:latest `
  pytest /app/qa_automated/tests/test_funcionalidad_auth.py -v
```

**Problema:** Requiere que PostgreSQL esté corriendo y accesible.

---

### Solución 2: Usar Base de Datos en Memoria (Recomendada)

**Modificar `api/database.py` para usar SQLite en memoria cuando no hay DATABASE_URL:**

```python
# api/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# Si no hay DATABASE_URL, usar SQLite en memoria para tests
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=False)
```

**Ventajas:**
- ✅ No requiere PostgreSQL corriendo
- ✅ Los tests pueden ejecutarse sin configuración adicional
- ✅ Más rápido (en memoria)

---

### Solución 3: Lazy Initialization (Más Compleja)

**Modificar `database.py` para inicializar el engine solo cuando se necesite:**

```python
# api/database.py
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        _engine = create_async_engine(DATABASE_URL, echo=False)
    return _engine
```

**Ventajas:**
- ✅ Permite mockear antes de la inicialización
- ✅ Más flexible

**Desventajas:**
- ⚠️ Requiere modificar todo el código que usa `engine`

---

### Solución 4: Mockear en conftest.py (Ideal para Tests)

**Crear `qa_automated/tests/conftest.py` que mockee antes de importar:**

```python
# qa_automated/tests/conftest.py
import os
import sys
from unittest.mock import patch

# Configurar DATABASE_URL ANTES de importar api.main
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Ahora sí importar
from api.main import app
```

**Ventajas:**
- ✅ No requiere modificar código de producción
- ✅ Solo afecta a los tests
- ✅ Solución estándar en pytest

---

## 🎯 Recomendación

**Usar Solución 4 (conftest.py) + Solución 2 (fallback a SQLite):**

1. **Modificar `api/database.py`** para usar SQLite en memoria si no hay DATABASE_URL
2. **Crear `qa_automated/tests/conftest.py`** que configure el entorno antes de importar

Esto permite:
- ✅ Tests funcionan sin configuración adicional
- ✅ Producción sigue usando PostgreSQL
- ✅ No requiere modificar mucho código

---

## 📊 Estado Actual vs Ideal

### Estado Actual ❌

```
Tests → Import api.main → Import database → ❌ ERROR (sin DATABASE_URL)
```

### Estado Ideal ✅

```
Tests → conftest.py configura DATABASE_URL → Import api.main → Import database → ✅ OK
```

---

## 🔧 ¿Quieres que lo Corrija?

Puedo implementar la **Solución 4** (conftest.py) que es la más limpia y no requiere modificar código de producción. ¿Te parece bien?

---

## 📝 Resumen

**¿Por qué están pendientes?**
- Los tests no se pueden ejecutar porque `database.py` requiere `DATABASE_URL` al importarse
- El error ocurre ANTES de que los tests puedan configurar mocks
- Es un problema de orden de inicialización

**¿Cómo solucionarlo?**
- Configurar `DATABASE_URL` antes de importar `api.main`
- Usar `conftest.py` para configurar el entorno de testing
- O modificar `database.py` para usar SQLite en memoria como fallback

