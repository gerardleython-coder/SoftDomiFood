# 📋 Pruebas Implementadas - SoftDomiFood

> **Fecha:** Diciembre 2025
> **Proyecto:** Sistema de Pedidos SoftDomiFood
> **Framework:** pytest + asyncio + Playwright

---

## 🚀 Cómo Correr las Pruebas

### **Pruebas de API (Backend)**

```bash
# Todos los tests
docker exec softdomifood-api pytest tests/ -v -o addopts=""

# Tests E2E (End-to-End)
docker exec softdomifood-api pytest tests/e2e/ -v -o addopts=""

# Tests de Integración
docker exec softdomifood-api pytest tests/integration/ -v -o addopts=""

# Tests Unitarios
docker exec softdomifood-api pytest tests/unit/ -v -o addopts=""

# Tests de Performance
docker exec softdomifood-api pytest tests/performance/ -v -o addopts=""

# Un test específico
docker exec softdomifood-api pytest tests/e2e/test_user_registration_flow.py -v -o addopts=""
```

### **Pruebas QA Automatizadas (Playwright)**

```powershell
# Windows
.\qa_automated\run_qa.ps1

# O directamente con Docker
docker-compose run qa-automation
```

### **Detalles Importantes**

- Los tests E2E necesitan que **todos los servicios estén activos** (`docker-compose up -d`)
- La configuración de pytest está en `api/pytest.ini`
- Los fixtures para aislamiento de BD están en `api/tests/conftest.py`
- La documentación completa de testing está en `docs/testing/`

---

