import asyncio
import asyncpg
import os

TEST_DATABASE_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_test_db"

async def main():
    conn = await asyncpg.connect(TEST_DATABASE_URL)

    # Listar todos los usuarios
    users = await conn.fetch("SELECT email, role, LEFT(password, 50) as pass_preview FROM users")

    print("Usuarios en BD de test:")
    for user in users:
        print(f"  - {user['email']} ({user['role']}): {user['pass_preview']}...")

    if not users:
        print("  ❌ No hay usuarios en la BD de test")

    # Listar productos
    products = await conn.fetch("SELECT name FROM products LIMIT 5")
    print(f"\nProductos en BD de test: {len(products)}")
    for product in products:
        print(f"  - {product['name']}")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
