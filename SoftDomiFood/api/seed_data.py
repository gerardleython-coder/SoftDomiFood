"""
Script para poblar la base de datos con datos de ejemplo.
Incluye productos, usuarios de prueba y pedidos de ejemplo.
"""

import asyncpg
import os
import asyncio
from datetime import datetime, timedelta
# Importar el hash de contraseña real del servicio de autenticación
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import get_password_hash

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Datos de ejemplo para productos
SAMPLE_PRODUCTS = [
    {
        "name": "Salchipapa Clásica",
        "description": "Papas fritas crujientes con salchichas, salsas (mayonesa, ketchup, mostaza) y queso rallado",
        "price": 12000,
        "category": "SALCHIPAPAS",
        "image": "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?w=500",
        "isAvailable": True
    },
    {
        "name": "Salchipapa Especial",
        "description": "Papas fritas con salchichas, pollo desmechado, chorizo, huevo frito y todas las salsas",
        "price": 18000,
        "category": "SALCHIPAPAS",
        "image": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=500",
        "isAvailable": True
    },
    {
        "name": "SalchiGod",
        "description": "Explosión de sabores",
        "price": 15000,
        "category": "SALCHIPAPAS",
        "image": "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=500",
        "isAvailable": True
    },
    {
        "name": "Gaseosa",
        "description": "Gaseosa 350ml (Coca Cola, Pepsi, Sprite o 7UP)",
        "price": 3000,
        "category": "BEBIDAS",
        "image": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=500",
        "isAvailable": True
    },
    {
        "name": "Jugo Natural",
        "description": "Jugo natural de frutas 500ml (Lulo, Mora, Maracuyá)",
        "price": 4000,
        "category": "BEBIDAS",
        "image": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=500",
        "isAvailable": True
    },
    {
        "name": "Agua con Gas",
        "description": "Agua con gas 500ml",
        "price": 2500,
        "category": "BEBIDAS",
        "image": "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=500",
        "isAvailable": True
    },
    {
        "name": "Queso Extra",
        "description": "Porción adicional de queso rallado para tu salchipapa",
        "price": 2000,
        "category": "ADICIONALES",
        "image": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=500",
        "isAvailable": True
    },
    {
        "name": "Chorizo Extra",
        "description": "Porción adicional de chorizo",
        "price": 3000,
        "category": "ADICIONALES",
        "image": "https://images.unsplash.com/photo-1616190171443-4cdaaaa23a90?w=500",
        "isAvailable": True
    },
    {
        "name": "Combo Familiar",
        "description": "2 Salchipapas Especiales + 2 Gaseosas + Queso Extra",
        "price": 45000,
        "category": "COMBOS",
        "image": "https://images.unsplash.com/photo-1534939561126-855b8675edd7?w=500",
        "isAvailable": True
    },
    {
        "name": "Combo Personal",
        "description": "1 Salchipapa Clásica + 1 Gaseosa",
        "price": 15000,
        "category": "COMBOS",
        "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=500",
        "isAvailable": True
    }
]

# Datos de ejemplo para usuarios (no admin)
SAMPLE_USERS = [
    {
        "email": "cliente1@example.com",
        "password": "cliente123",
        "name": "Juan Pérez",
        "phone": "3001234567",
        "role": "CUSTOMER"
    },
    {
        "email": "cliente2@example.com",
        "password": "cliente123",
        "name": "María García",
        "phone": "3007654321",
        "role": "CUSTOMER"
    }
]


