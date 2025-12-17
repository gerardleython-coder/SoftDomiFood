from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

from routers.auth import get_current_user
from services.database_service import get_order_status, get_user_orders
from services.async_order_service import get_async_order_processor  # HU-04

router = APIRouter()

class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"

class OrderItem(BaseModel):
    productId: str
    quantity: int
    price: Optional[float] = None

class CreateOrderRequest(BaseModel):
    addressId: str
    items: List[OrderItem]
    total: Optional[float] = None
    paymentMethod: PaymentMethod = PaymentMethod.CASH
    notes: Optional[str] = None
    couponCode: Optional[str] = None
    scheduledFor: Optional[str] = None

@router.post("/")
async def create_new_order(
    order_data: CreateOrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Crear nuevo pedido con confirmación instantánea (HU-04).

    HU-04 Criterios de Aceptación:
    1. Devuelve confirmación "Pedido Recibido" en ≤100ms (P95)
    2. Fallos posteriores NO revierten confirmación inicial
    3. Pedido se registra asíncronamente sin pérdida de datos

    Arquitectura:
    - Fast Path: Confirmación inmediata con order_id
    - Slow Path: Procesamiento asíncrono (validaciones, BD, RabbitMQ)
    - Resiliencia: Fire-and-forget con retry logic
    """
    try:
        # Validación de autenticación (fast - no bloquea)
        if not current_user or not current_user.get("userId"):
            raise HTTPException(status_code=401, detail="Usuario no autenticado")

        # HU-04: Obtener procesador asíncrono
        async_processor = get_async_order_processor()

        # HU-04 Criterio 1: Confirmación instantánea (≤100ms)
        confirmation = await async_processor.create_order_fast(
            user_id=current_user["userId"],
            order_data={
                "addressId": order_data.addressId,
                "items": [item.dict() for item in order_data.items],
                "total": order_data.total,
                "paymentMethod": order_data.paymentMethod.value,
                "notes": order_data.notes,
                "couponCode": order_data.couponCode,
                "scheduledFor": order_data.scheduledFor
            }
        )

        # HU-04 Criterio 1: Respuesta inmediata (<100ms)
        # El procesamiento real ocurre en background (asyncio.create_task)
        return confirmation

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

@router.get("/{order_id}")
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener estado de un pedido"""
    order = await get_order_status(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order": order}

@router.get("/")
async def get_orders(
    current_user: dict = Depends(get_current_user)
):
    """Obtener todos los pedidos del usuario autenticado"""
    if not current_user or not current_user.get("userId"):
        raise HTTPException(status_code=401, detail="Usuario no autenticado")

    orders = await get_user_orders(current_user["userId"])
    return {"orders": orders}
