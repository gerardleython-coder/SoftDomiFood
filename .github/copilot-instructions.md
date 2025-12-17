## Pruebas: Principios INVEST y TDD
- **INVEST**: Cada caso de prueba y HU debe ser:
	- **I**ndependiente: Los tests no deben depender unos de otros. Usa fixtures con datos únicos (UUID) y rollback de BD.
	- **N**egociable: Los criterios de aceptación y casos de prueba pueden refinarse en `entregables/TEST_CASES.md` y `entregables/TEST_PLAN.md`.
	- **V**alorable: Cada test debe validar un resultado de negocio claro (ej: registro exitoso, error de email duplicado).
	- **E**stimable: Los tests y HU están priorizados y estimados en `REFINED_BACKLOG.md`.
	- **S**mall (Pequeño): Los tests deben ser atómicos, cubrir un solo comportamiento.
	- **T**estable: Todo criterio de aceptación tiene un test automatizado (ver `api/tests/e2e/`).
- **TDD**: El desarrollo sigue el ciclo Red-Green-Refactor:
	1. Escribe primero el test (basado en los criterios de aceptación INVEST).
	2. Ejecuta y verifica que falla (Red).
	3. Implementa la funcionalidad mínima para pasar el test (Green).
	4. Refactoriza el código y los tests manteniendo cobertura y claridad.
- **Ejemplo de patrón de test TDD/INVEST:**
	- Cada archivo de test E2E (`api/tests/e2e/`) cubre una HU y sus criterios.
	- Usa nombres descriptivos: `test_tc_hu001_01_successful_registration`.
	- Valida tanto casos positivos como negativos y de borde.
	- Los tests no dependen de datos previos: usan fixtures y limpian la BD.
	- Los resultados esperados están alineados con los criterios de negocio.

# 🤖 Instrucciones Copilot para SoftDomiFood

## Arquitectura General
- **Microservicios**: El sistema se divide en `api/` (backend FastAPI), `worker/` (Node.js consumidor), `frontend/` (React), y `admin-frontend/` (panel admin en React).
- **Flujo de datos**: Los pedidos se crean vía API, se procesan de forma asíncrona por el worker (RabbitMQ) y los resultados se reflejan en la base de datos y la UI.
- **Base de datos**: PostgreSQL, con migraciones y scripts de seed en `database/` y `api/`.
- **Testing**: Automatización E2E y QA en `qa_automated/`, tests de API en `api/tests/`.

## Flujos de Trabajo de Desarrollo
- **Levantar todos los servicios**: `docker-compose up -d` desde la raíz. Ver `README.md` para puertos y URLs.
- **Desarrollo local**: Ver `SoftDomiFood/docs/setup/DESARROLLO-LOCAL.md` para setup de Python/Node, variables de entorno y configuración de BD.
- **Ejecutar tests de API**: `pytest api/tests/` (E2E, integración, unitarios). Usa `pytest.ini` para configuración.
- **Seed de datos**: `docker exec softdomifood-api python /app/seed_data.py` (o ver scripts/ para más).
- **Scripts**: Scripts utilitarios en `scripts/` (ver `scripts/README.md`).

## Convenciones Específicas del Proyecto
- **API**: Todos los endpoints bajo `/api/`. Autenticación JWT, ver `api/routers/auth.py`.
- **Testing**: Los tests E2E esperan BD real y servicios activos. Los fixtures usan UUIDs para datos únicos.
- **Respuestas**: Algunos endpoints (ej: `/api/products`) retornan `{ "products": [...] }` en vez de una lista directa.
- **Credenciales**: Admin por defecto: `admin@softdomifood.com` / `admin123`. Cliente por defecto: `cliente@test.com`.
- **Docs**: Toda la documentación de negocio/testing/arquitectura está en `SoftDomiFood/docs/` y `SoftDomiFood/entregables/`.

## Puntos de Integración
- **RabbitMQ**: Usado para procesamiento asíncrono de pedidos. Ver `api/services/rabbitmq.py` y `worker/`.
- **Prisma**: Usado en `worker/` para acceso a BD.
- **Playwright**: Usado para automatización QA en `qa_automated/`.

## Patrones y Ejemplos
- **Límites de servicio**: Cada carpeta (`api/`, `worker/`, `frontend/`, `admin-frontend/`) es una unidad desplegable.
- **Acceso a base de datos**: Usar `api/services/database_service.py` para lógica de BD, no queries directas en routers.
- **Testing**: Usar fixtures en `api/tests/conftest.py` para aislamiento de BD y datos únicos.
- **Scripts**: Ejecutar scripts vía Docker para entornos consistentes (ver `scripts/README.md`).

## Archivos/Directorios Clave
- `api/routers/` - Endpoints de API
- `api/services/` - Lógica de negocio
- `api/tests/` - Todos los tipos de tests
- `worker/` - Consumidor de pedidos
- `frontend/`, `admin-frontend/` - Apps React
- `database/` - Migraciones SQL, backups
- `scripts/` - Scripts utilitarios
- `docs/`, `entregables/` - Toda la documentación

---

Para más información, ver el `README.md` principal y `docs/`. Si algún patrón no es claro, revisa el README de la carpeta correspondiente o pide aclaración.
