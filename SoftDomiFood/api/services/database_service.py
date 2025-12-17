import asyncpg
import os
import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from services.cache_service import get_cache, CacheKeys
from services.secrets_manager import get_database_url, get_async_pg_url  # HU-05

# Cargar variables de entorno
load_dotenv()

# Instancia de cache (singleton)
_cache = get_cache()

# HU-05: Funciones para obtener URLs con auditoría
def _get_database_url() -> str:
    """Obtener DATABASE_URL con auditoría (HU-05)"""
    return get_database_url()

def _get_async_pg_url() -> str:
    """Obtener ASYNC_PG_URL con auditoría (HU-05)"""
    return get_async_pg_url()

async def get_connection():
    """Obtener conexión a PostgreSQL con secret auditado (HU-05)"""
    return await asyncpg.connect(_get_async_pg_url())

def convert_uuid_to_str(data: Any) -> Any:
    """Convertir UUIDs y fechas a strings en diccionarios o listas"""
    if isinstance(data, dict):
        return {k: convert_value(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_uuid_to_str(item) for item in data]
    else:
        return convert_value(data)

def convert_value(value: Any) -> Any:
    """Convertir un valor individual (UUID, fecha, etc.) a string si es necesario"""
    if isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, dict):
        return convert_uuid_to_str(value)
    elif isinstance(value, list):
        return [convert_uuid_to_str(item) for item in value]
    return value

async def get_products(category: Optional[str] = None, available: Optional[bool] = None) -> List[Dict[str, Any]]:
    """Obtener lista de productos (con cache de 120s)"""
    # Cache key basado en filtros
    cache_key = f"products:all:cat={category}:avail={available}"

    # Intentar obtener del cache
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    conn = await get_connection()
    try:
        query = "SELECT id, name, description, price, image, category, \"isAvailable\", \"createdAt\" FROM products WHERE 1=1"
        params = []

        if category:
            query += " AND category = $1"
            params.append(category)

        if available is not None:
            param_index = len(params) + 1
            query += f" AND \"isAvailable\" = ${param_index}"
            params.append(available)

        query += " ORDER BY \"createdAt\" DESC"

        rows = await conn.fetch(query, *params)
        products = [convert_uuid_to_str(dict(row)) for row in rows]

        # Guardar en cache (TTL 120s para catálogo)
        _cache.set(cache_key, products, ttl_seconds=120)

        return products
    finally:
        await conn.close()

