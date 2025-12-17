# 🧪 Documentación de Scripts de Testing

Este documento describe los scripts de pruebas automatizadas generados para el módulo de autenticación.

## 📋 Scripts Disponibles

### 1. ⚙️ Script de Validación Funcional

**Archivo:** `tests/test_funcionalidad_auth.py`

**Propósito:** Pruebas unitarias y de integración para validar todos los criterios de aceptación del módulo de autenticación.

**Criterios de Aceptación Validados:**
1. ✅ El endpoint POST /api/auth/register debe crear un usuario y retornar un token JWT válido
2. ✅ El endpoint POST /api/auth/login debe autenticar credenciales válidas y retornar un token JWT
3. ✅ El endpoint POST /api/auth/login debe rechazar credenciales inválidas con código 401
4. ✅ El endpoint GET /api/auth/profile debe retornar el perfil del usuario autenticado
5. ✅ El endpoint GET /api/auth/profile debe rechazar peticiones sin token con código 401
6. ✅ La validación del campo password debe ser fuerte (hash bcrypt)
7. ✅ El token JWT debe contener userId y role
8. ✅ El token JWT debe expirar después de 7 días
9. ✅ El hash de contraseña no debe ser reversible
10. ✅ No se debe permitir registro de usuarios duplicados

**Ejecución:**
```bash
# Ejecutar todos los tests funcionales
./qa_automated/run_qa.sh tests/test_funcionalidad_auth.py

# Ejecutar con más verbosidad
./qa_automated/run_qa.sh tests/test_funcionalidad_auth.py -v -s

# Ejecutar solo tests marcados como "smoke"
./qa_automated/run_qa.sh tests/test_funcionalidad_auth.py -m smoke
```

**Windows (PowerShell):**
```powershell
.\qa_automated\run_qa.ps1 tests/test_funcionalidad_auth.py
```

---

### 2. 🛡️ Script de Análisis de Seguridad

**Archivo:** `tests/security_analysis.py`

**Propósito:** Análisis estático de seguridad (SAST) usando Bandit para detectar vulnerabilidades comunes en código Python.

