# 📊 Cómo Ver los Resultados de los Tests

## 🎯 Acceso Rápido a Resultados

### 📄 Archivos de Resultados Generados

Todos los resultados están en la carpeta `qa_automated/`:

1. **🛡️ RESULTADOS_ANALISIS_SEGURIDAD.md**
   - Resultados completos del análisis de seguridad estática
   - Vulnerabilidades encontradas y corregidas
   - Métricas y estadísticas

2. **✅ CORRECCION_B104.md**
   - Detalles de la corrección de la vulnerabilidad B104
   - Antes/después del código
   - Instrucciones de verificación

3. **📊 RESULTADOS_EJECUCION.md**
   - Resumen de la ejecución de todos los scripts
   - Estado de cada tipo de test
   - Problemas encontrados y soluciones

4. **📖 README_TESTING.md**
   - Documentación completa de los scripts
   - Instrucciones de uso
   - Ejemplos de ejecución

---

## 🌐 URLs para Ver Resultados (Archivos Locales)

### Windows (File Protocol)

Abre estos enlaces en tu navegador:

```
file:///F:/Prueba Restaurant/prueba-restaurante-/qa_automated/RESULTADOS_ANALISIS_SEGURIDAD.md
```

```
file:///F:/Prueba Restaurant/prueba-restaurante-/qa_automated/CORRECCION_B104.md
```

```
file:///F:/Prueba Restaurant/prueba-restaurante-/qa_automated/RESULTADOS_EJECUCION.md
```

```
file:///F:/Prueba Restaurant/prueba-restaurante-/qa_automated/README_TESTING.md
```

### Dashboard HTML Visual

Abre el dashboard interactivo:

```
file:///F:/Prueba Restaurant/prueba-restaurante-/qa_automated/generate_reports.html
```

---

## 💻 Comandos para Ver Resultados

### PowerShell (Windows)

```powershell
# Ver análisis de seguridad
Get-Content qa_automated\RESULTADOS_ANALISIS_SEGURIDAD.md

# Ver corrección B104
Get-Content qa_automated\CORRECCION_B104.md

# Ver resumen de ejecución
Get-Content qa_automated\RESULTADOS_EJECUCION.md

# Abrir dashboard HTML
Start-Process "qa_automated\generate_reports.html"
```

### Abrir en Editor/Visualizador

```powershell
# Abrir en VS Code
code qa_automated\RESULTADOS_ANALISIS_SEGURIDAD.md

# Abrir en navegador (Markdown)
Start-Process "qa_automated\RESULTADOS_ANALISIS_SEGURIDAD.md"
```

---

## 📈 Resultados por Tipo de Test

### 1. ✅ Análisis de Seguridad (COMPLETADO)

**Estado:** ✅ Ejecutado exitosamente

**Resultados:**
- **Vulnerabilidades encontradas:** 1 (en código propio)
- **Vulnerabilidad B104:** ✅ Corregida
- **Estado final:** 0 vulnerabilidades en código propio

**Ver resultados:**
- Archivo: `qa_automated/RESULTADOS_ANALISIS_SEGURIDAD.md`
- Corrección: `qa_automated/CORRECCION_B104.md`

**Re-ejecutar:**
```powershell
.\qa_automated\run_security_analysis.ps1
```

---

### 2. ⚙️ Tests Funcionales (PENDIENTE)

**Estado:** ⚠️ Requiere configuración de base de datos

**Tests disponibles:** 30+ tests en `qa_automated/tests/test_funcionalidad_auth.py`

**Ejecutar:**
```powershell
# Con configuración de BD
docker run --rm `
  -v "${PWD}:/app" `
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" `
  -e JWT_SECRET="test-secret" `
  -e PYTHONPATH=/app:/app/api `
  salchipapas-qa:latest `
  pytest /app/qa_automated/tests/test_funcionalidad_auth.py -v --html=/app/qa_automated/reports/funcional_tests.html
```

**Ver resultados:**
- Reporte HTML: `qa_automated/reports/funcional_tests.html`
- Consola: Salida directa del comando

---

### 3. 📈 Pruebas de Estrés (LISTO)

**Estado:** ✅ Listo para ejecutar (requiere API corriendo)

**Escenario:** 500 usuarios virtuales durante 60 segundos

**Ejecutar:**
```powershell
# Con interfaz web (recomendado)
docker run --rm -p 8089:8089 -v "${PWD}:/app" salchipapas-qa:latest `
  locust -f /app/qa_automated/tests/load_test_auth.py `
         --host=http://host.docker.internal:5000

# Luego abrir: http://localhost:8089
```

**Ver resultados:**
- Interfaz web: `http://localhost:8089` (métricas en tiempo real)
- Reporte HTML: `qa_automated/reports/load_test_report.html` (al finalizar)

---

## 🎨 Dashboard Visual HTML

He creado un dashboard HTML interactivo que puedes abrir directamente:

**Ubicación:** `qa_automated/generate_reports.html`

**Abrir:**
```powershell
# Opción 1: Doble clic en el archivo
# Opción 2: Desde PowerShell
Start-Process "qa_automated\generate_reports.html"

# Opción 3: URL directa
# file:///F:/Prueba Restaurant/prueba-restaurante-/qa_automated/generate_reports.html
```

El dashboard muestra:
- ✅ Estado de cada tipo de test
- 📊 Métricas y estadísticas
- 🔗 Enlaces a todos los archivos de resultados
- 📈 Resumen visual de los resultados

---

## 📂 Estructura de Archivos de Resultados

```
qa_automated/
├── RESULTADOS_ANALISIS_SEGURIDAD.md    ← Análisis de seguridad
├── CORRECCION_B104.md                   ← Corrección de vulnerabilidad
├── RESULTADOS_EJECUCION.md              ← Resumen de ejecución
├── README_TESTING.md                    ← Documentación completa
├── generate_reports.html                ← Dashboard visual
├── VER_RESULTADOS.md                    ← Este archivo
└── reports/                             ← Reportes HTML (se crean al ejecutar)
    ├── funcional_tests.html             ← Tests funcionales (cuando se ejecuten)
    └── load_test_report.html            ← Pruebas de estrés (cuando se ejecuten)
```

---

## 🔍 Resumen de Resultados Actuales

### ✅ Completados

1. **Análisis de Seguridad**
   - ✅ Ejecutado
   - ✅ 1 vulnerabilidad encontrada y corregida
   - ✅ Estado: 0 vulnerabilidades en código propio

### ⚠️ Pendientes

2. **Tests Funcionales**
   - ⚠️ Requiere configuración de BD
   - ✅ Scripts listos (30+ tests)

3. **Pruebas de Estrés**
   - ⚠️ Requiere API corriendo
   - ✅ Scripts listos

---

## 🚀 Próximos Pasos

1. **Ver resultados actuales:**
   - Abre `generate_reports.html` en tu navegador
   - O lee los archivos `.md` directamente

2. **Ejecutar tests funcionales:**
   - Configura variables de entorno de BD
   - Ejecuta con el comando proporcionado arriba

3. **Ejecutar pruebas de estrés:**
   - Asegúrate de que la API esté corriendo
   - Ejecuta Locust con el comando proporcionado

---

**¿Necesitas ayuda?** Revisa `README_TESTING.md` para documentación completa.

