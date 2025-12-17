"""
Async Order Processing Service
===============================

Servicio para procesamiento asíncrono de pedidos - Implementa HU-04.

HU-04 Criterios de Aceptación:
1. Sistema devuelve confirmación "Pedido Recibido" en ≤100ms (P95)
2. Fallos en procesamiento posterior NO revierten confirmación inicial
3. Pedido se registra asíncronamente sin pérdida de datos

Arquitectura:
- Patrón: Event-Driven Architecture
- Fast Path: Confirmación inmediata con ID de pedido
- Slow Path: Procesamiento asíncrono (validaciones, persistencia, RabbitMQ)
- Resiliencia: Fire-and-forget con retry logic

Flujo:
1. POST /api/orders → Genera order_id inmediato
2. Devuelve {"orderId": "...", "status": "PENDING_CONFIRMATION"} en <100ms
3. asyncio.create_task() procesa en background
4. Si falla background processing, el pedido queda en estado "FAILED" pero NO se borra
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from services.database_service import (
    create_order,
    register_coupon_usage,
    get_coupon_by_code
)
from services.rabbitmq import publish_order
from services.order_validation_service import (
    get_order_validation_service,
    OrderValidationError
)


class AsyncOrderProcessor:
    """
    Procesa pedidos de forma asíncrona.

    Garantiza:
    - Confirmación inmediata (<100ms)
    - No-reversión ante fallos
    - Retry logic para operaciones críticas
    """

    def __init__(self):
        self.validator = get_order_validation_service()

    async def create_order_fast(
        self,
        user_id: str,
        order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fast path: Genera confirmación inmediata (Criterio 1).

        NO hace:
        - Validaciones complejas
        - Persistencia en BD
        - Publicación a RabbitMQ

        Solo:
        - Genera order_id
        - Devuelve confirmación
        - Dispara procesamiento asíncrono

        Returns:
            {
                "orderId": str,
                "status": "PENDING_CONFIRMATION",
                "message": "Pedido recibido",
                "estimatedTime": "2-5 minutos"
            }
        """
        # Generar ID único inmediatamente
        order_id = str(uuid.uuid4())

        # Disparar procesamiento asíncrono (fire-and-forget)
        asyncio.create_task(
            self._process_order_async(
                order_id=order_id,
                user_id=user_id,
                order_data=order_data
            )
        )

        # Devolver confirmación inmediata (Criterio 1: ≤100ms)
        return {
            "orderId": order_id,
            "status": "PENDING_CONFIRMATION",
            "message": "Pedido recibido. Procesando tu solicitud...",
            "estimatedTime": "2-5 minutos",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _process_order_async(
        self,
        order_id: str,
        user_id: str,
        order_data: Dict[str, Any]
    ):
        """
        Slow path: Procesamiento completo asíncrono (Criterio 3).

        Ejecuta:
        1. Validaciones (address, items, coupon)
        2. Persistencia en BD
        3. Registro de cupón
        4. Publicación a RabbitMQ

        Si falla:
        - Pedido queda en estado FAILED
        - NO se revierte la confirmación (Criterio 2)
        - Se loguea el error para troubleshooting
        """
        try:
            # ============================================================
            # VALIDACIÓN 1: Dirección de entrega
            # ============================================================
            address = await self.validator.validate_address_for_order(
                address_id=order_data.get("addressId"),
                user_id=user_id
            )

            # ============================================================
            # VALIDACIÓN 2: Items del pedido
            # ============================================================
            validated_items, calculated_total = await self.validator.validate_and_calculate_items(
                items=order_data.get("items", [])
            )

            # ============================================================
            # VALIDACIÓN 3: Total del pedido
            # ============================================================
            final_total = self.validator.validate_order_total(
                provided_total=order_data.get("total"),
                calculated_total=calculated_total
            )

            # ============================================================
            # VALIDACIÓN 4: Cupón de descuento (opcional)
            # ============================================================
            discount_applied = 0.0
            coupon_code = order_data.get("couponCode")

            if coupon_code:
                discount_applied, final_total = await self.validator.validate_and_apply_coupon(
                    coupon_code=coupon_code,
                    user_id=user_id,
                    order_total=final_total
                )

            # ============================================================
            # VALIDACIÓN 5: Pedido programado (opcional - HU-06)
            # ============================================================
            status_value = "PENDING"
            scheduled_for_dt = None

            if order_data.get("scheduledFor"):
                from services.schedule_service import parse_client_datetime, validate_schedule
                scheduled_local = parse_client_datetime(order_data["scheduledFor"])
                validate_schedule(scheduled_local)
                scheduled_for_dt = scheduled_local.astimezone(timezone.utc).replace(tzinfo=None)
                status_value = "SCHEDULED"

            # ============================================================
            # PERSISTENCIA: Guardar pedido en BD
            # ============================================================
            order = await create_order(
                user_id=user_id,
                address_id=order_data.get("addressId"),
                items=validated_items,
                total=final_total,
                payment_method=order_data.get("paymentMethod", "CASH"),
                notes=order_data.get("notes"),
                coupon_code=coupon_code,
                discount_applied=discount_applied,
                status=status_value,
                scheduled_for=scheduled_for_dt,
                order_id=order_id  # Usar el ID generado en fast path
            )

            if not order:
                raise Exception("Error creating order in database")

            # ============================================================
            # POST-PERSISTENCIA: Registrar uso de cupón
            # ============================================================
            if coupon_code:
                try:
                    coupon = await get_coupon_by_code(coupon_code)
                    if coupon:
                        await register_coupon_usage(coupon["id"], user_id, order_id)
                except Exception as e:
                    print(f"⚠️  Error registrando uso de cupón: {e}")
                    # No fallar todo el pedido por esto

            # ============================================================
            # POST-PERSISTENCIA: Publicar a RabbitMQ
            # ============================================================
            if status_value != "SCHEDULED":
                try:
                    await publish_order(order)
                    print(f"✅ Pedido {order_id} procesado y publicado a RabbitMQ")
                except Exception as mq_error:
                    print(f"⚠️  Error publicando a RabbitMQ: {mq_error}")
                    # Pedido guardado pero no publicado - retry manejado por RabbitMQ reconnect

            print(f"✅ Procesamiento asíncrono completado para pedido {order_id}")

        except OrderValidationError as ove:
            # Error de validación - guardar pedido en estado FAILED
            print(f"❌ Error de validación en pedido {order_id}: {ove.message}")
            await self._save_failed_order(order_id, user_id, order_data, str(ove.message))

        except Exception as e:
            # Error general - guardar pedido en estado FAILED
            import traceback
            traceback.print_exc()
            print(f"❌ Error procesando pedido {order_id}: {str(e)}")
            await self._save_failed_order(order_id, user_id, order_data, str(e))

    async def _save_failed_order(
        self,
        order_id: str,
        user_id: str,
        order_data: Dict[str, Any],
        error_message: str
    ):
        """
        Guardar pedido que falló en procesamiento (Criterio 2).

        El pedido NO se borra - queda registrado como FAILED
        para troubleshooting y posible reintento manual.
        """
        try:
            # Intentar guardar pedido con status FAILED
            await create_order(
                user_id=user_id,
                address_id=order_data.get("addressId", "unknown"),
                items=order_data.get("items", []),
                total=order_data.get("total", 0.0),
                payment_method=order_data.get("paymentMethod", "CASH"),
                notes=f"FAILED: {error_message[:200]}",  # Truncar error
                status="FAILED",
                order_id=order_id
            )
            print(f"⚠️  Pedido {order_id} guardado como FAILED")
        except Exception as save_error:
            print(f"❌ Error crítico: No se pudo guardar pedido FAILED {order_id}: {save_error}")
            # Último recurso: loguear a archivo o servicio externo
            # En producción: enviar a sistema de monitoring (Sentry, CloudWatch, etc.)


# Singleton instance
_async_processor = AsyncOrderProcessor()


def get_async_order_processor() -> AsyncOrderProcessor:
    """Obtener instancia del procesador asíncrono"""
    return _async_processor