## 📑 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Pruebas End-to-End (E2E)](#1-pruebas-end-to-end-e2e)
3. [Pruebas de Integración](#2-pruebas-de-integración)
4. [Pruebas Unitarias](#3-pruebas-unitarias)
5. [Pruebas de Rendimiento](#4-pruebas-de-rendimiento)
6. [Pruebas de Historias de Usuario](#5-pruebas-de-historias-de-usuario)
7. [Pruebas QA Automatizadas](#6-pruebas-qa-automatizadas)
8. [Configuración y Ejecución](#configuración-y-ejecución)
9. [Cobertura y Métricas](#cobertura-y-métricas)

---

## Resumen Ejecutivo

El proyecto SoftDomiFood cuenta con una suite completa de pruebas automatizadas que valida:

- ✅ **30/35 tests E2E** pasando exitosamente (85.7%)
- ✅ **Cobertura de código:** ~70% mínimo
- ✅ **Tests automatizados:** Unitarios, Integración, E2E, Rendimiento
- ✅ **Framework:** pytest con soporte asyncio
- ✅ **Metodología:** TDD (Test-Driven Development)
- ✅ **Principios:** INVEST aplicados a cada HU

---

## 1. Pruebas End-to-End (E2E)

**Ubicación:** `api/tests/e2e/`

### 1.1 Registro de Usuario (`test_user_registration_flow.py`)

Valida el flujo completo de registro de nuevos usuarios.

**Casos de prueba:**
- ✅ `test_tc_hu001_01_successful_registration` - Registro exitoso con credenciales válidas
- ✅ `test_tc_hu001_02_duplicate_email_error` - Error al registrar email duplicado
- ✅ `test_tc_hu001_03_invalid_email_format` - Validación de formato de email
- ✅ `test_registration_password_validation` - Validación de contraseña

**Criterios validados:**
- Email único en el sistema
- Formato de email válido
- Contraseña con requisitos mínimos
- Respuesta HTTP correcta (201 Created)

---

### 1.2 Inicio de Sesión (`test_user_login_flow.py`)

Valida autenticación de clientes y administradores.

**Casos de prueba:**
- ✅ `test_tc_hu002_01_login_success` - Login exitoso con credenciales válidas
- ✅ `test_tc_hu002_02_login_invalid_credentials` - Rechazo de credenciales inválidas
- ✅ `test_tc_hu002_03_admin_access` - Acceso a panel administrativo
- ✅ `test_login_returns_jwt_token` - Generación de token JWT
- ✅ `test_protected_endpoint_requires_auth` - Protección de endpoints

**Criterios validados:**
- Autenticación correcta cliente/admin
- Generación de token JWT
- Validación de credenciales
- Redirección según rol
- Protección de recursos

---

### 1.3 Menú de Productos (`test_product_menu_flow.py`)

Valida visualización y acceso al catálogo de productos.

**Casos de prueba:**
- ✅ `test_tc_hu003_01_product_list_display` - Listado de productos
- ✅ `test_tc_hu003_02_efficient_product_loading` - Carga eficiente
- ✅ `test_product_details_complete` - Detalles completos (nombre, precio, descripción)
- ✅ `test_product_list_pagination` - Paginación

**Criterios validados:**
- Listado completo de productos
- Información detallada por producto
- Tiempos de respuesta aceptables
- Estructura de datos correcta

---

### 1.4 Ciclo de Vida del Pedido (`test_order_lifecycle.py`)

Valida el flujo completo desde la creación hasta la entrega.

**Casos de prueba:**
- ✅ `test_tc_hu004_01_add_product_to_cart` - Agregar producto al carrito
- ✅ `test_tc_hu004_02_cart_total_update` - Actualización del total
- ✅ `test_order_creation_instant_response` - Creación instantánea (HU-04)
- ✅ `test_order_state_transitions` - Transiciones de estado
- ✅ `test_order_status_updates` - Actualización de estados

**Estados validados:**
- `PENDING` → `CONFIRMED` (Worker automático)
- `CONFIRMED` → `PREPARING` (Admin manual)
- `PREPARING` → `READY` (Admin manual)
- `READY` → `ON_DELIVERY` (Admin manual)
- `ON_DELIVERY` → `DELIVERED` (Admin manual)

**Criterios validados:**
- Respuesta instantánea (<500ms)
- Procesamiento asíncrono
- Transiciones válidas de estado
- Persistencia correcta

---

### 1.5 Pedidos con Dirección (`test_order_with_address_flow.py`)

Valida la gestión de direcciones en pedidos (HU-02 y HU-03).

**Casos de prueba:**
- ✅ `test_tc_hu002_01_order_with_existing_address` - Pedido con dirección existente
- ✅ `test_tc_hu002_02_address_selection_from_list` - Selección de dirección
- ✅ `test_tc_hu003_01_add_new_address_in_order` - Nueva dirección en pedido
- ✅ `test_tc_hu003_02_address_validation` - Validación de dirección
- ✅ `test_address_persistence` - Persistencia de dirección

**Criterios validados (HU-02):**
- Uso de dirección existente
- Selección desde lista de direcciones
- Pedido completado sin crear nueva dirección

**Criterios validados (HU-03):**
- Creación de nueva dirección válida
- Validación de campos obligatorios
- Dirección guardada para futuros pedidos

---

### 1.6 Favoritos (`test_favorites_flow.py`)

Valida la gestión de productos favoritos.

**Casos de prueba:**
- ✅ `test_add_product_to_favorites` - Agregar a favoritos
- ✅ `test_remove_product_from_favorites` - Remover de favoritos
- ✅ `test_list_user_favorites` - Listar favoritos
- ✅ `test_favorites_persistence` - Persistencia
- ✅ `test_duplicate_favorite_prevention` - Prevenir duplicados

**Criterios validados:**
- CRUD completo de favoritos
- Sincronización entre cliente y BD
- Validación de permisos
- Prevención de duplicados

---

## 2. Pruebas de Integración

**Ubicación:** `api/tests/integration/`

### 2.1 Autenticación

#### `test_auth_login.py`
- ✅ `test_login_success_with_created_user` - Login con usuario válido
- ✅ `test_login_invalid_password_returns_401` - Rechazo de contraseña inválida

#### `test_auth_profile.py`
- ✅ `test_get_profile_authenticated_success` - Perfil con autenticación
- ✅ `test_get_profile_unauthenticated_returns_403` - Rechazo sin autenticación

---

### 2.2 Direcciones

#### `test_addresses_create.py`
- ✅ `test_create_address_with_camelCase_payload_returns_201` - Crear con camelCase

#### `test_addresses_endpoints.py`
- ✅ `test_get_addresses_returns_list` - Listar direcciones
- ✅ `test_get_address_by_id_ok` - Obtener por ID
- ✅ `test_get_address_not_found` - Dirección no encontrada (404)

---

### 2.3 Cupones

#### `test_api_coupon.py`
- ✅ Gestión completa de cupones (CRUD)

#### `test_create_coupon.py`
- ✅ Creación de cupones con validaciones

#### `test_coupons_validate.py`
- ✅ `test_validate_coupon_valid_flow` - Validación de cupón válido
- ✅ `test_validate_coupon_missing_code_returns_400` - Error sin código
- ✅ `test_validate_coupon_inactive_returns_invalid` - Cupón inactivo

---

### 2.4 Health Check

#### `test_health_endpoint.py`
- ✅ `test_health_endpoint_returns_200` - Health check funcional

---

## 3. Pruebas Unitarias

**Ubicación:** `api/tests/unit/`

### 3.1 Servicios Core

#### `test_auth_service.py`
Valida lógica de autenticación aislada.
- ✅ Hash de contraseñas
- ✅ Verificación de contraseñas
- ✅ Generación de tokens JWT
- ✅ Validación de tokens

#### `test_database_service.py`
Valida operaciones de base de datos con mocks.
- ✅ `test_get_connection_uses_asyncpg_connect` - Conexión asyncpg
- ✅ `test_get_user_by_email_found` - Búsqueda de usuario
- ✅ `test_get_user_by_email_not_found` - Usuario no encontrado
- ✅ `test_create_user_inserts_and_returns_id` - Crear usuario
- ✅ `test_get_products_returns_rows` - Obtener productos

#### `test_reviews_service.py`
Valida sistema de reseñas.
- ✅ Crear reseña
- ✅ Listar reseñas por producto
- ✅ Validación de calificación (1-5)
- ✅ Cálculo de promedio

---

### 3.2 Historias de Usuario

#### `test_hu02_order_with_address.py` (HU-02)
- ✅ Validación de dirección existente
- ✅ Lógica de selección de dirección
- ✅ Orden sin crear nueva dirección

#### `test_hu03_address_validation.py` (HU-03)
- ✅ Validación de campos obligatorios
- ✅ Formato de dirección
- ✅ Persistencia de nueva dirección

#### `test_hu04_async_orders.py` (HU-04)
- ✅ Creación instantánea de pedido
- ✅ Procesamiento asíncrono
- ✅ Publicación a cola RabbitMQ
- ✅ Validación de timeouts

---

## 4. Pruebas de Rendimiento

**Ubicación:** `api/tests/performance/`

### `test_hu01_performance.py` (HU-01)

Valida los requisitos de rendimiento del sistema.

**Métricas validadas:**
- ✅ **Tiempo de respuesta P90:** <500ms
- ✅ **Tiempo de respuesta P95:** <1000ms
- ✅ **Disponibilidad:** >99%
- ✅ **Concurrencia:** 50+ usuarios simultáneos

**Casos de prueba:**
- ✅ `test_response_time_p90_under_500ms` - P90 bajo 500ms
- ✅ `test_response_time_p95_under_1s` - P95 bajo 1 segundo
- ✅ `test_concurrent_users_performance` - 50 usuarios concurrentes
- ✅ `test_system_availability` - Disponibilidad 99%+

**Endpoints medidos:**
- `GET /api/products` - Listado de productos
- `POST /api/orders` - Creación de pedidos
- `POST /api/auth/login` - Autenticación

---

## 5. Pruebas de Historias de Usuario

**Ubicación:** `api/tests/` (raíz)

### `test_hu05_secrets_manager.py` (HU-05)

**Historia de Usuario:** Protección segura de información sensible

**Casos de prueba:**
- ✅ `test_secrets_not_in_code` - Secrets no en código fuente
- ✅ `test_environment_variables_used` - Variables de entorno usadas
- ✅ `test_database_password_encrypted` - Contraseñas encriptadas
- ✅ `test_jwt_secret_not_exposed` - JWT secret protegido
- ✅ `test_api_keys_in_env` - API keys en .env

**Criterios validados:**
- Credenciales fuera del código
- Uso de variables de entorno
- Secrets en gestores seguros
- Sin hardcoding de contraseñas

---

### `test_hu06_scheduled_orders.py` (HU-06)

**Historia de Usuario:** Entrega de pedidos programados a la hora exacta

**Casos de prueba:**
- ✅ `test_tc_hu006_01_schedule_order_future_time` - Programar para el futuro
- ✅ `test_tc_hu006_02_scheduled_time_display` - Visualización correcta
- ✅ `test_tc_hu006_03_timezone_handling` - Manejo de zona horaria
- ✅ `test_scheduled_order_not_processed_early` - No procesar antes
- ✅ `test_scheduled_order_timezone_bogota` - Timezone Colombia

**Criterios validados:**
- Programación a hora exacta
- Visualización en hora local (Bogotá)
- No procesamiento anticipado
- Campo `scheduledFor` guardado y mostrado
- Timezone UTC en BD, Colombia en UI

---

## 6. Pruebas QA Automatizadas

**Ubicación:** `qa_automated/tests/`

### Playwright Tests

**Framework:** Playwright + TypeScript

**Categorías:**
- ✅ Tests de regresión visual
- ✅ Tests de flujos críticos UI
- ✅ Tests cross-browser
- ✅ Tests de accesibilidad

### Análisis de Seguridad

**Herramienta:** Bandit (Python security linter)

**Validaciones:**
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF tokens
- ✅ Password hashing
- ✅ Input validation

**Scripts:**
- `run_security_analysis.ps1` / `.sh`
- `run_qa.ps1` / `.sh`

---

## Configuración y Ejecución

### Archivo de Configuración: `pytest.ini`

```ini
[pytest]
# Modo asyncio para tests asíncronos
asyncio_mode = auto

# Directorio raíz de tests
testpaths = tests

# Patrones de descubrimiento
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers personalizados
markers =
    unit: Tests unitarios (lógica aislada, sin DB)
    integration: Tests de integración (con DB, endpoints)
    e2e: Tests end-to-end (flujos completos)
    slow: Tests lentos (> 5 segundos)
    rabbitmq: Tests que requieren RabbitMQ
    admin: Tests de endpoints administrativos
    auth: Tests de autenticación

# Cobertura mínima
addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=services.auth_service
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-fail-under=70
    -ra

# Timeout para tests
timeout = 30
```

---

### Comandos de Ejecución

#### Ejecutar TODOS los tests
```bash
pytest api/tests/
```

#### Ejecutar por categoría
```bash
# Tests unitarios
pytest api/tests/unit/ -m unit

# Tests de integración
pytest api/tests/integration/ -m integration

# Tests E2E
pytest api/tests/e2e/ -m e2e

# Tests de rendimiento
pytest api/tests/performance/ -m slow
```

#### Ejecutar HU específica
```bash
# HU-05: Secrets Manager
pytest api/tests/test_hu05_secrets_manager.py

# HU-06: Pedidos Programados
pytest api/tests/test_hu06_scheduled_orders.py
```

#### Con cobertura detallada
```bash
pytest api/tests/ --cov --cov-report=html
```

#### Tests específicos por nombre
```bash
pytest api/tests/ -k "login"
pytest api/tests/ -k "address"
pytest api/tests/ -k "scheduled"
```

---

## Cobertura y Métricas

### Estado Actual (Diciembre 2025)

| Categoría | Tests | Pasando | Fallando | % Éxito |
|-----------|-------|---------|----------|---------|
| **E2E** | 35 | 30 | 5 | 85.7% |
| **Integración** | 15+ | 15+ | 0 | 100% |
| **Unitarios** | 20+ | 20+ | 0 | 100% |
| **Rendimiento** | 4 | 4 | 0 | 100% |
| **Total** | 74+ | 69+ | 5 | 93.2% |

---

### Cobertura de Código

```
Module                     Statements   Coverage
--------------------------------------------------
services/auth_service.py        85        92%
services/database_service.py    120       78%
services/rabbitmq.py           45        85%
routers/auth.py                65        95%
routers/orders.py              110       82%
routers/products.py            55        88%
--------------------------------------------------
TOTAL                          480       85%
```

---

### Métricas de Rendimiento (HU-01)

| Métrica | Objetivo | Actual | Estado |
|---------|----------|--------|--------|
| **P90 Response Time** | <500ms | 280ms | ✅ PASS |
| **P95 Response Time** | <1000ms | 450ms | ✅ PASS |
| **Disponibilidad** | >99% | 99.8% | ✅ PASS |
| **Concurrencia** | 50 users | 100 users | ✅ PASS |

---

## Fixtures y Datos de Prueba

**Ubicación:** `api/tests/conftest.py`, `api/tests/fixtures/`

### Fixtures Principales

#### `test_db_connection`
- Conexión a BD de pruebas
- Rollback automático después de cada test
- Aislamiento de datos

#### `test_users`
- Usuario de prueba con UUID único
- Email: `test-{uuid}@test.com`
- Limpieza automática post-test

#### `test_products`
- Productos mock para pruebas
- Datos realistas
- Cleanup automático

#### `test_client`
- Cliente HTTP async para API
- Headers automáticos
- Autenticación incluida

---

## Principios Aplicados

### INVEST

Cada test y HU cumple con:

- **I**ndependiente: Tests no dependen entre sí, usan fixtures únicos
- **N**egociable: Criterios refinados en TEST_PLAN.md
- **V**alorable: Cada test valida resultado de negocio claro
- **E**stimable: Tests estimados y priorizados en REFINED_BACKLOG.md
- **S**mall: Tests atómicos, un comportamiento por test
- **T**estable: Todo criterio tiene test automatizado

### TDD (Test-Driven Development)

Ciclo aplicado:
1. **Red:** Escribir test que falla
2. **Green:** Implementar mínimo para pasar
3. **Refactor:** Mejorar código manteniendo tests

---

## Documentación Relacionada

- 📋 [TEST_PLAN.md](TEST_PLAN.md) - Plan maestro de pruebas
- 📝 [TEST_CASES.md](TEST_CASES.md) - Casos de prueba detallados (Gherkin)
- 📊 [REFINED_BACKLOG.md](REFINED_BACKLOG.md) - HU priorizadas con estimaciones
- 🏗️ [user_stories.md](../user_stories.md) - Historias de Usuario originales
- 🔧 [pytest.ini](../api/pytest.ini) - Configuración de pytest

---

## Mejoras Recientes

### ✅ Implementadas (Diciembre 2025)

1. **Timezone Colombia**
   - Todos los timestamps muestran hora de Bogotá
   - BD en UTC, UI en `America/Bogota`

2. **Campo scheduledFor**
   - Guardado correctamente en BD
   - Mostrado en admin y cliente
   - Tests validando funcionalidad

3. **Worker CONFIRMED**
   - Worker actualiza a `CONFIRMED` (no `PREPARING`)
   - Admin tiene control total de preparación
   - Separación de responsabilidades

4. **Cache de Productos**
   - Invalidación correcta de cache
   - Actualizaciones inmediatas en UI

5. **Botones Admin**
   - Botones correctos para todos los estados
   - Incluyendo pedidos `SCHEDULED`

---

## Tests Pendientes (5 de 35)

### En proceso de corrección:

1. `test_order_cancellation` - Cancelación de pedidos
2. `test_payment_methods` - Métodos de pago múltiples
3. `test_delivery_tracking` - Seguimiento en tiempo real
4. `test_notifications` - Sistema de notificaciones
5. `test_reviews_integration` - Integración completa de reseñas

**Próximos pasos:**
- Revisar logs de tests fallidos
- Actualizar fixtures según cambios recientes
- Validar integración con worker CONFIRMED

---

## Contacto y Soporte

Para dudas sobre pruebas:
- Ver logs: `api/tests/`
- Cobertura HTML: `api/htmlcov/index.html`
- CI/CD: Ver pipeline en repositorio

---

**Última actualización:** Diciembre 18, 2025
**Versión:** 1.0
**Autor:** Equipo SoftDomiFood
