import asyncio
import asyncpg
import os

async def check_table():
    # Usar la URL de la base de datos local
    DATABASE_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Verificar si la tabla coupons existe
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'coupons'
            )
        """)
        
        print(f"¿Tabla 'coupons' existe? {exists}")
        
        if exists:
            # Obtener columnas
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'coupons'
                ORDER BY ordinal_position
            """)
            
            print("\nColumnas de la tabla 'coupons':")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        else:
            print("\nLa tabla 'coupons' NO EXISTE en la base de datos")
            print("Necesitas crear la tabla primero")
        
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_table())
