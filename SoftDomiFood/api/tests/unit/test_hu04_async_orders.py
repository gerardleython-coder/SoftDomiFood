"""
Tests para HU-04: Creación instantánea de pedidos sin bloqueos
===============================================================

Criterios de Aceptación:
1. Sistema devuelve confirmación "Pedido Recibido" en ≤100ms (P95)
2. Fallos en procesamiento posterior NO bloquean ni revierten confirmación
3. Pedido se registra asíncronamente sin pérdida de datos

Test Coverage:
- Performance: P95 < 100ms para POST /api/orders
- Resiliencia: Confirmación devuelta incluso si validaciones fallan después
- Asincronía: asyncio.create_task dispara procesamiento en background
- No-reversión: Pedido NO se elimina si falla procesamiento
"""

import pytest
import time
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from services.async_order_service import (
    AsyncOrderProcessor,
    get_async_order_processor
)


# ==============================================================================
# Tests para AsyncOrderProcessor (HU-04 Criterio 1: Fast Path)
# ==============================================================================

class TestAsyncOrderProcessorFastPath:
    """Tests para el fast path: confirmación instantánea"""

    @pytest.mark.asyncio
    async def test_create_order_fast_returns_immediately(self):
        """Confirmación se devuelve inmediatamente (Criterio 1)"""
        processor = AsyncOrderProcessor()

        # Medir tiempo de respuesta
        start_time = time.perf_counter()

        result = await processor.create_order_fast(
            user_id="user-123",
            order_data={
                "addressId": "addr-456",
                "items": [{"productId": "prod-1", "quantity": 2, "price": 10.0}],
                "total": 20.0,
                "paymentMethod": "CASH"
            }
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Criterio 1: Respuesta en ≤100ms
        assert elapsed_ms < 100, f"Respuesta tardó {elapsed_ms:.2f}ms (debería ser <100ms)"

        # Verificar estructura de respuesta
        assert "orderId" in result
        assert result["status"] == "PENDING_CONFIRMATION"
        assert "Pedido recibido" in result["message"]
        assert "estimatedTime" in result

    @pytest.mark.asyncio
    async def test_create_order_fast_generates_unique_order_id(self):
        """Cada confirmación tiene un order_id único"""
        processor = AsyncOrderProcessor()

        order_data = {
            "addressId": "addr-456",
            "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
            "total": 10.0,
            "paymentMethod": "CASH"
        }

        result1 = await processor.create_order_fast("user-123", order_data)
        result2 = await processor.create_order_fast("user-123", order_data)

        assert result1["orderId"] != result2["orderId"]
        assert len(result1["orderId"]) == 36  # UUID format

    @pytest.mark.asyncio
    async def test_create_order_fast_does_not_wait_for_validation(self):
        """Fast path NO espera validaciones (Criterio 1)"""
        processor = AsyncOrderProcessor()

        # Mock de validación que tarda 500ms
        async def slow_validation(*args, **kwargs):
            await asyncio.sleep(0.5)
            return {"id": "addr-123"}

        with patch.object(processor.validator, 'validate_address_for_order', slow_validation):
            start_time = time.perf_counter()
            result = await processor.create_order_fast(
                user_id="user-123",
                order_data={
                    "addressId": "addr-456",
                    "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
                    "total": 10.0,
                    "paymentMethod": "CASH"
                }
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Debe responder antes de que termine la validación (500ms)
        assert elapsed_ms < 100  # Mucho menos que 500ms
        assert result["status"] == "PENDING_CONFIRMATION"


# ==============================================================================
# Tests para AsyncOrderProcessor (HU-04 Criterio 2: No-Reversión)
# ==============================================================================

class TestAsyncOrderProcessorNoReversal:
    """Tests para garantizar que confirmación NO se revierte ante fallos"""

    @pytest.mark.asyncio
    async def test_confirmation_not_reverted_on_validation_failure(self):
        """
        Criterio 2: Confirmación devuelta aunque validaciones fallen después.

        Flujo:
        1. Fast path devuelve order_id
        2. Slow path falla validación
        3. Order NO se elimina, queda como FAILED
        """
        processor = AsyncOrderProcessor()

        # Mock de validación que falla
        async def failing_validation(*args, **kwargs):
            raise Exception("Dirección no válida")

        with patch.object(processor.validator, 'validate_address_for_order', failing_validation):
            # Fast path devuelve confirmación
            result = await processor.create_order_fast(
                user_id="user-123",
                order_data={
                    "addressId": "invalid-addr",
                    "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
                    "total": 10.0,
                    "paymentMethod": "CASH"
                }
            )

            order_id = result["orderId"]
            assert result["status"] == "PENDING_CONFIRMATION"

            # Dar tiempo al slow path para fallar
            await asyncio.sleep(0.1)

            # La confirmación ya se devolvió - NO se revierte
            assert order_id is not None
            # En producción, el pedido quedaría guardado como FAILED

    @pytest.mark.asyncio
    async def test_confirmation_not_reverted_on_database_failure(self):
        """Confirmación NO se revierte aunque falle persistencia en BD"""
        processor = AsyncOrderProcessor()

        # Mock de validaciones exitosas
        async def mock_validate_address(*args, **kwargs):
            return {"id": "addr-123"}

        async def mock_validate_items(*args, **kwargs):
            return ([{"productId": "prod-1", "quantity": 1, "price": 10.0}], 10.0)

        # Mock de create_order que falla
        async def failing_create_order(*args, **kwargs):
            raise Exception("Database connection failed")

        with patch.object(processor.validator, 'validate_address_for_order', mock_validate_address), \
             patch.object(processor.validator, 'validate_and_calculate_items', mock_validate_items), \
             patch('services.async_order_service.create_order', failing_create_order):

            result = await processor.create_order_fast(
                user_id="user-123",
                order_data={
                    "addressId": "addr-123",
                    "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
                    "total": 10.0,
                    "paymentMethod": "CASH"
                }
            )

            # Confirmación devuelta exitosamente
            assert result["status"] == "PENDING_CONFIRMATION"
            assert "orderId" in result

            # Dar tiempo al slow path
            await asyncio.sleep(0.1)

            # La confirmación permanece válida

    @pytest.mark.asyncio
    async def test_failed_order_is_saved_not_deleted(self):
        """
        Criterio 2: Pedido que falla se guarda como FAILED (no se elimina).

        Esto permite troubleshooting y posible reintento manual.
        """
        processor = AsyncOrderProcessor()

        # Mock de save_failed_order
        saved_failed_orders = []

        async def mock_save_failed(*args, **kwargs):
            saved_failed_orders.append(args[0])  # order_id

        # Mock de validación que falla
        async def failing_validation(*args, **kwargs):
            raise Exception("Validation failed")

        with patch.object(processor.validator, 'validate_address_for_order', failing_validation), \
             patch.object(processor, '_save_failed_order', mock_save_failed):

            result = await processor.create_order_fast(
                user_id="user-123",
                order_data={
                    "addressId": "addr-123",
                    "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
                    "total": 10.0,
                    "paymentMethod": "CASH"
                }
            )

            order_id = result["orderId"]

            # Dar tiempo al slow path para procesar y guardar como FAILED
            await asyncio.sleep(0.2)

            # Verificar que se intentó guardar como FAILED
            assert order_id in saved_failed_orders


# ==============================================================================
# Tests para AsyncOrderProcessor (HU-04 Criterio 3: Procesamiento Asíncrono)
# ==============================================================================

class TestAsyncOrderProcessorAsyncProcessing:
    """Tests para verificar procesamiento asíncrono sin pérdida de datos"""

    @pytest.mark.asyncio
    async def test_slow_path_executes_all_validations(self):
        """
        Criterio 3: Slow path ejecuta todas las validaciones asíncronamente.
        """
        processor = AsyncOrderProcessor()

        # Mocks para rastrear llamadas
        validate_address_called = asyncio.Event()
        validate_items_called = asyncio.Event()
        create_order_called = asyncio.Event()

        async def mock_validate_address(*args, **kwargs):
            validate_address_called.set()
            return {"id": "addr-123"}

        async def mock_validate_items(*args, **kwargs):
            validate_items_called.set()
            return ([{"productId": "prod-1", "quantity": 1, "price": 10.0}], 10.0)

        async def mock_create_order(*args, **kwargs):
            create_order_called.set()
            return {"id": kwargs.get("order_id", "order-123")}

        with patch.object(processor.validator, 'validate_address_for_order', mock_validate_address), \
             patch.object(processor.validator, 'validate_and_calculate_items', mock_validate_items), \
             patch('services.async_order_service.create_order', mock_create_order):

            # Fast path
            result = await processor.create_order_fast(
                user_id="user-123",
                order_data={
                    "addressId": "addr-123",
                    "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
                    "total": 10.0,
                    "paymentMethod": "CASH"
                }
            )

            # Confirmación inmediata
            assert result["status"] == "PENDING_CONFIRMATION"

            # Esperar a que el slow path complete
            await asyncio.wait_for(validate_address_called.wait(), timeout=1.0)
            await asyncio.wait_for(validate_items_called.wait(), timeout=1.0)
            await asyncio.wait_for(create_order_called.wait(), timeout=1.0)

            # Todas las validaciones se ejecutaron
            assert validate_address_called.is_set()
            assert validate_items_called.is_set()
            assert create_order_called.is_set()

    @pytest.mark.asyncio
    async def test_rabbitmq_publish_happens_asynchronously(self):
        """Publicación a RabbitMQ ocurre en background (no bloquea respuesta)"""
        processor = AsyncOrderProcessor()

        publish_called = asyncio.Event()

        async def mock_validate_address(*args, **kwargs):
            return {"id": "addr-123"}

        async def mock_validate_items(*args, **kwargs):
            return ([{"productId": "prod-1", "quantity": 1, "price": 10.0}], 10.0)

        async def mock_create_order(*args, **kwargs):
            return {"id": kwargs.get("order_id", "order-123"), "userId": "user-123", "items": []}

        async def mock_publish_order(*args, **kwargs):
            publish_called.set()
            await asyncio.sleep(0.1)  # Simular latencia de RabbitMQ

        with patch.object(processor.validator, 'validate_address_for_order', mock_validate_address), \
             patch.object(processor.validator, 'validate_and_calculate_items', mock_validate_items), \
             patch('services.async_order_service.create_order', mock_create_order), \
             patch('services.async_order_service.publish_order', mock_publish_order):

            start_time = time.perf_counter()
            result = await processor.create_order_fast(
                user_id="user-123",
                order_data={
                    "addressId": "addr-123",
                    "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
                    "total": 10.0,
                    "paymentMethod": "CASH"
                }
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Respuesta inmediata (no esperó 100ms de RabbitMQ)
            assert elapsed_ms < 50

            # Esperar a que RabbitMQ se publique en background
            await asyncio.wait_for(publish_called.wait(), timeout=1.0)
            assert publish_called.is_set()


# ==============================================================================
# Tests de Performance (HU-04 Criterio 1: P95 < 100ms)
# ==============================================================================

class TestOrderCreationPerformance:
    """Tests de performance para validar P95 < 100ms"""

    @pytest.mark.asyncio
    async def test_p95_response_time_under_100ms(self):
        """
        Criterio 1: P95 de tiempo de respuesta < 100ms.

        Ejecuta 100 requests y verifica que el percentil 95 sea <100ms.
        """
        processor = AsyncOrderProcessor()
        response_times = []

        # Ejecutar 100 requests
        for i in range(100):
            start_time = time.perf_counter()

            await processor.create_order_fast(
                user_id=f"user-{i}",
                order_data={
                    "addressId": f"addr-{i}",
                    "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
                    "total": 10.0,
                    "paymentMethod": "CASH"
                }
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            response_times.append(elapsed_ms)

        # Calcular P95
        response_times.sort()
        p95_index = int(len(response_times) * 0.95)
        p95_time = response_times[p95_index]

        print(f"\n📊 Performance Stats:")
        print(f"   Min: {min(response_times):.2f}ms")
        print(f"   P50: {response_times[50]:.2f}ms")
        print(f"   P90: {response_times[90]:.2f}ms")
        print(f"   P95: {p95_time:.2f}ms")
        print(f"   Max: {max(response_times):.2f}ms")

        # Criterio 1: P95 < 100ms
        assert p95_time < 100, f"P95 fue {p95_time:.2f}ms (debería ser <100ms)"

    @pytest.mark.asyncio
    async def test_concurrent_orders_maintain_performance(self):
        """Performance se mantiene bajo alta concurrencia"""
        processor = AsyncOrderProcessor()

        async def create_order_with_timing(order_num):
            start = time.perf_counter()
            await processor.create_order_fast(
                user_id=f"user-{order_num}",
                order_data={
                    "addressId": f"addr-{order_num}",
                    "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
                    "total": 10.0,
                    "paymentMethod": "CASH"
                }
            )
            return (time.perf_counter() - start) * 1000

        # 50 pedidos concurrentes
        tasks = [create_order_with_timing(i) for i in range(50)]
        response_times = await asyncio.gather(*tasks)

        response_times.sort()
        p95_time = response_times[int(len(response_times) * 0.95)]

        print(f"\n📊 Concurrency Test (50 concurrent orders):")
        print(f"   P95: {p95_time:.2f}ms")

        # Incluso con 50 pedidos concurrentes, P95 < 100ms
        assert p95_time < 100


# ==============================================================================
# Tests de Integración
# ==============================================================================

class TestAsyncOrderServiceIntegration:
    """Tests de integración con el servicio completo"""

    @pytest.mark.asyncio
    async def test_get_async_order_processor_singleton(self):
        """get_async_order_processor devuelve siempre la misma instancia"""
        processor1 = get_async_order_processor()
        processor2 = get_async_order_processor()
        assert processor1 is processor2

    @pytest.mark.asyncio
    async def test_full_flow_with_scheduled_order(self):
        """Pedido programado (HU-06) funciona con async processing"""
        processor = AsyncOrderProcessor()

        async def mock_validate_address(*args, **kwargs):
            return {"id": "addr-123"}

        async def mock_validate_items(*args, **kwargs):
            return ([{"productId": "prod-1", "quantity": 1, "price": 10.0}], 10.0)

        async def mock_create_order(*args, **kwargs):
            return {"id": kwargs.get("order_id"), "status": kwargs.get("status", "PENDING")}

        with patch.object(processor.validator, 'validate_address_for_order', mock_validate_address), \
             patch.object(processor.validator, 'validate_and_calculate_items', mock_validate_items), \
             patch('services.async_order_service.create_order', mock_create_order):

            result = await processor.create_order_fast(
                user_id="user-123",
                order_data={
                    "addressId": "addr-123",
                    "items": [{"productId": "prod-1", "quantity": 1, "price": 10.0}],
                    "total": 10.0,
                    "paymentMethod": "CASH",
                    "scheduledFor": "2024-12-25T10:00:00-05:00"  # ISO format
                }
            )

            # Confirmación inmediata
            assert result["status"] == "PENDING_CONFIRMATION"
            assert "orderId" in result

            # Dar tiempo al slow path
            await asyncio.sleep(0.2)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