async def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Obtener producto por ID (con cache de 180s)"""
    cache_key = CacheKeys.product_by_id(product_id)

    # Intentar obtener del cache
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            'SELECT id, name, description, price, image, category, "isAvailable" FROM products WHERE id = $1',
            product_id
        )
        product = convert_uuid_to_str(dict(row)) if row else None

        # Guardar en cache solo si existe (TTL 180s)
        if product:
            _cache.set(cache_key, product, ttl_seconds=180)

        return product
    finally:
        await conn.close()

async def create_order(
    user_id: str,
    address_id: str,
    items: List[Dict],
    total: float,
    payment_method: str = "CASH",
    notes: Optional[str] = None,
    coupon_code: Optional[str] = None,
    discount_applied: float = 0.0,
    status: str = "PENDING",
    scheduled_for: Optional[datetime] = None,
    order_id: Optional[str] = None  # 👈 HU-04: Permitir ID predefinido
) -> Dict[str, Any]:
    """
    Crear pedido en la base de datos.

    Soporta:
    - Pedidos programados (status=SCHEDULED, scheduledFor)
    - Order ID predefinido (HU-04: confirmación inmediata)
    """
    conn = await get_connection()
    try:
        async with conn.transaction():
            # HU-04: Si se proporciona order_id, usarlo; sino, generar uno nuevo
            if order_id:
                await conn.execute(
                    """
                    INSERT INTO orders (
                        id, "userId", "addressId", status, total, "paymentMethod", notes,
                        coupon_code, discount_applied, "scheduledFor", "createdAt", "updatedAt"
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
                    """,
                    order_id, user_id, address_id, status, total, payment_method, notes,
                    coupon_code, discount_applied, scheduled_for
                )
            else:
                order_id = await conn.fetchval(
                    """
                    INSERT INTO orders (
                        id, "userId", "addressId", status, total, "paymentMethod", notes,
                        coupon_code, discount_applied, "scheduledFor", "createdAt", "updatedAt"
                    )
                    VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
                    RETURNING id
                    """,
                    user_id, address_id, status, total, payment_method, notes,
                    coupon_code, discount_applied, scheduled_for
                )

            for item in items:
                await conn.execute(
                    """
                    INSERT INTO order_items (id, "orderId", "productId", quantity, price, "createdAt")
                    VALUES (gen_random_uuid(), $1, $2, $3, $4, NOW())
                    """,
                    order_id, item["productId"], item["quantity"], item["price"]
                )

            order = await conn.fetchrow(
                """
                SELECT id, "userId", "addressId", status, total, "paymentMethod", notes,
                       coupon_code, discount_applied, "scheduledFor", "createdAt", "updatedAt"
                FROM orders WHERE id = $1
                """,
                order_id
            )

            if not order:
                return None

            order_dict = convert_uuid_to_str(dict(order))

            order_items = await conn.fetch(
                """
                SELECT "productId", quantity, price
                FROM order_items
                WHERE "orderId" = $1
                """,
                order_id
            )

            items_list = []
            for item in order_items:
                item_dict = convert_uuid_to_str(dict(item))
                if 'productId' not in item_dict and 'product_id' in item_dict:
                    item_dict['productId'] = item_dict.pop('product_id')
                items_list.append(item_dict)

            order_dict['items'] = items_list
            return order_dict
    finally:
        await conn.close()


async def get_coupon_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Obtener cupón por código"""
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            """
            SELECT id, code, description, discount_type, amount, percentage, valid_from, valid_to,
                   max_uses, per_user_limit, applicable_user_id, is_active
            FROM coupons WHERE code = $1
            """,
            code
        )
        return convert_uuid_to_str(dict(row)) if row else None
    finally:
        await conn.close()

async def validate_coupon_for_user(code: str, user_id: str, now_iso: Optional[str] = None) -> Dict[str, Any]:
    """Validar cupón: existencia, vigencia, aplicabilidad y límites de uso"""
    from datetime import datetime
    conn = await get_connection()
    try:
        coupon = await conn.fetchrow(
            """
            SELECT c.id, c.code, c.discount_type, c.amount, c.percentage, c.valid_from, c.valid_to,
                   c.max_uses, c.per_user_limit, c.applicable_user_id, c.is_active,
                   (SELECT COUNT(*) FROM coupon_usages cu WHERE cu.coupon_id = c.id) as total_uses,
                   (SELECT COUNT(*) FROM coupon_usages cu WHERE cu.coupon_id = c.id AND cu.user_id = $2) as user_uses
            FROM coupons c WHERE c.code = $1
            """,
            code, user_id
        )
        if not coupon:
            return {"valid": False, "reason": "Cupón no existe"}
        c = dict(coupon)
        if not c.get("is_active"):
            return {"valid": False, "reason": "Cupón inactivo"}
        now = datetime.fromisoformat(now_iso) if now_iso else datetime.utcnow()
        if c.get("valid_from") and now < c["valid_from"]:
            return {"valid": False, "reason": "Cupón aún no está vigente"}
        if c.get("valid_to") and now > c["valid_to"]:
            return {"valid": False, "reason": "Cupón expirado"}
        if c.get("applicable_user_id") and str(c["applicable_user_id"]) != str(user_id):
            return {"valid": False, "reason": "Cupón no aplica a este usuario"}
        if c.get("max_uses") is not None and c["total_uses"] >= c["max_uses"]:
            return {"valid": False, "reason": "Cupón alcanzó el máximo de usos"}
        if c.get("per_user_limit") is not None and c["user_uses"] >= c["per_user_limit"]:
            return {"valid": False, "reason": "Cupón ya usado por el usuario"}
        return {"valid": True, "coupon": convert_uuid_to_str(c)}
    finally:
        await conn.close()