async def seed_products(conn: asyncpg.Connection, force_clear: bool = False):
    """Poblar la tabla de productos con datos de ejemplo"""
    try:
        if force_clear:
            await conn.execute("DELETE FROM products WHERE category IN ('SALCHIPAPAS', 'BEBIDAS', 'ADICIONALES', 'COMBOS')")

        # Verificar qué productos ya existen
        existing_products = await conn.fetch("SELECT name FROM products")
        existing_names = {p['name'] for p in existing_products}

        inserted_count = 0
        for product in SAMPLE_PRODUCTS:
            if product['name'] not in existing_names:
                await conn.execute("""
                    INSERT INTO products (id, name, description, price, category, image, "isAvailable", "createdAt", "updatedAt")
                    VALUES (gen_random_uuid(), $1, $2, $3, $4::"ProductCategory", $5, $6, NOW(), NOW())
                """, product['name'], product['description'], product['price'],
                    product['category'], product.get('image'), product['isAvailable'])
                inserted_count += 1

        print(f"✅ Productos procesados: {inserted_count} nuevos, {len(SAMPLE_PRODUCTS) - inserted_count} ya existían")
        return inserted_count
    except Exception as e:
        print(f"⚠️  Error al poblar productos: {e}")
        return 0


async def seed_users(conn: asyncpg.Connection, force_clear: bool = False):
    """Poblar la tabla de usuarios con datos de ejemplo"""
    try:
        if force_clear:
            await conn.execute("DELETE FROM users WHERE role = 'CUSTOMER' AND email LIKE 'cliente%@example.com'")
            # Forzar invalidación de caché de usuarios de prueba
            try:
                from services.database_service import CacheKeys, _cache
                for user_data in SAMPLE_USERS:
                    cache_key = CacheKeys.user_by_email(user_data['email'])
                    _cache.delete(cache_key)
            except Exception as ce:
                print(f"⚠️  No se pudo invalidar caché de usuarios: {ce}")

        inserted_count = 0
        for user_data in SAMPLE_USERS:
            # Verificar si el usuario ya existe
            existing = await conn.fetchrow(
                'SELECT id FROM users WHERE email = $1',
                user_data['email']
            )

            if not existing:
                hashed_password = get_password_hash(user_data['password'])
                await conn.execute("""
                    INSERT INTO users (id, email, password, name, phone, role, "createdAt", "updatedAt")
                    VALUES (gen_random_uuid(), $1, $2, $3, $4, $5::"UserRole", NOW(), NOW())
                """, user_data['email'], hashed_password, user_data['name'],
                    user_data.get('phone'), user_data['role'])
                inserted_count += 1
                print(f"   ✅ Usuario creado: {user_data['email']}")
            else:
                print(f"   ⏭️  Usuario ya existe: {user_data['email']}")

        print(f"✅ Usuarios procesados: {inserted_count} nuevos")
        return inserted_count
    except Exception as e:
        print(f"⚠️  Error al poblar usuarios: {e}")
        import traceback
        traceback.print_exc()
        return 0


