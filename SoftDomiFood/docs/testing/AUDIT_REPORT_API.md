# 📋 Reporte de Auditoría de Código - SoftDomiFood API

**Proyecto:** SoftDomiFood Backend API  
**Tecnología:** FastAPI + Python 3.11+, PostgreSQL, RabbitMQ  
**Fecha de Auditoría:** 2 de diciembre de 2025  
**Auditor:** GitHub Copilot (AI Agent)

---

## 📑 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis de Principios SOLID](#análisis-de-principios-solid)
3. [Patrones de Diseño](#patrones-de-diseño)
4. [Evaluación de Implementaciones](#evaluación-de-implementaciones)
5. [Estrategia de Pruebas (QA - Principios FIRST)](#estrategia-de-pruebas-qa---principios-first)
6. [Recomendaciones Prioritarias](#recomendaciones-prioritarias)
7. [Plan de Acción](#plan-de-acción)

---

## 1. Resumen Ejecutivo

### Arquitectura General
El proyecto implementa un **API Producer** basado en FastAPI que:
- Expone endpoints REST para autenticación, productos, pedidos, direcciones, cupones y administración
- Se conecta a PostgreSQL usando `asyncpg` para operaciones asíncronas
- Publica mensajes de órdenes a RabbitMQ para procesamiento asíncrono por un worker
- Implementa autenticación JWT con roles (CUSTOMER, ADMIN, DELIVERY)

### Estado General del Código

| Aspecto | Calificación | Observación |
|---------|--------------|-------------|
| **Estructura** | 🟡 Aceptable | Separación básica de concerns (routers, services), pero mejorable |
| **SOLID** | 🔴 Necesita mejora | Violaciones importantes de SRP y DIP |
| **Patrones** | 🟡 Parcial | Algunos patrones emergentes, falta formalización |
| **Manejo de Errores** | 🟢 Bueno | try-except consistente, HTTPException apropiado |
| **Seguridad** | 🟡 Aceptable | JWT implementado, pero secrets en código |
| **Calidad de Código** | 🟢 Bueno | Código legible, comentarios útiles |
| **Testing** | 🔴 Inexistente | No hay pruebas unitarias ni de integración |

---

## 2. Análisis de Principios SOLID

### 2.1. Single Responsibility Principle (SRP) - **🔴 VIOLADO**

#### ❌ Violaciones Identificadas

**1. `database_service.py` - Responsabilidad Excesiva**
- **Líneas:** 1-700+ (todo el archivo)
- **Problema:** Este módulo realiza TODAS las operaciones de base de datos para TODAS las entidades (usuarios, productos, órdenes, cupones, direcciones). Mezcla lógica de negocio, conversión de datos y acceso a BD.
- **Impacto:** 
  - Archivo de ~700 líneas difícil de mantener
  - Cambios en una entidad pueden afectar otras
  - Dificulta el testing unitario
  - Violación clara de cohesión

**Ejemplo concreto:**
```python
# database_service.py maneja:
async def get_products(...)  # Productos
async def create_order(...)  # Órdenes
async def get_user_by_email(...)  # Usuarios
async def create_coupon(...)  # Cupones
async def get_user_addresses(...)  # Direcciones
async def validate_coupon_for_user(...)  # Lógica de negocio de cupones
```

**2. `orders.py` (router) - Mezcla de Responsabilidades**
- **Líneas:** 40-120 en `create_new_order`
- **Problema:** El endpoint de creación de pedidos contiene:
  - Validación de entrada
  - Lógica de negocio (cálculo de totales, aplicación de cupones)
  - Orquestación de servicios (DB + RabbitMQ)
  - Manejo de errores
- **Impacto:** Función de 80+ líneas con múltiples responsabilidades

**Ejemplo:**
```python
@router.post("/")
async def create_new_order(...):
    # Validación de auth
    if not current_user or not current_user.get("userId"):
        ...
    # Validación de items
    if not order_data.items or len(order_data.items) == 0:
        ...
    # Lógica de negocio: cálculo de precios
    for item in order_data.items:
        product = await get_product_by_id(item.productId)
        item_price = item.price if item.price is not None else product.get("price", 0)
        calculated_total += item_total
    # Lógica de negocio: aplicación de cupones
    if order_data.couponCode:
        validation = await validate_coupon_for_user(...)
        if coupon.get("discount_type") == "PERCENTAGE":
            discount_applied = round(final_total * (pct/100.0), 2)
    # Persistencia
    order = await create_order(...)
    # Mensajería
    await publish_order(order)
```

**3. `main.py` - Configuración + Lógica de Startup**
- **Líneas:** 15-60 (función `lifespan`)
- **Problema:** Mezcla inicialización de BD, RabbitMQ, creación de admin, manejo de errores y logs
- **Impacto:** Dificulta testing de startup, acoplamiento alto

#### ✅ Recomendaciones SRP

1. **Refactorizar `database_service.py`:**
   ```
   services/
     ├── repositories/
     │   ├── user_repository.py
     │   ├── product_repository.py
     │   ├── order_repository.py
     │   ├── coupon_repository.py
     │   └── address_repository.py
     ├── business/
     │   ├── order_service.py  # Lógica de negocio de órdenes
     │   ├── coupon_service.py  # Validación y aplicación de cupones
     │   └── pricing_service.py  # Cálculo de precios y descuentos
   ```

2. **Separar lógica de negocio de routers:**
   - Crear `OrderService` que encapsule validación + cálculo + persistencia
   - Router solo debe orquestar y manejar HTTP

3. **Extraer inicialización:**
   - `services/startup_service.py` con responsabilidad única de startup

---

### 2.2. Open/Closed Principle (OCP) - **🟡 PARCIALMENTE VIOLADO**

#### ❌ Violaciones

**1. Sistema de Descuentos de Cupones - Lógica Hardcoded**
- **Archivo:** `orders.py`, líneas 73-80
- **Problema:** Lógica de descuento directamente codificada con if/elif
```python
if coupon.get("discount_type") == "PERCENTAGE":
    pct = float(coupon.get("percentage", 0))
    discount_applied = round(final_total * (pct/100.0), 2)
elif coupon.get("discount_type") == "AMOUNT":
    discount_applied = float(coupon.get("amount", 0))
```
- **Impacto:** Agregar un nuevo tipo de descuento (ej: "BUY_ONE_GET_ONE", "FREE_SHIPPING") requiere modificar código existente

#### ✅ Implementación Acertada

**Uso de Enums para Categorías y Estados:**
- **Archivo:** `models.py`
```python
class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    ...
```
- **Ventaja:** Fácil extensión sin modificar lógica existente (se agregan valores al enum)

#### 🔧 Recomendaciones OCP

**1. Implementar Strategy Pattern para Descuentos:**
```python
# services/business/discount_strategies.py
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, total: float, coupon: dict) -> float:
        pass

class PercentageDiscount(DiscountStrategy):
    def calculate(self, total: float, coupon: dict) -> float:
        pct = float(coupon.get("percentage", 0))
        return round(total * (pct / 100.0), 2)

class AmountDiscount(DiscountStrategy):
    def calculate(self, total: float, coupon: dict) -> float:
        return float(coupon.get("amount", 0))

class DiscountFactory:
    _strategies = {
        "PERCENTAGE": PercentageDiscount(),
        "AMOUNT": AmountDiscount()
    }
    
    @classmethod
    def get_strategy(cls, discount_type: str) -> DiscountStrategy:
        return cls._strategies.get(discount_type)
```

---

### 2.3. Liskov Substitution Principle (LSP) - **🟢 NO VIOLADO**

#### ✅ Estado Actual
- No hay jerarquías de herencia complejas en el código actual
- El uso de Pydantic BaseModel para validación respeta LSP
- Enums son usados correctamente sin jerarquías problemáticas

#### ⚠️ Punto de Atención Futuro
Si se implementan estrategias de descuento o repositorios con herencia, asegurar que las subclases no cambien el contrato esperado.

---

### 2.4. Interface Segregation Principle (ISP) - **🟢 ACEPTABLE**

#### ✅ Puntos Positivos
- Routers separados por dominio (`auth`, `products`, `orders`, `admin`)
- Cada router expone solo endpoints relevantes a su dominio
- Pydantic models específicos por endpoint (no se reutilizan modelos genéricos innecesariamente)

#### 🟡 Área de Mejora
**`database_service.py` como "God Interface":**
- Módulo importa TODO el servicio aunque solo se necesiten 1-2 funciones
- Recomendación: Separar en repositorios específicos para importar solo lo necesario

---

### 2.5. Dependency Inversion Principle (DIP) - **🔴 VIOLADO**

#### ❌ Violaciones Críticas

**1. Acoplamiento Directo a `asyncpg` en Toda la Aplicación**
- **Archivos:** `database_service.py`, `init_db.py`
- **Problema:** Todos los servicios dependen directamente de implementación concreta de `asyncpg`
```python
async def get_connection():
    return await asyncpg.connect(DATABASE_URL)  # Dependencia concreta
```
- **Impacto:**
  - Imposible cambiar de motor de BD sin reescribir todo
  - Dificulta testing (no se puede mockear fácilmente)
  - No hay abstracción de repositorio

**2. Acoplamiento a `aio_pika` en `rabbitmq.py`**
- Similar al punto anterior, servicios dependen directamente de librería específica
- No hay interfaz abstracta para mensajería

**3. `routers` importan directamente `services.database_service`**
```python
from services.database_service import create_order, get_product_by_id
```
- Routers dependen de módulos concretos, no de abstracciones/interfaces

#### 🔧 Recomendaciones DIP

**1. Introducir Abstracciones (Dependency Injection):**
```python
# repositories/base.py
from abc import ABC, abstractmethod

class IOrderRepository(ABC):
    @abstractmethod
    async def create(self, order_data: dict) -> dict:
        pass
    
    @abstractmethod
    async def get_by_id(self, order_id: str) -> dict:
        pass

# repositories/postgres/order_repository.py
class PostgresOrderRepository(IOrderRepository):
    def __init__(self, db_connection):
        self._conn = db_connection
    
    async def create(self, order_data: dict) -> dict:
        # Implementación con asyncpg
        pass

# routers/orders.py (con DI)
def get_order_repo() -> IOrderRepository:
    return PostgresOrderRepository(get_connection())

@router.post("/")
async def create_order(
    order_data: CreateOrderRequest,
    repo: IOrderRepository = Depends(get_order_repo)
):
    order = await repo.create(order_data)
```

**2. Usar Factory Pattern para Mensajería:**
```python
class IMessageBroker(ABC):
    @abstractmethod
    async def publish(self, queue: str, message: dict):
        pass

class RabbitMQBroker(IMessageBroker):
    async def publish(self, queue: str, message: dict):
        # Implementación con aio_pika
        pass
```

---

## 3. Patrones de Diseño

### 3.1. Patrones Actualmente Implementados (Emergentes)

#### ✅ **Patrón Singleton (Implícito) - RabbitMQ Connection**
- **Archivo:** `services/rabbitmq.py`
- **Implementación:**
```python
_connection: Optional[aio_pika.RobustConnection] = None
_channel: Optional[aio_pika.RobustChannel] = None

async def get_connection() -> aio_pika.RobustConnection:
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(RABBITMQ_URL)
    return _connection
```
- **Evaluación:** ✅ **ACERTADO**
  - Evita múltiples conexiones a RabbitMQ
  - Manejo de reconexión automática con `connect_robust`
- **Mejora:** Convertir en Singleton formal con clase y threading.Lock para thread-safety

#### 🟡 **Patrón Repository (Parcial) - `database_service.py`**
- **Evaluación:** **PARCIALMENTE IMPLEMENTADO**
  - Funciones como `get_products()`, `create_order()` actúan como repositorio
  - **Problema:** No hay interfaz abstracta, todo en un solo archivo (viola SRP)
- **Recomendación:** Formalizar con clases Repository por entidad

#### ✅ **Patrón Dependency Injection - FastAPI Depends**
- **Archivo:** `routers/auth.py`, `routers/orders.py`
```python
@router.get("/")
async def get_orders(current_user: dict = Depends(get_current_user)):
```
- **Evaluación:** ✅ **ACERTADO**
  - Uso correcto de FastAPI `Depends()` para inyección
  - Facilita testing (se pueden mockear dependencias)

#### ✅ **Patrón Factory (Implícito) - Password Hashing**
- **Archivo:** `services/auth_service.py`
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```
- **Evaluación:** ✅ **ACERTADO**
  - `CryptContext` actúa como factory para algoritmos de hash
  - Permite cambiar algoritmo sin cambiar código

---

### 3.2. Patrones Recomendados (No Implementados)

#### 🔧 **1. Strategy Pattern - Descuentos de Cupones**
- **Ubicación:** `services/business/discount_strategies.py`
- **Justificación:** 
  - Actualmente lógica de descuento hardcoded en `orders.py`
  - Necesario para agregar nuevos tipos sin modificar código existente (OCP)
- **Beneficios:**
  - Extensibilidad: Nuevos tipos de descuento = nueva clase Strategy
  - Testing: Cada estrategia se testea independientemente
  - Claridad: Lógica de negocio separada y formalizada

#### 🔧 **2. Factory Pattern - Creación de Órdenes**
- **Ubicación:** `services/business/order_factory.py`
- **Propósito:** Centralizar lógica de creación de órdenes con diferentes estados/tipos
```python
class OrderFactory:
    @staticmethod
    def create_standard_order(data: OrderData) -> Order:
        # Orden estándar con validaciones básicas
        pass
    
    @staticmethod
    def create_admin_order(data: OrderData) -> Order:
        # Orden creada por admin (puede omitir validaciones)
        pass
```

#### 🔧 **3. Observer Pattern - Notificaciones de Órdenes**
- **Ubicación:** `services/events/order_events.py`
- **Justificación:** Actualmente solo se publica a RabbitMQ, pero podrían agregarse:
  - Envío de email
  - Notificación push
  - Actualización de analytics
- **Implementación:**
```python
class OrderObserver(ABC):
    @abstractmethod
    async def on_order_created(self, order: dict):
        pass

class RabbitMQNotifier(OrderObserver):
    async def on_order_created(self, order: dict):
        await publish_order(order)

class EmailNotifier(OrderObserver):
    async def on_order_created(self, order: dict):
        await send_email(order)

class OrderEventManager:
    def __init__(self):
        self._observers = []
    
    def subscribe(self, observer: OrderObserver):
        self._observers.append(observer)
    
    async def notify_order_created(self, order: dict):
        for obs in self._observers:
            await obs.on_order_created(order)
```

#### 🔧 **4. Builder Pattern - Construcción de Queries Complejas**
- **Ubicación:** `repositories/query_builder.py`
- **Justificación:** Queries en `database_service.py` construyen SQL dinámicamente con string concat
```python
# Actual (en get_products)
query = "SELECT ... WHERE 1=1"
if category:
    query += " AND category = $1"
```
- **Propuesta:**
```python
class OrderQueryBuilder:
    def __init__(self):
        self._filters = []
        self._params = []
    
    def filter_by_user(self, user_id: str):
        self._filters.append('"userId" = $' + str(len(self._params) + 1))
        self._params.append(user_id)
        return self
    
    def filter_by_status(self, status: str):
        self._filters.append('status = $' + str(len(self._params) + 1))
        self._params.append(status)
        return self
    
    def build(self) -> tuple[str, list]:
        base = "SELECT * FROM orders WHERE "
        where = " AND ".join(self._filters) if self._filters else "1=1"
        return (base + where, self._params)
```

---

## 4. Evaluación de Implementaciones

### 4.1. ✅ Implementaciones Acertadas (Buenas Prácticas)

#### **1. Manejo de Errores Consistente**
- **Archivos:** Todos los routers
- **Patrón:**
```python
try:
    # Lógica
    pass
except HTTPException:
    raise  # Re-lanzar excepciones HTTP sin modificar
except Exception as e:
    import traceback
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```
- **Fortalezas:**
  - Diferencia entre errores esperados (HTTPException) y no esperados
  - Logs de traceback para debugging
  - Mensajes de error informativos

#### **2. Validación de Entrada con Pydantic**
- **Ejemplo:** `routers/admin.py`
```python
class CreateCouponRequest(BaseModel):
    code: str
    discountType: str
    amount: Optional[float] = None
    percentage: Optional[float] = None
    ...
```
- **Fortalezas:**
  - Validación automática de tipos
  - Documentación auto-generada en /docs
  - Previene inyección de datos maliciosos

#### **3. Autenticación JWT con Roles**
- **Archivo:** `services/auth_service.py` + `routers/auth.py`
- **Fortalezas:**
  - Tokens con expiración (7 días)
  - Payload incluye userId y role para autorización
  - Middleware de autenticación reutilizable (`get_current_user`)

#### **4. Conexiones Persistentes a RabbitMQ**
- **Archivo:** `services/rabbitmq.py`
- **Fortalezas:**
  - Uso de `connect_robust` para auto-reconexión
  - Manejo de conexión cerrada con fallback
  - Serialización correcta de UUID/datetime a JSON

#### **5. Conversión de UUIDs y Fechas**
- **Función:** `convert_uuid_to_str()` en `database_service.py`
- **Fortalezas:**
  - Evita errores de serialización JSON
  - Manejo recursivo de dicts y listas

#### **6. Uso de Async/Await Consistente**
- **Fortalezas:**
  - Todo el código usa asyncio correctamente
  - `asyncpg` para I/O no bloqueante
  - Mejora significativa de performance vs sync

#### **7. Índices en Base de Datos**
- **Archivo:** `init_db.py`
```sql
CREATE INDEX IF NOT EXISTS idx_users_email ON "users"(email);
CREATE INDEX IF NOT EXISTS idx_orders_status ON "orders"(status);
```
- **Fortalezas:**
  - Optimización de queries frecuentes
  - Uso de `IF NOT EXISTS` para idempotencia

---

### 4.2. ❌ Implementaciones Fallidas o Problemáticas

#### **1. Secrets Hardcodeados en Código**
- **Archivo:** `services/auth_service.py`, línea 10
```python
SECRET_KEY = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
```
- **Problema:** 
  - Secret por defecto INSEGURO en producción
  - Si no se configura env var, queda expuesto
- **Riesgo:** 🔴 **CRÍTICO - SEGURIDAD**
- **Solución:**
```python
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET environment variable must be set")
```

#### **2. Falta de Rate Limiting**
- **Endpoints afectados:** Todos (especialmente `/api/auth/login`)
- **Problema:** No hay protección contra brute force o DDoS
- **Riesgo:** 🔴 **ALTO - SEGURIDAD**
- **Solución:** Implementar `slowapi` o middleware custom:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(...):
```

#### **3. Autenticación Deshabilitada Temporalmente en Cupones**
- **Archivo:** `routers/admin.py`, líneas 160-250
```python
@router.get("/coupons")
async def admin_list_coupons():  # SIN get_current_user
    """Listar cupones (sin autenticación temporal para pruebas)"""
```
- **Problema:** 
  - Endpoints admin expuestos sin autenticación
  - Comentario indica "temporal" pero puede olvidarse
- **Riesgo:** 🔴 **CRÍTICO - SEGURIDAD**
- **Solución:** Reactivar autenticación INMEDIATAMENTE:
```python
@router.get("/coupons")
async def admin_list_coupons(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
```

#### **4. Falta de Validación de Ownership en Direcciones**
- **Archivo:** `routers/addresses.py`, `get_address` (parcial)
- **Problema:** Solo valida ownership en GET pero no en DELETE/UPDATE (no existen)
- **Riesgo:** 🟡 **MEDIO - SEGURIDAD**
- **Solución:** Implementar DELETE/UPDATE con validación de userId

#### **5. SQL Injection Potential (Bajo riesgo con asyncpg)**
- **Archivo:** `database_service.py`
- **Observación:** 
  - Uso correcto de parámetros ($1, $2) en la mayoría de queries
  - asyncpg previene SQL injection por diseño
- **Punto de Mejora:** En `update_coupon`, construcción dinámica de query:
```python
set_clause = ", ".join(set_parts) + ", \"updatedAt\" = NOW()"
query = f"UPDATE coupons SET {set_clause} WHERE id = ${idx} ..."
```
- **Riesgo:** 🟡 **BAJO** (keys validados, pero podría mejorarse)
- **Solución:** Usar query builder o ORM (SQLAlchemy)

#### **6. Falta de Logging Estructurado**
- **Problema:** Solo prints a stdout, no hay niveles de log ni rotación
```python
print("✅ Usuario admin creado exitosamente")
print(f"⚠️  Error al crear usuario admin: {e}")
```
- **Riesgo:** 🟡 **BAJO - OPERACIONAL**
- **Impacto:** Dificulta debugging en producción
- **Solución:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Usuario admin creado exitosamente")
logger.error(f"Error al crear usuario admin: {e}", exc_info=True)
```

#### **7. Falta de Validación de Business Rules**
- **Ejemplo:** `create_order` permite cantidad negativa si se pasa directamente
- **Archivo:** `routers/orders.py`, línea 50
```python
if item.quantity <= 0:
    raise HTTPException(status_code=422, detail="...")
```
- **Problema:** Validación solo en router, no en capa de servicio/negocio
- **Riesgo:** 🟡 **MEDIO** (si se llama desde otro lugar)
- **Solución:** Mover validaciones a `OrderService`

#### **8. Falta de Transacciones en Operaciones Complejas**
- **Ejemplo:** `create_order` usa transacción ✅, pero `register_coupon_usage` es llamada FUERA de la transacción
- **Archivo:** `routers/orders.py`, líneas 90-95
```python
order = await create_order(...)  # Dentro de transacción
# ...
await register_coupon_usage(...)  # FUERA de transacción
```
- **Riesgo:** 🔴 **ALTO - CONSISTENCIA**
- **Problema:** Si `register_coupon_usage` falla, la orden ya está creada → inconsistencia
- **Solución:** Incluir registro de uso dentro de la transacción de `create_order`

#### **9. Falta de Paginación en Listados**
- **Endpoints:** `/api/products`, `/api/admin/orders`, `/api/admin/customers`
- **Problema:** Devuelven TODOS los registros sin límite
- **Riesgo:** 🟡 **MEDIO - PERFORMANCE**
- **Impacto:** Con miles de órdenes, response puede ser de MB
- **Solución:**
```python
@router.get("/")
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100)
):
    query += f" LIMIT ${len(params)+1} OFFSET ${len(params)+2}"
    params.extend([limit, skip])
```

#### **10. Manejo de Errores de RabbitMQ Silencioso**
- **Archivo:** `routers/orders.py`, líneas 100-105
```python
try:
    await publish_order(order)
except Exception as mq_error:
    print(f"⚠️  Error publicando a RabbitMQ: {mq_error}")
    # Continúa sin fallar → orden creada pero no procesada
```
- **Problema:** 
  - Orden queda en BD pero nunca se procesa
  - Usuario recibe éxito aunque el pedido no llegue al worker
- **Riesgo:** 🔴 **ALTO - FUNCIONAL**
- **Solución:** 
  - Opción 1: Fallar la creación de orden si RabbitMQ no disponible
  - Opción 2: Implementar retry automático o dead letter queue
  - Opción 3: Marcar orden con estado "PENDING_NOTIFICATION" y tener job de reconciliación

---

## 5. Estrategia de Pruebas (QA - Principios FIRST)

### 5.1. Análisis del Estado Actual
**🔴 CRÍTICO:** El proyecto NO tiene ninguna suite de pruebas automatizadas.

### 5.2. Estrategia Propuesta siguiendo Principios FIRST

#### **F - Fast (Rápidas)**

**Objetivo:** Suite de pruebas que ejecute en < 30 segundos

**Implementación:**

1. **Pruebas Unitarias (< 10s total):**
   - Mock de dependencias externas (DB, RabbitMQ)
   - Testing de lógica de negocio aislada
   
2. **Pruebas de Integración (10-20s):**
   - Usar PostgreSQL en memoria o Docker con volumen temporal
   - Conexión real a DB de pruebas, no producción

3. **Optimizaciones:**
   - `pytest-xdist` para ejecución paralela
   - Fixtures reutilizables con scope="session" para DB setup

**Ejemplo:**
```python
# tests/conftest.py
@pytest.fixture(scope="session")
async def test_db():
    """DB de pruebas creada una vez por sesión"""
    conn = await asyncpg.connect(TEST_DATABASE_URL)
    await init_database()
    yield conn
    await conn.close()
```

---

#### **I - Isolated (Aisladas/Independientes)**

**Objetivo:** Cada test puede ejecutarse en cualquier orden sin afectar otros

**Implementación:**

1. **Aislamiento de Base de Datos:**
   - Cada test ejecuta en transacción que se hace rollback al final
   ```python
   @pytest.fixture
   async def isolated_db(test_db):
       async with test_db.transaction():
           yield test_db
           raise Exception("Rollback")  # Forzar rollback
   ```

2. **Mock de Estado Global:**
   - Mock de `_connection`, `_channel` en `rabbitmq.py`
   ```python
   @pytest.fixture
   def mock_rabbitmq(monkeypatch):
       async def mock_publish(order_data):
           return True
       monkeypatch.setattr("services.rabbitmq.publish_order", mock_publish)
   ```

3. **Limpieza de Side Effects:**
   - No modificar variables de entorno globalmente
   - Usar `monkeypatch` de pytest para env vars temporales

---

#### **R - Repeatable (Repetibles en cualquier entorno)**

**Objetivo:** Tests pasan en local, CI/CD, y máquina de cualquier dev

**Implementación:**

1. **Datos de Prueba Determinísticos:**
   ```python
   # tests/fixtures/data.py
   SAMPLE_USER = {
       "email": "test@example.com",
       "password": "Test123!",
       "name": "Test User"
   }
   
   SAMPLE_PRODUCT = {
       "name": "Salchipapa Básica",
       "price": 15000.0,
       "category": "SALCHIPAPAS"
   }
   ```

2. **Configuración via ENV:**
   ```python
   # tests/.env.test
   DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_db
   RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   JWT_SECRET=test-secret-key-only-for-testing
   ```

3. **Docker Compose para Servicios:**
   ```yaml
   # docker-compose.test.yml
   services:
     postgres-test:
       image: postgres:15
       environment:
         POSTGRES_DB: test_db
         POSTGRES_USER: test_user
         POSTGRES_PASSWORD: test_pass
       ports:
         - "5433:5432"
     rabbitmq-test:
       image: rabbitmq:3-management
       ports:
         - "5673:5672"
   ```

4. **Seed Data Automatizado:**
   - Script `tests/seed_test_data.py` que corre antes de tests

---

#### **S - Self-validating (Auto-validables)**

**Objetivo:** Tests pasan/fallan automáticamente sin revisión manual

**Implementación:**

1. **Aserciones Claras:**
   ```python
   # ❌ MAL: Requiere inspección manual
   def test_create_order():
       order = await create_order(...)
       print(order)  # Requiere ver logs

   # ✅ BIEN: Pasa o falla automáticamente
   def test_create_order():
       order = await create_order(...)
       assert order["status"] == "PENDING"
       assert order["total"] == 30000.0
       assert len(order["items"]) == 2
   ```

2. **Validación de Estructura Completa:**
   ```python
   from pydantic import BaseModel
   
   class OrderResponse(BaseModel):
       id: str
       userId: str
       status: str
       total: float
       items: list
   
   def test_order_structure():
       order = await create_order(...)
       validated = OrderResponse(**order)  # Falla si estructura incorrecta
   ```

3. **Aserciones de Mensajes de Error:**
   ```python
   def test_invalid_coupon():
       with pytest.raises(HTTPException) as exc:
           await validate_coupon("INVALID123", user_id)
       assert exc.value.status_code == 400
       assert "no existe" in exc.value.detail
   ```

---

#### **T - Timely (Oportunas)**

**Objetivo:** Escribir tests ANTES o DURANTE desarrollo, no después

**Implementación:**

1. **TDD Workflow:**
   - Escribir test de feature antes de implementar
   - Implementar hasta que test pase
   - Refactorizar manteniendo tests verdes

2. **Tests en PR Review:**
   - CI/CD bloquea merge si tests fallan
   - Coverage mínimo del 70% para aprobar PR

3. **Pre-commit Hooks:**
   ```yaml
   # .pre-commit-config.yaml
   - repo: local
     hooks:
       - id: pytest
         name: Run pytest
         entry: pytest
         language: system
         pass_filenames: false
         always_run: true
   ```

---

### 5.3. Tipos de Pruebas Propuestas

#### **5.3.1. Pruebas Unitarias - Lógica de Negocio**

**Scope:** Testing de funciones individuales sin dependencias externas

**Archivos a testear:**
- `services/auth_service.py`: `verify_password`, `create_access_token`, `decode_token`
- Futura `services/business/coupon_service.py`: `validate_coupon`, `apply_discount`
- Futura `services/business/pricing_service.py`: `calculate_order_total`

**Ejemplo:**
```python
# tests/unit/test_auth_service.py
import pytest
from services.auth_service import verify_password, get_password_hash, create_access_token, decode_token

def test_password_hashing():
    """Verificar que hash y verificación funcionan"""
    password = "MySecurePass123!"
    hashed = get_password_hash(password)
    
    assert hashed != password  # Hash no debe ser texto plano
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPass", hashed) is False

def test_jwt_token_creation_and_decode():
    """Verificar creación y decodificación de JWT"""
    payload = {"userId": "123", "role": "CUSTOMER"}
    token = create_access_token(payload)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_token(token)
    assert decoded["userId"] == "123"
    assert decoded["role"] == "CUSTOMER"
    assert "exp" in decoded  # Debe incluir expiración

def test_invalid_token_returns_none():
    """Token inválido debe retornar None"""
    invalid_token = "this-is-not-a-valid-jwt"
    decoded = decode_token(invalid_token)
    assert decoded is None
```

**Justificación FIRST:**
- **F:** Ejecuta en milisegundos (no hay I/O)
- **I:** No depende de DB ni otros tests
- **R:** Siempre produce mismo resultado
- **S:** Assert claro de pass/fail
- **T:** Se escribe al desarrollar auth

---

#### **5.3.2. Pruebas de Integración - API + DB**

**Scope:** Testing de endpoints completos con BD real (test DB)

**Archivos a testear:**
- `routers/auth.py`: `/register`, `/login`, `/profile`
- `routers/products.py`: GET `/products`
- `routers/orders.py`: POST `/orders`
- `routers/admin.py`: POST `/admin/coupons`, GET `/admin/orders`

**Ejemplo:**
```python
# tests/integration/test_order_flow.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture
async def auth_headers(test_client):
    """Fixture que retorna headers de autenticación"""
    # Crear usuario de prueba
    response = await test_client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "Test123!",
        "name": "Test User"
    })
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_complete_order_flow(test_client, auth_headers):
    """Test de flujo completo: crear dirección + crear orden"""
    
    # 1. Crear dirección
    address_response = await test_client.post(
        "/api/addresses",
        headers=auth_headers,
        json={
            "street": "Calle 123",
            "city": "Bogotá",
            "state": "Cundinamarca",
            "zipCode": "110111",
            "isDefault": True
        }
    )
    assert address_response.status_code == 201
    address_id = address_response.json()["address"]["id"]
    
    # 2. Obtener productos disponibles
    products_response = await test_client.get("/api/products")
    assert products_response.status_code == 200
    products = products_response.json()["products"]
    assert len(products) > 0
    
    product_id = products[0]["id"]
    product_price = products[0]["price"]
    
    # 3. Crear orden
    order_response = await test_client.post(
        "/api/orders",
        headers=auth_headers,
        json={
            "addressId": address_id,
            "items": [
                {"productId": product_id, "quantity": 2, "price": product_price}
            ],
            "paymentMethod": "CASH",
            "notes": "Sin salsas"
        }
    )
    assert order_response.status_code == 200
    order = order_response.json()["order"]
    
    assert order["status"] == "PENDING"
    assert order["total"] == product_price * 2
    assert len(order["items"]) == 1
    assert order["paymentMethod"] == "CASH"

@pytest.mark.asyncio
async def test_coupon_discount_applied(test_client, auth_headers, test_db):
    """Verificar que cupón se aplica correctamente"""
    
    # Setup: Crear cupón de 20% descuento
    await test_db.execute("""
        INSERT INTO coupons (id, code, discount_type, percentage, is_active)
        VALUES (gen_random_uuid(), 'TEST20', 'PERCENTAGE', 20.0, true)
    """)
    
    # ... (crear dirección y obtener producto similar a test anterior)
    
    # Crear orden con cupón
    order_response = await test_client.post(
        "/api/orders",
        headers=auth_headers,
        json={
            "addressId": address_id,
            "items": [{"productId": product_id, "quantity": 1, "price": 10000}],
            "paymentMethod": "CASH",
            "couponCode": "TEST20"
        }
    )
    
    assert order_response.status_code == 200
    order = order_response.json()["order"]
    
    # Verificar descuento aplicado: 10000 * 0.20 = 2000 descuento
    assert order["discount_applied"] == 2000.0
    assert order["total"] == 8000.0  # 10000 - 2000
    
    # Verificar registro de uso de cupón
    usage = await test_db.fetchrow(
        "SELECT * FROM coupon_usages WHERE order_id = $1",
        order["id"]
    )
    assert usage is not None
```

**Justificación FIRST:**
- **F:** < 1s por test (DB en memoria o Docker local)
- **I:** Rollback de transacción después de cada test
- **R:** Seed data determinístico, siempre mismo resultado
- **S:** Aserciones de status code y valores específicos
- **T:** Se escribe al implementar feature de órdenes

---

#### **5.3.3. Pruebas de Integración - Mensajería (RabbitMQ)**

**Scope:** Verificar publicación de mensajes a RabbitMQ

**Ejemplo:**
```python
# tests/integration/test_rabbitmq_publishing.py
import pytest
import json
from services.rabbitmq import publish_order, get_channel

@pytest.mark.asyncio
async def test_order_published_to_queue():
    """Verificar que orden se publica correctamente a RabbitMQ"""
    
    # Setup: Orden de ejemplo
    order_data = {
        "id": "test-order-123",
        "userId": "user-456",
        "addressId": "addr-789",
        "items": [
            {"productId": "prod-1", "quantity": 2, "price": 15000}
        ],
        "total": 30000,
        "notes": "Test order"
    }
    
    # Publicar orden
    result = await publish_order(order_data)
    assert result is True
    
    # Consumir mensaje de la cola para verificar
    channel = await get_channel()
    queue = await channel.get_queue("order_queue")
    
    message = await queue.get(timeout=5)
    assert message is not None
    
    body = json.loads(message.body.decode())
    assert body["orderId"] == "test-order-123"
    assert body["userId"] == "user-456"
    assert len(body["items"]) == 1
    assert body["total"] == 30000
    
    await message.ack()

@pytest.mark.asyncio
async def test_rabbitmq_reconnection():
    """Verificar reconexión automática si RabbitMQ se cae"""
    
    # Publicar mensaje exitosamente
    await publish_order({"id": "order-1", "userId": "user-1", ...})
    
    # Simular cierre de conexión
    from services import rabbitmq
    if rabbitmq._connection:
        await rabbitmq._connection.close()
        rabbitmq._connection = None
        rabbitmq._channel = None
    
    # Siguiente publicación debe reconectar automáticamente
    result = await publish_order({"id": "order-2", "userId": "user-2", ...})
    assert result is True
```

**Justificación FIRST:**
- **F:** Rápido con RabbitMQ en Docker local
- **I:** Purgar cola antes/después de cada test
- **R:** Mismo comportamiento en cualquier entorno con RabbitMQ
- **S:** Aserciones de mensaje recibido vs esperado
- **T:** Se escribe al implementar integración RabbitMQ

---

#### **5.3.4. Pruebas End-to-End (E2E)**

**Scope:** Flujo completo desde frontend hasta worker

**Justificación:** Verificar que Producer (API) + Broker (RabbitMQ) + Consumer (Worker) funcionan juntos

**Ejemplo:**
```python
# tests/e2e/test_order_processing.py
import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_order_complete_lifecycle():
    """
    Test E2E: Orden creada en API → Publicada a RabbitMQ → Procesada por Worker → Estado actualizado
    """
    
    # Prerequisito: Worker debe estar corriendo
    # (En CI/CD, docker-compose.test.yml levanta API + Worker + DB + RabbitMQ)
    
    async with AsyncClient(base_url="http://localhost:5000") as client:
        # 1. Autenticación
        auth_response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        token = auth_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Crear orden
        order_response = await client.post(
            "/api/orders",
            headers=headers,
            json={
                "addressId": "...",  # Setup fixture
                "items": [{"productId": "...", "quantity": 1, "price": 10000}],
                "paymentMethod": "CASH"
            }
        )
        order_id = order_response.json()["order"]["id"]
        
        # 3. Esperar a que worker procese (máx 10s)
        for _ in range(10):
            await asyncio.sleep(1)
            status_response = await client.get(f"/api/orders/{order_id}", headers=headers)
            order = status_response.json()["order"]
            
            if order["status"] != "PENDING":
                break
        
        # 4. Verificar que worker actualizó el estado
        assert order["status"] in ["CONFIRMED", "PREPARING"]
        # Worker debe haber actualizado updatedAt
        assert order["updatedAt"] > order["createdAt"]
```

**Justificación FIRST:**
- **F:** 10-15s (depende de worker processing time)
- **I:** Cada test con orden única (UUID)
- **R:** Determinístico si worker está disponible
- **S:** Pass si estado cambia, Fail si queda PENDING
- **T:** Se escribe después de implementar worker

---

### 5.4. Herramientas y Configuración Recomendada

#### **pytest + plugins**
```bash
pip install pytest pytest-asyncio pytest-cov pytest-xdist httpx
```

#### **Estructura de carpetas de tests (actual):**
```
api/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures globales
│   ├── fixtures/
│   │   ├── data.py              # Datos de prueba
│   │   └── database.py          # Fixtures de DB
│   ├── unit/
│   │   └── test_auth_service.py # Unitarias de auth
│   └── integration/
│       ├── test_health_endpoint.py
│       ├── test_products_endpoints.py
│       ├── test_auth_login.py
│       ├── test_auth_profile.py
│       ├── test_addresses_endpoints.py
│       ├── test_addresses_create.py
│       └── test_coupons_validate.py
```

#### **pytest.ini:**
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Pruebas unitarias rápidas
    integration: Pruebas de integración con DB
    e2e: Pruebas end-to-end (requieren servicios externos)
    slow: Pruebas que tardan > 5s

# Coverage mínimo
addopts = 
    --cov=services
    --cov=routers
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
```

#### **GitHub Actions CI/CD:**
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      rabbitmq:
        image: rabbitmq:3-management
        ports:
          - 5672:5672
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx
      
      - name: Run Unit Tests
        run: pytest tests/unit -v --cov
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
          RABBITMQ_URL: amqp://guest:guest@localhost:5672/
          JWT_SECRET: test-secret
      
      - name: Run Integration Tests
        run: pytest tests/integration -v --cov --cov-append
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
```

---

### 5.5. Niveles de Testing y Cobertura Objetivo

| Nivel | Cobertura Objetivo | Tiempo Ejecución | Justificación |
|-------|-------------------|------------------|---------------|
| **Unitarias** | 90% de `services/` | < 5s | Lógica de negocio crítica (auth, pricing, validation) |
| **Integración API** | 80% de `routers/` | 10-20s | Endpoints principales (auth, orders, admin) |
| **Integración Mensajería** | 70% de `services/rabbitmq.py` | 5-10s | Publicación y reconexión |
| **E2E** | 5-10 flujos críticos | 30-60s | Solo happy paths y edge cases críticos |

**Total esperado:** Suite completa en < 90s

---

### 5.6. Implementación Recomendada (Prioridad)

#### **Fase 1: Fundamentos (Semana 1)**
1. Setup de pytest + fixtures base
2. Tests unitarios de `auth_service.py`
3. Tests de integración de `/api/auth/register` y `/api/auth/login`

#### **Fase 2: Core Business Logic (Semana 2)**
1. Tests de creación de órdenes (sin cupones)
2. Tests de RabbitMQ publishing
3. Tests de productos y direcciones

#### **Fase 3: Features Avanzadas (Semana 3)**
1. Tests de cupones (validación, aplicación, registro de uso)
2. Tests de admin endpoints
3. Tests de edge cases (errores, validaciones)

#### **Fase 4: E2E y CI/CD (Semana 4)**
1. Tests E2E de flujo completo
2. Configuración de GitHub Actions
3. Pre-commit hooks
4. Documentación de testing

---

## 6. Recomendaciones Prioritarias

### 🔴 **Críticas (Implementar INMEDIATAMENTE)**

1. **[SEGURIDAD] Reactivar autenticación en endpoints de cupones**
   - **Archivo:** `routers/admin.py`
   - **Acción:** Añadir `current_user: dict = Depends(get_current_user)` a todos los endpoints de cupones
   - **Tiempo estimado:** 15 minutos

2. **[SEGURIDAD] Remover secret por defecto de JWT**
   - **Archivo:** `services/auth_service.py`
   - **Acción:** Forzar configuración de `JWT_SECRET` via env var
   - **Tiempo estimado:** 10 minutos

3. **[CONSISTENCIA] Mover registro de cupón dentro de transacción**
   - **Archivo:** `routers/orders.py` + `database_service.py`
   - **Acción:** Incluir `register_coupon_usage` en transacción de `create_order`
   - **Tiempo estimado:** 30 minutos

4. **[TESTING] Implementar Fase 1 de pruebas (auth + fixtures)**
   - **Archivos:** `tests/unit/test_auth_service.py`, `tests/conftest.py`
   - **Tiempo estimado:** 4 horas

---

### 🟡 **Importantes (Implementar en 1-2 semanas)**

1. **[SOLID - SRP] Separar `database_service.py` en repositorios**
   - **Acción:** Crear `repositories/` con archivos por entidad
   - **Tiempo estimado:** 8 horas

2. **[SOLID - DIP] Introducir abstracciones de Repository**
   - **Acción:** Interfaces + Dependency Injection
   - **Tiempo estimado:** 12 horas

3. **[PATRONES] Implementar Strategy Pattern para descuentos**
   - **Acción:** `services/business/discount_strategies.py`
   - **Tiempo estimado:** 4 horas

4. **[SEGURIDAD] Implementar Rate Limiting**
   - **Acción:** Middleware con `slowapi`
   - **Tiempo estimado:** 2 horas

5. **[PERFORMANCE] Agregar paginación a listados**
   - **Acción:** Query params `skip` y `limit` en GET endpoints
   - **Tiempo estimado:** 3 horas

---

### 🟢 **Deseables (Implementar en 1 mes)**

1. **[CALIDAD] Logging estructurado**
   - **Acción:** Reemplazar `print()` con `logging`
   - **Tiempo estimado:** 4 horas

2. **[PATRONES] Observer Pattern para notificaciones**
   - **Acción:** `services/events/order_events.py`
   - **Tiempo estimado:** 6 horas

3. **[TESTING] Completar cobertura de 80%**
   - **Acción:** Implementar Fases 2-4 de pruebas
   - **Tiempo estimado:** 16 horas

4. **[DOCS] Documentación de arquitectura**
   - **Acción:** Diagramas de componentes, flujos, ERD
   - **Tiempo estimado:** 4 horas

---

## 7. Plan de Acción

### Sprint 1 (Semana 1): Seguridad y Testing Base
- [ ] Reactivar auth en cupones (**CRÍTICO**)
- [ ] Configurar JWT secret obligatorio (**CRÍTICO**)
- [ ] Mover registro de cupón a transacción (**CRÍTICO**)
- [ ] Setup pytest + fixtures
- [ ] Tests unitarios de auth_service
- [ ] Tests de integración de endpoints de auth

**Entregables:**
- Vulnerabilidades de seguridad resueltas
- Suite de tests base con 30% cobertura

---

### Sprint 2 (Semana 2): Refactoring SOLID
- [ ] Separar `database_service.py` en repositorios por entidad
- [ ] Introducir interfaces de Repository
- [ ] Implementar Strategy Pattern para descuentos
- [ ] Tests de órdenes y cupones

**Entregables:**
- Código con mejor separación de responsabilidades
- Cobertura de tests al 50%

---

### Sprint 3 (Semana 3): Features y Performance
- [ ] Rate limiting en endpoints críticos
- [ ] Paginación en listados
- [ ] Logging estructurado
- [ ] Tests de RabbitMQ y admin endpoints

**Entregables:**
- API más robusta y escalable
- Cobertura de tests al 70%

---

### Sprint 4 (Semana 4): E2E y CI/CD
- [ ] Tests E2E de flujos completos
- [ ] Configuración de GitHub Actions
- [ ] Pre-commit hooks
- [ ] Documentación completa

**Entregables:**
- Pipeline de CI/CD funcional
- Cobertura de tests al 80%
- Documentación de arquitectura

---

## 📊 Métricas de Éxito

### Antes de Auditoría
- ❌ 0% Cobertura de tests
- ❌ Vulnerabilidades de seguridad críticas
- ❌ Código monolítico (database_service 700+ líneas)
- ❌ Sin CI/CD

### Después de Implementar Plan (1 mes)
- ✅ 80% Cobertura de tests
- ✅ Vulnerabilidades críticas resueltas
- ✅ Código modular con SOLID mejorado
- ✅ CI/CD con tests automáticos
- ✅ Documentación completa

---

## 📚 Recursos Adicionales

- **Principios SOLID:** https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design
- **Patrones de Diseño en Python:** https://refactoring.guru/design-patterns/python
- **Testing con pytest-asyncio:** https://pytest-asyncio.readthedocs.io/
- **FIRST Principles:** https://medium.com/@tasdikrahman/f-i-r-s-t-principles-of-testing-1a497acda8d6
- **FastAPI Testing:** https://fastapi.tiangolo.com/tutorial/testing/

---

**Fin del Reporte de Auditoría**

---

## Actualización: Resultados de Testing y Ejecución

- Estado: Suite de integración curada ejecutándose en verde (16 tests en ~11.7s). Unitarias de `auth_service` ejecutadas correctamente.
- Evidencias incluidas en el repo:
    - `api/Evidencia Tests Unitarios.png`
    - `api/Evidencia Tests de Integracion.png`

### Endpoints validados en integraciones
- `auth`: `/api/auth/login`, `/api/auth/profile`
- `addresses`: GET `/api/addresses`, GET `/api/addresses/{id}`, POST `/api/addresses`
- `coupons`: POST `/api/coupons/validate` (válido, inactivo, expirado, error por falta de código)
- `health`: GET `/api/health`
- `products`: GET `/api/products/`, GET `/api/products/{id}`, 404 para no encontrado

Endpoints legacy retirados temporalmente: `admin`, `orders`, `rabbitmq` (se reintroducen cuando estén alineados y con mocks).

### Cómo ejecutar los tests (Windows PowerShell)

Prerequisitos:
- Ubicación: `SoftDomiFood/SoftDomiFood/api`
- Python 3.12 y entorno virtual (`venv`) activo

Instalación:

```powershell
cd "C:\Users\yesid.perez\Desktop\TrainingIA\SoftDomiFood\SoftDomiFood\api";
python -m venv venv;
.\venv\Scripts\Activate.ps1;
pip install -r requirements.txt;
pip install -r requirements-test.txt
```

Variables de entorno mínimas:

```powershell
$env:DATABASE_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_db";
$env:ASYNC_PG_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_db";
$env:JWT_SECRET = "test-secret-key"
```

Ejecutar integraciones:

```powershell
pytest tests/integration -v --no-cov
```

Ejecutar unitarias:

```powershell
pytest tests/unit -v --no-cov
```

Ejecutar suite con cobertura:

```powershell
pytest -v --cov=services --cov=routers --cov-report=term-missing
```

Nota: Puede aparecer un warning de `passlib/bcrypt` por `pkg_resources` deprecado; no afecta la ejecución. Se sugiere actualizar `bcrypt`/`passlib` posteriormente.

