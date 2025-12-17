"""
Configuración global de pytest y fixtures compartidos
"""
import pytest
import asyncio
import asyncpg
import os
import uuid
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi import FastAPI

# Configurar variables de entorno para pruebas
os.environ["DATABASE_URL"] = "postgresql+asyncpg://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_test_db"
os.environ["ASYNC_PG_URL"] = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_test_db"
os.environ["RABBITMQ_URL"] = "amqp://admin:admin123@localhost:5672/"
os.environ["JWT_SECRET"] = "test-secret-key-only-for-testing-do-not-use-in-production"

from tests.fixtures.database import (
    TEST_DATABASE_URL,
    create_test_database,
    init_test_database,
    clean_test_database,
    seed_sample_products
)

# Event loop fixture para async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Database fixtures
@pytest.fixture(scope="session")
async def setup_test_db():
    """Setup: Crear DB de pruebas una vez por sesión"""
    await create_test_database()
    yield
    # Teardown se maneja en pytest_sessionfinish

@pytest.fixture(scope="session")
async def test_db_connection(setup_test_db):
    """Conexión a DB de pruebas que dura toda la sesión"""
    conn = await asyncpg.connect(TEST_DATABASE_URL)

    # Inicializar esquema
    await init_test_database(conn)

    yield conn

    await conn.close()

@pytest.fixture(scope="function")
async def test_db(test_db_connection):
    """
    Fixture de DB con aislamiento por test
    Cada test ejecuta en una transacción que se hace rollback al final
    """
    # Iniciar transacción
    transaction = test_db_connection.transaction()
    await transaction.start()

    try:
        yield test_db_connection
    finally:
        # Rollback para limpiar cambios del test
        await transaction.rollback()

@pytest.fixture(scope="function")
async def seeded_db(test_db):
    """DB con datos de prueba (productos) pre-cargados"""
    await seed_sample_products(test_db)
    yield test_db

# Application fixtures
@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Instancia de la aplicación FastAPI"""
    from main import app
    return app

@pytest.fixture
async def test_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP async para pruebas de endpoints"""
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as client:
        yield client

# Authentication fixtures
@pytest.fixture
async def sample_user(test_db):
    """Crear usuario de prueba y retornar sus datos"""
    from tests.fixtures.data import SAMPLE_USER
    from services.auth_service import get_password_hash

    # Email único con UUID para evitar duplicados
    unique_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    hashed_password = get_password_hash(SAMPLE_USER["password"])

    user_id = await test_db.fetchval(
        """
        INSERT INTO users (id, email, password, name, phone, role, "createdAt", "updatedAt")
        VALUES (gen_random_uuid(), $1, $2, $3, $4, 'CUSTOMER', NOW(), NOW())
        RETURNING id
        """,
        unique_email,
        hashed_password,
        SAMPLE_USER["name"],
        SAMPLE_USER.get("phone")
    )

    return {
        "id": str(user_id),
        "email": unique_email,
        "password": SAMPLE_USER["password"],  # Password sin hash para login
        "name": SAMPLE_USER["name"],
        "phone": SAMPLE_USER.get("phone"),
        "role": "CUSTOMER"
    }

@pytest.fixture
async def sample_admin(test_db):
    """Crear usuario admin de prueba"""
    from tests.fixtures.data import SAMPLE_ADMIN
    from services.auth_service import get_password_hash

    # Email único con UUID para evitar duplicados
    unique_email = f"admin_{uuid.uuid4().hex[:8]}@test.com"
    hashed_password = get_password_hash(SAMPLE_ADMIN["password"])

    admin_id = await test_db.fetchval(
        """
        INSERT INTO users (id, email, password, name, role, "createdAt", "updatedAt")
        VALUES (gen_random_uuid(), $1, $2, $3, 'ADMIN', NOW(), NOW())
        RETURNING id
        """,
        unique_email,
        hashed_password,
        SAMPLE_ADMIN["name"]
    )

    return {
        "id": str(admin_id),
        "email": unique_email,
        "password": SAMPLE_ADMIN["password"],
        "name": SAMPLE_ADMIN["name"],
        "role": "ADMIN"
    }

@pytest.fixture
async def auth_headers(test_client: AsyncClient, sample_user):
    """Headers de autenticación simulados para usuario regular (sin llamar a /api/auth/login)"""
    return {"Authorization": "Bearer test-user-token"}

@pytest.fixture
async def admin_headers(test_client: AsyncClient, sample_admin):
    """Headers de autenticación simulados para admin (sin llamar a /api/auth/login)"""
    return {"Authorization": "Bearer test-admin-token"}

@pytest.fixture
async def sample_address(test_db, sample_user):
    """Crear dirección de prueba para usuario"""
    from tests.fixtures.data import SAMPLE_ADDRESS

    address_id = await test_db.fetchval(
        """
        INSERT INTO addresses (id, "userId", street, city, state, "zipCode", country, "isDefault", instructions, "createdAt", "updatedAt")
        VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
        RETURNING id
        """,
        sample_user["id"],
        SAMPLE_ADDRESS["street"],
        SAMPLE_ADDRESS["city"],
        SAMPLE_ADDRESS["state"],
        SAMPLE_ADDRESS["zipCode"],
        SAMPLE_ADDRESS["country"],
        SAMPLE_ADDRESS["isDefault"],
        SAMPLE_ADDRESS.get("instructions")
    )

    return {
        "id": str(address_id),
        **SAMPLE_ADDRESS,
        "userId": sample_user["id"]
    }

# Mock de RabbitMQ para pruebas
@pytest.fixture
def mock_rabbitmq(monkeypatch):
    """Mock de RabbitMQ para evitar dependencia en pruebas unitarias"""
    async def mock_publish(order_data):
        return True

    monkeypatch.setattr("services.rabbitmq.publish_order", mock_publish)
    return mock_publish

# Cleanup
def pytest_sessionfinish(session, exitstatus):
    """Cleanup después de toda la sesión de pruebas"""
    # Nota: drop_test_database requiere async, se maneja manualmente si es necesario
    pass