async def register_coupon_usage(coupon_id: str, user_id: str, order_id: str) -> None:
    """Registrar uso de cupón"""
    conn = await get_connection()
    try:
        await conn.execute(
            """
            INSERT INTO coupon_usages (id, coupon_id, user_id, order_id, used_at)
            VALUES (gen_random_uuid(), $1, $2, $3, NOW())
            """,
            coupon_id, user_id, order_id
        )
    finally:
        await conn.close()

async def get_order_status(order_id: str) -> Optional[Dict[str, Any]]:
    """Obtener estado de un pedido (incluye scheduledFor)"""
    conn = await get_connection()
    try:
        order = await conn.fetchrow(
            """
            SELECT id, status, total, "paymentMethod", coupon_code, discount_applied, "scheduledFor", "createdAt", "updatedAt"
            FROM orders WHERE id = $1
            """,
            order_id
        )
        return convert_uuid_to_str(dict(order)) if order else None
    finally:
        await conn.close()


async def get_user_orders(user_id: str) -> List[Dict[str, Any]]:
    """Obtener todas las órdenes de un usuario específico (incluye scheduledFor)"""
    conn = await get_connection()
    try:
        orders = await conn.fetch(
            """
            SELECT
                o.id,
                o.status,
                o.total,
                o."paymentMethod",
                o.notes,
                o.coupon_code,
                o.discount_applied,
                o."scheduledFor",
                o."createdAt",
                o."updatedAt",
                o."addressId"
            FROM orders o
            WHERE o."userId" = $1
            ORDER BY o."createdAt" DESC
            """,
            user_id
        )

        orders_list = [convert_uuid_to_str(dict(row)) for row in orders]

        for order in orders_list:
            items = await conn.fetch(
                """
                SELECT
                    oi.id,
                    oi.quantity,
                    oi.price,
                    p.id as product_id,
                    p.name as product_name,
                    p.description as product_description,
                    p.category as product_category
                FROM order_items oi
                JOIN products p ON oi."productId" = p.id
                WHERE oi."orderId" = $1
                ORDER BY oi."createdAt"
                """,
                order['id']
            )
            order['items'] = [convert_uuid_to_str(dict(item)) for item in items]

        return orders_list
    finally:
        await conn.close()

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario por email (con cache de 300s)"""
    cache_key = CacheKeys.user_by_email(email)

    # Intentar obtener del cache
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    conn = await get_connection()
    try:
        user = await conn.fetchrow(
            'SELECT id, email, password, name, phone, role FROM users WHERE email = $1',
            email
        )
        user_data = convert_uuid_to_str(dict(user)) if user else None

        # Guardar en cache solo si existe (TTL 300s)
        if user_data:
            _cache.set(cache_key, user_data, ttl_seconds=300)

        return user_data
    finally:
        await conn.close()

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario por ID"""
    conn = await get_connection()
    try:
        user = await conn.fetchrow(
            'SELECT id, email, name, phone, role FROM users WHERE id = $1',
            user_id
        )
        return convert_uuid_to_str(dict(user)) if user else None
    finally:
        await conn.close()

async def create_user(email: str, hashed_password: str, name: str, phone: Optional[str] = None) -> Dict[str, Any]:
    """Crear nuevo usuario (invalida cache)"""
    conn = await get_connection()
    try:
        user_id = await conn.fetchval(
            """
            INSERT INTO users (id, email, password, name, phone, role, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, NOW(), NOW())
            RETURNING id
            """,
            email, hashed_password, name, phone, "CUSTOMER"
        )

        user = await conn.fetchrow(
            'SELECT id, email, name, phone, role FROM users WHERE id = $1',
            user_id
        )

        # Invalidar cache del usuario por email (aunque es nuevo, previene inconsistencias)
        cache_key = CacheKeys.user_by_email(email)
        _cache.delete(cache_key)

        return convert_uuid_to_str(dict(user)) if user else None
    finally:
        await conn.close()