async def seed_sample_orders(conn: asyncpg.Connection, force_clear: bool = False):
    """Crear pedidos de ejemplo (requiere usuarios y productos existentes)"""
    try:
        if force_clear:
            await conn.execute("DELETE FROM order_items")
            await conn.execute("DELETE FROM orders WHERE notes LIKE '%Pedido de ejemplo%'")

        # Obtener usuarios de prueba
        users = await conn.fetch("SELECT id FROM users WHERE role = 'CUSTOMER' LIMIT 2")
        if not users:
            print("⚠️  No hay usuarios de cliente para crear pedidos de ejemplo")
            return 0

        # Obtener productos
        products = await conn.fetch("SELECT id, price FROM products LIMIT 5")
        if not products:
            print("⚠️  No hay productos para crear pedidos de ejemplo")
            return 0

        # Crear direcciones de ejemplo para los usuarios
        addresses_created = []
        for user in users:
            # Verificar si el usuario tiene dirección
            addr = await conn.fetchrow(
                'SELECT id FROM addresses WHERE "userId" = $1 LIMIT 1',
                user['id']
            )

            if not addr:
                addr_id = await conn.fetchval("""
                    INSERT INTO addresses (id, "userId", street, city, state, "zipCode", country, "isDefault", "createdAt", "updatedAt")
                    VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, true, NOW(), NOW())
                    RETURNING id
                """, user['id'], "Calle 123 #45-67", "Bogotá", "Cundinamarca", "110111", "Colombia")
                addresses_created.append(addr_id)
            else:
                addresses_created.append(addr['id'])

        # Crear algunos pedidos de ejemplo
        orders_created = 0
        for i, user in enumerate(users[:2]):  # Solo primeros 2 usuarios
            addr_id = addresses_created[i] if i < len(addresses_created) else addresses_created[0]

            # Crear pedido
            order_id = await conn.fetchval("""
                INSERT INTO orders (id, "userId", "addressId", status, total, "paymentMethod", notes, "createdAt", "updatedAt")
                VALUES (gen_random_uuid(), $1, $2, $3::"OrderStatus", $4, $5::"PaymentMethod", $6, NOW() - INTERVAL '%s days', NOW())
                RETURNING id
            """ % (i + 1), user['id'], addr_id, 'DELIVERED',
                float(products[0]['price']) * 2, 'CASH', 'Pedido de ejemplo para testing')

            # Agregar items al pedido
            total = 0
            for j, product in enumerate(products[:2]):  # Primeros 2 productos
                quantity = 1 + j
                item_total = float(product['price']) * quantity
                total += item_total

                await conn.execute("""
                    INSERT INTO order_items (id, "orderId", "productId", quantity, price, "createdAt")
                    VALUES (gen_random_uuid(), $1, $2, $3, $4, NOW() - INTERVAL '%s days')
                """ % (i + 1), order_id, product['id'], quantity, product['price'])

            # Actualizar total del pedido
            await conn.execute("UPDATE orders SET total = $1 WHERE id = $2", total, order_id)
            orders_created += 1

        print(f"✅ Pedidos de ejemplo creados: {orders_created}")
        return orders_created
    except Exception as e:
        print(f"⚠️  Error al crear pedidos de ejemplo: {e}")
        import traceback
        traceback.print_exc()
        return 0


async def seed_database(force_clear: bool = False):
    """Poblar la base de datos con datos de ejemplo"""
    if not DATABASE_URL:
        print("❌ DATABASE_URL no está configurada")
        return False

    print("🌱 Iniciando seed de datos de ejemplo...")
    print("")

    try:
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            if force_clear:
                print("🧹 Limpiando tablas dependientes para integridad referencial...")
                # Eliminar primero tablas hijas (con manejo de errores para tablas inexistentes)
                tables_to_clean = [
                    "order_items",
                    "orders",
                    "favorites",
                    "addresses",
                    "reviews",
                    "coupon_usages",
                    "coupons"
                ]
                for table in tables_to_clean:
                    try:
                        await conn.execute(f"DELETE FROM {table}")
                        print(f"   🗑️  Tabla {table} limpiada")
                    except Exception as te:
                        print(f"   ⏭️  Tabla {table} no existe o ya está vacía")

                # Ahora sí usuarios y productos de prueba
                await conn.execute("DELETE FROM users WHERE role = 'CUSTOMER' AND email LIKE 'cliente%@example.com'")
                await conn.execute("DELETE FROM products WHERE category IN ('SALCHIPAPAS', 'BEBIDAS', 'ADICIONALES', 'COMBOS')")
                print("✅ Tablas limpiadas correctamente.\n")

            # Poblar productos
            print("📦 Poblando productos...")
            await seed_products(conn, force_clear)
            print("")

            # Poblar usuarios
            print("👥 Poblando usuarios de prueba...")
            await seed_users(conn, force_clear)
            print("")

            # Poblar pedidos de ejemplo
            print("📋 Creando pedidos de ejemplo...")
            await seed_sample_orders(conn, force_clear)
            print("")

            print("✅ Seed completado exitosamente!")
            return True
        finally:
            await conn.close()
    except Exception as e:
        print(f"❌ Error durante el seed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv or "-f" in sys.argv
    asyncio.run(seed_database(force_clear=force))
