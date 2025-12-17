import asyncio
import asyncpg

async def check_admin():
    DATABASE_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Buscar usuarios admin
        admins = await conn.fetch(
            "SELECT id, email, name, role FROM users WHERE role = 'ADMIN'"
        )
        
        print("Usuarios ADMIN en la base de datos:")
        for admin in admins:
            print(f"  - Email: {admin['email']}")
            print(f"    Nombre: {admin['name']}")
            print(f"    ID: {admin['id']}")
            print()
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_admin())
