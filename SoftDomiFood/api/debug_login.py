import asyncio
import asyncpg
import os
from services.auth_service import verify_password, get_password_hash

TEST_DATABASE_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_test_db"

async def main():
    conn = await asyncpg.connect(TEST_DATABASE_URL)

    # Obtener usuario de test
    user = await conn.fetchrow("SELECT email, password FROM users WHERE email = 'cliente1@example.com'")

    if user:
        print(f"Usuario encontrado: {user['email']}")
        print(f"Hash almacenado: {user['password'][:50]}...")

        # Verificar contraseña
        plain_password = "cliente123"
        is_valid = verify_password(plain_password, user['password'])
        print(f"Verificación de contraseña: {is_valid}")

        # Generar nuevo hash para comparar
        new_hash = get_password_hash(plain_password)
        print(f"Nuevo hash generado: {new_hash[:50]}...")

        # Verificar nuevo hash
        is_valid_new = verify_password(plain_password, new_hash)
        print(f"Verificación de nuevo hash: {is_valid_new}")
    else:
        print("❌ Usuario no encontrado")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