async def get_all_orders() -> List[Dict[str, Any]]:
    """Obtener todos los pedidos (admin) incluyendo scheduledFor"""
    conn = await get_connection()
    try:
        orders = await conn.fetch(
            """
            SELECT
                o.id,
                o.status,
                o.total,
                o."paymentMethod",
                o.notes,
                o.coupon_code,
                o.discount_applied,
                o."scheduledFor",
                o."createdAt",
                o."updatedAt",
                u.id as customer_id,
                u.name as customer_name,
                u.email as customer_email,
                u.phone as customer_phone,
                a.street as delivery_street,
                a.city as delivery_city,
                a.state as delivery_state,
                a."zipCode" as delivery_zipcode,
                a.country as delivery_country,
                a.instructions as delivery_instructions
            FROM orders o
            JOIN users u ON o."userId" = u.id
            JOIN addresses a ON o."addressId" = a.id
            ORDER BY o."createdAt" DESC
            """
        )

        orders_list = [convert_uuid_to_str(dict(row)) for row in orders]

        for order in orders_list:
            items = await conn.fetch(
                """
                SELECT
                    oi.id,
                    oi.quantity,
                    oi.price,
                    p.id as product_id,
                    p.name as product_name,
                    p.description as product_description,
                    p.category as product_category
                FROM order_items oi
                JOIN products p ON oi."productId" = p.id
                WHERE oi."orderId" = $1
                ORDER BY oi."createdAt"
                """,
                order['id']
            )
            order['items'] = [convert_uuid_to_str(dict(item)) for item in items]

        return orders_list
    finally:
        await conn.close()

async def update_order_status(order_id: str, status: str) -> Optional[Dict[str, Any]]:
    """Actualizar estado de un pedido"""
    conn = await get_connection()
    try:
        order = await conn.fetchrow(
            """
            UPDATE orders SET status = $1, "updatedAt" = NOW()
            WHERE id = $2
            RETURNING id, status, total, "paymentMethod", coupon_code, discount_applied, "createdAt", "updatedAt"
            """,
            status, order_id
        )
        return convert_uuid_to_str(dict(order)) if order else None
    finally:
        await conn.close()

async def create_address(user_id: str, street: str, city: str, state: str, zip_code: str, country: str = "Colombia", is_default: bool = False, instructions: Optional[str] = None) -> Dict[str, Any]:
    """Crear nueva dirección (invalida cache)"""
    conn = await get_connection()
    try:
        # Primero, si is_default es True, desmarcar cualquier otra dirección como predeterminada
        if is_default:
            await conn.execute(
                'UPDATE addresses SET "isDefault" = false WHERE "userId" = $1',
                user_id
            )

        # Insertar la nueva dirección
        address_id = await conn.fetchval(
            """
            INSERT INTO addresses (id, "userId", street, city, state, "zipCode", country, "isDefault", instructions, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
            RETURNING id
            """,
            user_id, street, city, state, zip_code, country, is_default, instructions
        )

        # Obtener la dirección recién creada
        address = await conn.fetchrow(
            'SELECT id, "userId", street, city, state, "zipCode", country, "isDefault", instructions FROM addresses WHERE id = $1',
            address_id
        )

        # Invalidar cache de direcciones del usuario
        cache_key = CacheKeys.user_addresses(user_id)
        _cache.delete(cache_key)

        return convert_uuid_to_str(dict(address)) if address else None
    finally:
        await conn.close()

async def get_user_addresses(user_id: str) -> List[Dict[str, Any]]:
    """Obtener direcciones de un usuario (con cache de 90s)"""
    cache_key = CacheKeys.user_addresses(user_id)

    # Intentar obtener del cache
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    conn = await get_connection()
    try:
        addresses = await conn.fetch(
            """
            SELECT id, "userId", street, city, state, "zipCode", country, "isDefault", instructions, "createdAt", "updatedAt"
            FROM addresses WHERE "userId" = $1
            ORDER BY "isDefault" DESC, "createdAt" DESC
            """,
            user_id
        )
        addresses_list = [convert_uuid_to_str(dict(row)) for row in addresses]

        # Guardar en cache (TTL 90s)
        _cache.set(cache_key, addresses_list, ttl_seconds=90)

        return addresses_list
    finally:
        await conn.close()

