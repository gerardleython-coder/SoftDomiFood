#!/usr/bin/env python3
"""Verifica que el usuario de test existe y tiene la contraseña correcta."""
import asyncio
import asyncpg
import os
from services.auth_service import verify_password

async def verify_user():
    """Verifica el usuario de test en la BD."""
    DATABASE_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_test_db"

    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Listar todos los usuarios
        users = await conn.fetch("SELECT email, role FROM users LIMIT 10")
        print(f"📊 Usuarios en la BD ({len(users)}):")
        for u in users:
            print(f"   - {u['email']} ({u.get('role', 'N/A')})")

        # Obtener el usuario
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            "cliente1@example.com"
        )

        if not user:
            print("❌ Usuario no encontrado")
            return

        print(f"✅ Usuario encontrado:")
        print(f"   Email: {user['email']}")
        print(f"   Columnas: {user.keys()}")

        # Intentar verificar la contraseña
        password_column = None
        for col in user.keys():
            if 'password' in col.lower():
                password_column = col
                print(f"   Columna de contraseña: {col}")
                print(f"   Hash: {user[col][:60]}...")

                # Verificar contraseña
                result = verify_password("cliente123", user[col])
                print(f"   Verificación de contraseña: {result}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_user())