**Herramienta:** Bandit (https://bandit.readthedocs.io/)

**Niveles Analizados:**
- 🔴 Severidad Alta (High)
- 🟡 Severidad Media (Medium)

**Ejecución:**
```bash
# Linux/Mac/WSL
chmod +x qa_automated/run_security_analysis.sh
./qa_automated/run_security_analysis.sh
```

**Windows (PowerShell):**
```powershell
.\qa_automated\run_security_analysis.ps1
```

**Ejecución Manual (sin Docker):**
```bash
# Instalar Bandit
pip install bandit[toml]

# Ejecutar análisis
python qa_automated/tests/security_analysis.py
```

**Códigos de Salida:**
- `0`: Análisis exitoso, no se encontraron vulnerabilidades
- `1`: Se encontraron vulnerabilidades de seguridad
- `2`: Bandit no está instalado
- `3`: Error durante la ejecución

---

### 3. 📈 Script de Pruebas de Estrés

**Archivo:** `tests/load_test_auth.py`

**Propósito:** Pruebas de carga y estrés para validar el rendimiento del módulo de autenticación bajo carga alta.

**Herramienta:** Locust (https://locust.io/)

**Escenario de Carga:**
- **Usuarios virtuales:** 500
- **Rampa:** 50 usuarios por segundo
- **Duración:** 60 segundos
- **Endpoints probados:**
  - POST /api/auth/login (60% de requests)
  - POST /api/auth/register (30% de requests)
  - GET /api/auth/profile (10% de requests)

**Métricas Clave:**
- ✅ Latencia promedio (p95) < 200 ms
- ✅ Tasa de éxito > 95%
- ✅ Tasa de error < 5%

**Prerrequisitos:**
```bash
# Instalar Locust
pip install locust
```

**Ejecución con Interfaz Web:**
```bash
# Iniciar servidor Locust
locust -f qa_automated/tests/load_test_auth.py --host=http://localhost:5000

# Abrir navegador en http://localhost:8089
# Configurar: 500 usuarios, 50 ramp-up, 60 segundos
```

**Ejecución Headless (sin UI):**
```bash
# Ejecutar directamente con parámetros
locust -f qa_automated/tests/load_test_auth.py \
       --host=http://localhost:5000 \
       --headless \
       -u 500 \
       -r 50 \
       -t 60s \
       --html=qa_automated/reports/load_test_report.html
```

**Variables de Entorno:**
```bash
# Cambiar URL de la API
export API_BASE_URL=http://localhost:5000
locust -f qa_automated/tests/load_test_auth.py --host=$API_BASE_URL
```

**Nota:** Asegúrate de que la API esté corriendo antes de ejecutar las pruebas de carga.

---

## 🚀 Ejecución Completa de Todos los Tests

### Opción 1: Ejecutar por Separado

```bash
# 1. Tests funcionales
./qa_automated/run_qa.sh tests/test_funcionalidad_auth.py

# 2. Análisis de seguridad
./qa_automated/run_security_analysis.sh

# 3. Pruebas de estrés (requiere API corriendo)
locust -f qa_automated/tests/load_test_auth.py --host=http://localhost:5000 --headless -u 500 -r 50 -t 60s
```

### Opción 2: Script Integrado (Crear si es necesario)

Puedes crear un script que ejecute todos los tests en secuencia:

```bash
#!/bin/bash
# run_all_tests.sh

echo "🧪 Ejecutando suite completa de tests..."

# Tests funcionales
echo "1️⃣  Ejecutando tests funcionales..."
./qa_automated/run_qa.sh tests/test_funcionalidad_auth.py || exit 1

# Análisis de seguridad
echo "2️⃣  Ejecutando análisis de seguridad..."
./qa_automated/run_security_analysis.sh || exit 1

# Pruebas de estrés (opcional, requiere API)
echo "3️⃣  Ejecutando pruebas de estrés..."
echo "   (Asegúrate de que la API esté corriendo en http://localhost:5000)"
locust -f qa_automated/tests/load_test_auth.py \
       --host=http://localhost:5000 \
       --headless -u 500 -r 50 -t 60s \
       --html=qa_automated/reports/load_test_report.html || exit 1

echo "✅ Todos los tests completados exitosamente"
```

---

## 📊 Reportes y Resultados

### Tests Funcionales
- Los resultados se muestran en la consola
- Coverage report disponible con `--cov-report=html`
- Reporte HTML en `htmlcov/index.html`

### Análisis de Seguridad
- Resultados en consola con resumen de vulnerabilidades
- Formato JSON disponible para integración CI/CD

### Pruebas de Estrés
- Reporte HTML generado en `qa_automated/reports/load_test_report.html`
- Métricas detalladas en consola
- Validación automática de criterios de aceptación

---

## 🔧 Configuración Avanzada

### Variables de Entorno para Tests

```bash
# Configurar URL de API para tests
export API_BASE_URL=http://localhost:5000

# Configurar base de datos de testing
export DATABASE_URL=postgresql://test:test@localhost:5432/test_db

# Configurar JWT secret para tests
export JWT_SECRET=test-secret-key
```

### Integración con CI/CD

**GitHub Actions:**
```yaml
name: QA Tests

on: [push, pull_request]

jobs:
  functional-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Functional Tests
        run: ./qa_automated/run_qa.sh tests/test_funcionalidad_auth.py
  
  security-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Security Analysis
        run: ./qa_automated/run_security_analysis.sh
  
  load-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start API
        run: docker-compose up -d api
      - name: Run Load Tests
        run: |
          pip install locust
          locust -f qa_automated/tests/load_test_auth.py \
                 --host=http://localhost:5000 \
                 --headless -u 500 -r 50 -t 60s
```

---

## 📝 Notas Importantes

1. **Tests Funcionales:** Usan mocks para aislar las pruebas de la base de datos real
2. **Análisis de Seguridad:** Solo reporta vulnerabilidades de severidad alta y media
3. **Pruebas de Estrés:** Requieren que la API esté corriendo y accesible
4. **Usuarios de Prueba:** Las pruebas de carga asumen que existen usuarios de prueba en la BD

---

## 🐛 Troubleshooting

### Error: "Module not found: api"
**Solución:** Asegúrate de ejecutar los scripts desde la raíz del proyecto.

### Error: "Bandit not found"
**Solución:** El script intentará instalar Bandit automáticamente, o instala manualmente: `pip install bandit[toml]`

### Error: "Connection refused" en pruebas de carga
**Solución:** Verifica que la API esté corriendo en el puerto especificado.

### Tests funcionales fallan con "401 Unauthorized"
**Solución:** Verifica que los mocks estén configurados correctamente. Los tests usan mocks, no requieren API real.

---

**Última actualización:** Diciembre 2024  
**Versión:** 1.0.0