async def get_address_by_id(address_id: str) -> Optional[Dict[str, Any]]:
    """Obtener dirección por ID"""
    conn = await get_connection()
    try:
        address = await conn.fetchrow(
            'SELECT id, "userId", street, city, state, "zipCode", country, "isDefault", instructions FROM addresses WHERE id = $1',
            address_id
        )
        return convert_uuid_to_str(dict(address)) if address else None
    finally:
        await conn.close()

async def create_product(name: str, description: Optional[str], price: float, category: str, image: Optional[str] = None, is_available: bool = True) -> Dict[str, Any]:
    """Crear nuevo producto"""
    conn = await get_connection()
    try:
        product_id = await conn.fetchval(
            """
            INSERT INTO products (id, name, description, price, image, category, "isAvailable", "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, NOW(), NOW())
            RETURNING id
            """,
            name, description, price, image, category, is_available
        )

        product = await conn.fetchrow(
            'SELECT id, name, description, price, image, category, "isAvailable", "createdAt", "updatedAt" FROM products WHERE id = $1',
            product_id
        )
        return convert_uuid_to_str(dict(product)) if product else None
    finally:
        await conn.close()

async def list_coupons() -> List[Dict[str, Any]]:
    """Listar cupones"""
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            """
            SELECT id, code, description, discount_type, amount, percentage, valid_from, valid_to,
                   max_uses, per_user_limit, applicable_user_id, is_active, "createdAt", "updatedAt"
            FROM coupons
            ORDER BY "createdAt" DESC
            """
        )
        return [convert_uuid_to_str(dict(r)) for r in rows]
    finally:
        await conn.close()

async def create_coupon(code: str, description: Optional[str], discount_type: str, amount: Optional[float], percentage: Optional[float],
                        valid_from: Optional[str], valid_to: Optional[str], max_uses: Optional[int], per_user_limit: Optional[int],
                        applicable_user_id: Optional[str], is_active: bool = True) -> Dict[str, Any]:
    """Crear cupón"""
    conn = await get_connection()
    try:
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
        row = await conn.fetchrow(
            """
            SELECT id, code, description, discount_type, amount, percentage, valid_from, valid_to,
                   max_uses, per_user_limit, applicable_user_id, is_active, "createdAt", "updatedAt"
            FROM coupons WHERE id = $1
            """,
            coupon_id
        )
        return convert_uuid_to_str(dict(row)) if row else None
    finally:
        await conn.close()

