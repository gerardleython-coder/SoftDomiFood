import asyncio
import asyncpg

async def test_create_coupon():
    DATABASE_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Datos de prueba
        code = "TEST20"
        description = "Cupón de prueba"
        discount_type = "PERCENTAGE"
        amount = None
        percentage = 20.0
        valid_from = None
        valid_to = None
        max_uses = None
        per_user_limit = None
        applicable_user_id = None
        is_active = True
        
        print(f"Intentando crear cupón con código: {code}")
        print(f"Tipo de descuento: {discount_type}")
        print(f"Porcentaje: {percentage}")
        
        coupon_id = await conn.fetchval(
            """
            INSERT INTO coupons (id, code, description, discount_type, amount, percentage, valid_from, valid_to,
                                 max_uses, per_user_limit, applicable_user_id, is_active, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), NOW())
            RETURNING id
            """,
            code, description, discount_type, amount, percentage, valid_from, valid_to,
            max_uses, per_user_limit, applicable_user_id, is_active
        )
        
        print(f"\n✓ Cupón creado exitosamente con ID: {coupon_id}")
        
        # Leer el cupón creado
        row = await conn.fetchrow(
            """
            SELECT id, code, description, discount_type, amount, percentage, valid_from, valid_to,
                   max_uses, per_user_limit, applicable_user_id, is_active, "createdAt", "updatedAt"
            FROM coupons WHERE id = $1
            """,
            coupon_id
        )
        
        print("\nDatos del cupón creado:")
        for key, value in dict(row).items():
            print(f"  {key}: {value}")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n✗ Error al crear cupón: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_coupon())
