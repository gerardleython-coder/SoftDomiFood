import asyncio
import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL", "")

async def main():
    conn = await asyncpg.connect(DATABASE_URL)
    print("\nUsuarios de prueba:")
    rows = await conn.fetch("SELECT id, email, password, role FROM users WHERE email LIKE 'cliente%@example.com';")
    for row in rows:
        print(dict(row))
    print("\nProductos de ejemplo:")
    rows = await conn.fetch("SELECT id, name, category FROM products;")
    for row in rows:
        print(dict(row))
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