async def update_coupon(coupon_id: str, **fields) -> Optional[Dict[str, Any]]:
    """Actualizar cupón"""
    if not fields:
        return None
    allowed = {"description", "discount_type", "amount", "percentage", "valid_from", "valid_to",
               "max_uses", "per_user_limit", "applicable_user_id", "is_active"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return None
    conn = await get_connection()
    try:
        set_parts = []
        values = []
        idx = 1
        for k, v in updates.items():
            set_parts.append(f"{k} = ${idx}")
            values.append(v)
            idx += 1
        set_clause = ", "+" ".join([])  # placeholder para estilo consistente
        set_clause = ", ".join(set_parts) + ", \"updatedAt\" = NOW()"
        values.append(coupon_id)
        query = f"UPDATE coupons SET {set_clause} WHERE id = ${idx} RETURNING id, code, description, discount_type, amount, percentage, valid_from, valid_to, max_uses, per_user_limit, applicable_user_id, is_active, \"createdAt\", \"updatedAt\""
        row = await conn.fetchrow(query, *values)
        return convert_uuid_to_str(dict(row)) if row else None
    finally:
        await conn.close()

async def delete_coupon(coupon_id: str) -> bool:
    """Eliminar cupón"""
    conn = await get_connection()
    try:
        result = await conn.execute("DELETE FROM coupons WHERE id = $1", coupon_id)
        return result.upper().startswith("DELETE")
    finally:
        await conn.close()

async def update_product(product_id: str, name: Optional[str] = None, description: Optional[str] = None, price: Optional[float] = None, category: Optional[str] = None, image: Optional[str] = None, is_available: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    """Actualizar producto existente"""
    conn = await get_connection()
    try:
        # Obtener producto actual
        current_product = await conn.fetchrow(
            'SELECT name, description, price, category, image, "isAvailable" FROM products WHERE id = $1',
            product_id
        )

        if not current_product:
            return None

        # Usar valores actuales si no se proporcionan nuevos
        updated_name = name if name is not None else current_product['name']
        updated_description = description if description is not None else current_product['description']
        updated_price = price if price is not None else current_product['price']
        updated_category = category if category is not None else current_product['category']
        updated_image = image if image is not None else current_product['image']
        updated_available = is_available if is_available is not None else current_product['isAvailable']

        # Actualizar producto
        product = await conn.fetchrow(
            """
            UPDATE products
            SET name = $1, description = $2, price = $3, category = $4, image = $5, "isAvailable" = $6, "updatedAt" = NOW()
            WHERE id = $7
            RETURNING id, name, description, price, image, category, "isAvailable", "createdAt", "updatedAt"
            """,
            updated_name, updated_description, updated_price, updated_category, updated_image, updated_available, product_id
        )

        return convert_uuid_to_str(dict(product)) if product else None
    finally:
        await conn.close()

async def get_all_customers_with_addresses() -> List[Dict[str, Any]]:
    """Obtener todos los clientes (CUSTOMER role) con sus direcciones (admin)"""
    conn = await get_connection()
    try:
        # Obtener todos los usuarios con rol CUSTOMER
        customers = await conn.fetch(
            """
            SELECT
                u.id,
                u.email,
                u.name,
                u.phone,
                u.role,
                u."createdAt",
                u."updatedAt"
            FROM users u
            WHERE u.role = 'CUSTOMER'
            ORDER BY u."createdAt" DESC
            """
        )

        customers_list = [convert_uuid_to_str(dict(row)) for row in customers]

        # Para cada cliente, obtener sus direcciones
        for customer in customers_list:
            addresses = await conn.fetch(
                """
                SELECT
                    id,
                    "userId",
                    street,
                    city,
                    state,
                    "zipCode",
                    country,
                    "isDefault",
                    instructions,
                    "createdAt",
                    "updatedAt"
                FROM addresses
                WHERE "userId" = $1
                ORDER BY "isDefault" DESC, "createdAt" DESC
                """,
                customer['id']
            )
            customer['addresses'] = [convert_uuid_to_str(dict(addr)) for addr in addresses]

        return customers_list
    finally:
        await conn.close()

async def get_due_scheduled_order_ids(limit: int = 50) -> List[str]:
    """IDs de pedidos programados que ya deben liberarse"""
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            """
            SELECT id
            FROM orders
            WHERE status = 'SCHEDULED'
              AND "scheduledFor" IS NOT NULL
              AND "scheduledFor" <= NOW()
            ORDER BY "scheduledFor" ASC
            LIMIT $1
            """,
            limit
        )
        return [str(r["id"]) for r in rows]
    finally:
        await conn.close()

async def claim_scheduled_order(order_id: str) -> bool:
    """
    Reclama un pedido programado para liberarlo (evita doble disparo).
    Pasa SCHEDULED -> PENDING solo si ya está vencido.
    """
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            """
            UPDATE orders
            SET status = 'PENDING', "updatedAt" = NOW()
            WHERE id = $1
              AND status = 'SCHEDULED'
              AND "scheduledFor" IS NOT NULL
              AND "scheduledFor" <= NOW()
            RETURNING id
            """,
            order_id
        )
        return bool(row)
    finally:
        await conn.close()

