"""
Fixtures de base de datos para pruebas
"""
import asyncpg
import os
from typing import AsyncGenerator

# URL de base de datos de pruebas
TEST_DATABASE_URL = os.getenv(
    "ASYNC_PG_URL",
    os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://softdomifood_user:softdomifood_pass@postgres:5432/softdomifood_test_db"
    )
)

async def create_test_database():
    """Crear base de datos de pruebas si no existe"""
    # Conectar a postgres default para crear DB
    conn = await asyncpg.connect(
        "postgresql://softdomifood_user:softdomifood_pass@postgres:5432/postgres"
    )
    try:
        # Verificar si existe
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'softdomifood_test_db'"
        )
        if not exists:
            await conn.execute("CREATE DATABASE softdomifood_test_db")
            print("✅ Base de datos de pruebas creada")
    finally:
        await conn.close()

async def drop_test_database():
    """Eliminar base de datos de pruebas"""
    conn = await asyncpg.connect(
        "postgresql://softdomifood_user:softdomifood_pass@postgres:5432/postgres"
    )
    try:
        # Terminar conexiones activas
        await conn.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'softdomifood_test_db'
            AND pid <> pg_backend_pid()
        """)
        await conn.execute("DROP DATABASE IF EXISTS softdomifood_test_db")
        print("✅ Base de datos de pruebas eliminada")
    finally:
        await conn.close()

async def init_test_database(conn: asyncpg.Connection):
    """Inicializar esquema de base de datos de pruebas"""
    from init_db import INIT_SQL
    await conn.execute(INIT_SQL)

async def clean_test_database(conn: asyncpg.Connection):
    """Limpiar datos de prueba (mantener esquema)"""
    # Orden importante por foreign keys
    tables = [
        "coupon_usages",
        "order_items",
        "orders",
        "addresses",
        "coupons",
        "products",
        "users"
    ]
    for table in tables:
        await conn.execute(f'TRUNCATE TABLE "{table}" CASCADE')

async def seed_sample_products(conn: asyncpg.Connection):
    """Insertar productos de prueba"""
    from tests.fixtures.data import SAMPLE_PRODUCTS

    for product in SAMPLE_PRODUCTS:
        await conn.execute(
            """
            INSERT INTO products (id, name, description, price, category, image, "isAvailable", "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, NOW(), NOW())
            """,
            product["name"],
            product["description"],
            product["price"],
            product["category"],
            product.get("image"),
            product["isAvailable"]
        )

async def seed_sample_users(conn: asyncpg.Connection):
    """Insertar usuarios de prueba con credenciales conocidas"""
    from tests.fixtures.data import SAMPLE_USER, SAMPLE_ADMIN
    from services.auth_service import get_password_hash

    # Usuario cliente
    try:
        hashed_password = get_password_hash(SAMPLE_USER["password"])
        await conn.execute(
            """
            INSERT INTO users (id, email, password, name, phone, role, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, 'CUSTOMER', NOW(), NOW())
            """,
            SAMPLE_USER["email"],
            hashed_password,
            SAMPLE_USER["name"],
            SAMPLE_USER.get("phone")
        )
        print(f"[OK] Usuario de test creado: {SAMPLE_USER['email']}")
    except Exception as e:
        print(f"[WARN] Error al insertar usuario de prueba: {e}")

    # Usuario admin
    try:
        hashed_password = get_password_hash(SAMPLE_ADMIN["password"])
        await conn.execute(
            """
            INSERT INTO users (id, email, password, name, role, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, 'ADMIN', NOW(), NOW())
            """,
            SAMPLE_ADMIN["email"],
            hashed_password,
            SAMPLE_ADMIN["name"]
        )
        print(f"[OK] Admin de test creado: {SAMPLE_ADMIN['email']}")
    except Exception as e:
        print(f"[WARN] Error al insertar admin de prueba: {e}")
