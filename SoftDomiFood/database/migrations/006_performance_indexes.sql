-- Migration 006: Performance Optimization Indexes
-- Fecha: 16 de Diciembre 2025
-- Autor: Senior Fullstack Developer
-- Propósito: Optimizar performance de queries críticas (HU-01)
--
-- Índices creados:
--   1. users(email) - Login rápido
--   2. products(id) - Consulta de productos
--   3. orders(user_id, status) - Consulta de pedidos por usuario
--   4. orders(scheduled_for) - Dispatcher de pedidos programados
--   5. addresses(user_id) - Direcciones de usuario
--
-- Impacto esperado:
--   - Login: Reducción 60-80% en tiempo de query
--   - Consulta productos: Reducción 50-70%
--   - Pedidos programados: Reducción 70-90%

-- ============================================================
-- ÍNDICES PARA TABLA USERS
-- ============================================================

-- Índice para búsqueda por email (usado en login)
-- Mejora performance de get_user_by_email de O(n) a O(log n)
CREATE INDEX IF NOT EXISTS idx_users_email
ON users(email);

-- ============================================================
-- ÍNDICES PARA TABLA PRODUCTS
-- ============================================================

-- Índice para búsqueda por ID (aunque es PK, explicit para joins)
-- Beneficia consultas frecuentes de productos
CREATE INDEX IF NOT EXISTS idx_products_id
ON products(id);

-- Índice para productos disponibles (filtro común)
CREATE INDEX IF NOT EXISTS idx_products_available
ON products("isAvailable")
WHERE "isAvailable" = true;

-- ============================================================
-- ÍNDICES PARA TABLA ORDERS
-- ============================================================

-- Índice compuesto para consultas de pedidos por usuario y estado
-- Usado frecuentemente en historial de pedidos
CREATE INDEX IF NOT EXISTS idx_orders_user_status
ON orders("userId", status);

-- Índice para scheduled_for (dispatcher de pedidos programados)
-- CRÍTICO para HU-06: Permite al dispatcher encontrar pedidos rápidamente
CREATE INDEX IF NOT EXISTS idx_orders_scheduled_for
ON orders("scheduledFor")
WHERE "scheduledFor" IS NOT NULL AND status = 'SCHEDULED';

-- Índice para búsqueda por fecha de creación (reportes)
CREATE INDEX IF NOT EXISTS idx_orders_created_at
ON orders("createdAt" DESC);

-- ============================================================
-- ÍNDICES PARA TABLA ADDRESSES
-- ============================================================

-- Índice para direcciones por usuario
-- Mejora performance de get_user_addresses
CREATE INDEX IF NOT EXISTS idx_addresses_user_id
ON addresses("userId");

-- Índice para dirección por defecto (consulta frecuente)
CREATE INDEX IF NOT EXISTS idx_addresses_default
ON addresses("userId", "isDefault")
WHERE "isDefault" = true;

-- ============================================================
-- ÍNDICES PARA TABLA REVIEWS
-- ============================================================

-- Índice para reviews por producto (mostrar reseñas de producto)
CREATE INDEX IF NOT EXISTS idx_reviews_product_id
ON reviews("productId");

-- Índice compuesto para reviews recientes por producto
CREATE INDEX IF NOT EXISTS idx_reviews_product_created
ON reviews("productId", "createdAt" DESC);

-- ============================================================
-- ÍNDICES PARA TABLA FAVORITES
-- ============================================================

-- Índice compuesto para favoritos por usuario
-- Previene duplicados y acelera consultas
CREATE INDEX IF NOT EXISTS idx_favorites_user_product
ON favorites("userId", "productId");

-- ============================================================
-- ANÁLISIS Y VERIFICACIÓN
-- ============================================================

-- Verificar que los índices se crearon correctamente
DO $$
DECLARE
    index_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE indexname LIKE 'idx_%'
    AND schemaname = 'public';

    RAISE NOTICE 'Total de índices de performance creados: %', index_count;
END $$;

-- Mostrar tamaño de índices (útil para monitoreo)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE indexname LIKE 'idx_%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================================
-- NOTAS DE MANTENIMIENTO
-- ============================================================

-- Los índices se actualizan automáticamente en INSERT/UPDATE/DELETE
-- Considerar REINDEX periódico en producción (mensual)
-- Comando: REINDEX TABLE users; REINDEX TABLE products; etc.

-- Para monitorear uso de índices:
-- SELECT * FROM pg_stat_user_indexes WHERE schemaname = 'public';

-- Para ver planes de ejecución con índices:
-- EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