async def get_order_by_id_full(order_id: str) -> Optional[Dict[str, Any]]:
    """Orden completa para publicar a Rabbit (incluye items)"""
    conn = await get_connection()
    try:
        order = await conn.fetchrow(
            """
            SELECT id, "userId", "addressId", status, total, "paymentMethod", notes,
                   coupon_code, discount_applied, "scheduledFor", "createdAt", "updatedAt"
            FROM orders
            WHERE id = $1
            """,
            order_id
        )
        if not order:
            return None
        order_dict = convert_uuid_to_str(dict(order))

        order_items = await conn.fetch(
            """
            SELECT "productId", quantity, price
            FROM order_items
            WHERE "orderId" = $1
            """,
            order_id
        )
        items_list = []
        for item in order_items:
            item_dict = convert_uuid_to_str(dict(item))
            if 'productId' not in item_dict and 'product_id' in item_dict:
                item_dict['productId'] = item_dict.pop('product_id')
            items_list.append(item_dict)

        order_dict["items"] = items_list
        return order_dict
    finally:
        await conn.close()


# ==================== REVIEWS FUNCTIONS ====================

async def user_can_review_product(user_id: str, product_id: str) -> Optional[str]:
    """
    Verifica si el usuario puede hacer una reseña de un producto.
    Solo puede reseñar si ha recibido el producto (status=DELIVERED).
    Retorna el order_id si es válido, None si no puede reseñar.
    """
    conn = await get_connection()
    try:
        # Buscar un pedido DELIVERED que contenga este producto para este usuario
        order = await conn.fetchrow(
            """
            SELECT o.id
            FROM orders o
            JOIN order_items oi ON oi."orderId" = o.id
            WHERE o."userId" = $1
              AND oi."productId" = $2
              AND o.status = 'DELIVERED'
            LIMIT 1
            """,
            user_id, product_id
        )
        return str(order['id']) if order else None
    finally:
        await conn.close()


async def create_review(
    user_id: str,
    product_id: str,
    order_id: str,
    rating: int,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crear una reseña para un producto.
    Lanza excepción si ya existe una reseña del usuario para ese producto.
    """
    conn = await get_connection()
    try:
        review_id = await conn.fetchval(
            """
            INSERT INTO reviews (id, "userId", "productId", "orderId", rating, comment, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, NOW(), NOW())
            RETURNING id
            """,
            user_id, product_id, order_id, rating, comment
        )

        review = await conn.fetchrow(
            """
            SELECT
                r.id,
                r."userId",
                r."productId",
                r."orderId",
                r.rating,
                r.comment,
                r."createdAt",
                u.name as user_name
            FROM reviews r
            JOIN users u ON r."userId" = u.id
            WHERE r.id = $1
            """,
            review_id
        )
        return convert_uuid_to_str(dict(review)) if review else None
    finally:
        await conn.close()


async def get_product_reviews(product_id: str) -> Dict[str, Any]:
    """
    Obtener todas las reseñas de un producto con estadísticas.
    Retorna: {reviews: [...], average: float, total: int}
    """
    conn = await get_connection()
    try:
        # Obtener todas las reseñas del producto
        reviews = await conn.fetch(
            """
            SELECT
                r.id,
                r."userId",
                r."productId",
                r."orderId",
                r.rating,
                r.comment,
                r."createdAt",
                u.name as user_name
            FROM reviews r
            JOIN users u ON r."userId" = u.id
            WHERE r."productId" = $1
            ORDER BY r."createdAt" DESC
            """,
            product_id
        )

        reviews_list = [convert_uuid_to_str(dict(row)) for row in reviews]

        # Calcular estadísticas
        total = len(reviews_list)
        average = sum(r['rating'] for r in reviews_list) / total if total > 0 else 0

        return {
            "reviews": reviews_list,
            "average": round(average, 1),
            "total": total
        }
    finally:
        await conn.close()


async def check_user_reviewed_product(user_id: str, product_id: str) -> bool:
    """
    Verifica si el usuario ya ha hecho una reseña de este producto.
    """
    conn = await get_connection()
    try:
        review = await conn.fetchrow(
            """
            SELECT id FROM reviews
            WHERE "userId" = $1 AND "productId" = $2
            LIMIT 1
            """,
            user_id, product_id
        )
        return review is not None
    finally:
        await conn.close()


async def get_user_favorites(user_id: str) -> List[Dict[str, Any]]:
    """Obtener lista de favoritos de un usuario (incluye info del producto)"""
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            """
            SELECT f.id, f."productId", p.name as product_name, p.description as product_description, p.price, p.image, p.category
            FROM favorites f
            JOIN products p ON f."productId" = p.id
            WHERE f."userId" = $1
            ORDER BY f."createdAt" DESC
            """,
            user_id
        )
        favorites = []
        for r in rows:
            d = convert_uuid_to_str(dict(r))
            # normalize keys similar to frontend expectations
            d['id'] = d.get('id')
            d['productId'] = d.get('productId')
            favorites.append(d)
        return favorites
    finally:
        await conn.close()


async def add_favorite(user_id: str, product_id: str) -> Optional[Dict[str, Any]]:
    """Agregar favorito (si no existe) y retornar el registro con info del producto"""
    conn = await get_connection()
    try:
        # Verificar existencia
        existing = await conn.fetchrow(
            'SELECT id FROM favorites WHERE "userId" = $1 AND "productId" = $2',
            user_id, product_id
        )
        if existing:
            # retornar el favorito existente
            fav = await conn.fetchrow(
                'SELECT id, "userId", "productId", "createdAt" FROM favorites WHERE id = $1',
                existing['id']
            )
            return convert_uuid_to_str(dict(fav)) if fav else None

        fav_id = await conn.fetchval(
            'INSERT INTO favorites (id, "userId", "productId", "createdAt") VALUES (gen_random_uuid(), $1, $2, NOW()) RETURNING id',
            user_id, product_id
        )

        fav = await conn.fetchrow(
            """
            SELECT f.id, f."userId", f."productId", f."createdAt", p.name as product_name, p.description as product_description, p.price, p.image
            FROM favorites f
            JOIN products p ON f."productId" = p.id
            WHERE f.id = $1
            """,
            fav_id
        )
        return convert_uuid_to_str(dict(fav)) if fav else None
    finally:
        await conn.close()


async def remove_favorite(user_id: str, product_id: str) -> bool:
    """Remover favorito por usuario y producto"""
    conn = await get_connection()
    try:
        result = await conn.execute(
            'DELETE FROM favorites WHERE "userId" = $1 AND "productId" = $2',
            user_id, product_id
        )
        return result.upper().startswith('DELETE')
    finally:
        await conn.close()


async def check_favorite(user_id: str, product_id: str) -> bool:
    """Verificar si un producto está en favoritos de un usuario"""
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            'SELECT id FROM favorites WHERE "userId" = $1 AND "productId" = $2 LIMIT 1',
            user_id, product_id
        )
        return bool(row)
    finally:
        await conn.close()


async def get_all_reviews() -> list:
    """
    Obtener todas las reseñas del sistema con información de usuario y producto.
    """
    conn = await get_connection()
    try:
        reviews = await conn.fetch(
            """
            SELECT
                r.id,
                r."userId",
                r."productId",
                r."orderId",
                r.rating,
                r.comment,
                r."createdAt",
                u.name as user_name,
                u.email as user_email,
                p.name as product_name,
                p.price as product_price
            FROM reviews r
            JOIN users u ON r."userId" = u.id
            JOIN products p ON r."productId" = p.id
            ORDER BY r."createdAt" DESC
            """
        )

        return [convert_uuid_to_str(dict(row)) for row in reviews]
    finally:
        await conn.close()


async def delete_review(review_id: str) -> bool:
    """
    Eliminar una reseña (admin only)
    """
    conn = await get_connection()
    try:
        result = await conn.execute(
            'DELETE FROM reviews WHERE id = $1',
            review_id
        )
        return result.upper().startswith('DELETE')
    finally:
        await conn.close()
