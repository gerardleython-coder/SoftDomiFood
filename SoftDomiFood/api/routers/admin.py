from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from services.database_service import (
    get_all_orders, update_order_status, create_product, update_product,
    get_all_customers_with_addresses, list_coupons, create_coupon, update_coupon, delete_coupon
)
from routers.auth import get_current_user

router = APIRouter()

class UpdateStatusRequest(BaseModel):
    status: str

class CreateProductRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image: Optional[str] = None
    isAvailable: bool = True

class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image: Optional[str] = None
    isAvailable: Optional[bool] = None

class CreateCouponRequest(BaseModel):
    code: str
    description: Optional[str] = None
    discountType: str
    amount: Optional[float] = None
    percentage: Optional[float] = None
    validFrom: Optional[str] = None
    validTo: Optional[str] = None
    maxUses: Optional[int] = None
    perUserLimit: Optional[int] = None
    applicableUserId: Optional[str] = None
    isActive: bool = True

class UpdateCouponRequest(BaseModel):
    description: Optional[str] = None
    discountType: Optional[str] = None
    amount: Optional[float] = None
    percentage: Optional[float] = None
    validFrom: Optional[str] = None
    validTo: Optional[str] = None
    maxUses: Optional[int] = None
    perUserLimit: Optional[int] = None
    applicableUserId: Optional[str] = None
    isActive: Optional[bool] = None

@router.get("/orders")
async def get_all_orders_admin(current_user: dict = Depends(get_current_user)):
    """Obtener todos los pedidos (solo admin)"""
    # El payload del token tiene 'role' directamente
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    orders = await get_all_orders()
    return {"orders": orders}

@router.patch("/orders/{order_id}/status")
async def update_order_status_admin(
    order_id: str,
    request: UpdateStatusRequest,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar estado de pedido (solo admin)"""
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    valid_statuses = ["PENDING", "CONFIRMED", "PREPARING", "READY", "ON_DELIVERY", "DELIVERED", "CANCELLED"]
    if request.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    order = await update_order_status(order_id, request.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "message": "Order status updated successfully",
        "order": order
    }

@router.post("/products")
async def create_new_product(
    request: CreateProductRequest,
    current_user: dict = Depends(get_current_user)
):
    """Crear nuevo producto (solo admin)"""
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Validar categoría
    valid_categories = ["SALCHIPAPAS", "BEBIDAS", "ADICIONALES", "COMBOS"]
    if request.category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}")

    product = await create_product(
        name=request.name,
        description=request.description,
        price=request.price,
        category=request.category,
        image=request.image,
        is_available=request.isAvailable
    )

    if not product:
        raise HTTPException(status_code=500, detail="Error creating product")

    return {
        "message": "Product created successfully",
        "product": product
    }

@router.put("/products/{product_id}")
async def update_existing_product(
    product_id: str,
    request: UpdateProductRequest,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar producto existente (solo admin)"""
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Validar categoría si se proporciona
    if request.category is not None:
        valid_categories = ["SALCHIPAPAS", "BEBIDAS", "ADICIONALES", "COMBOS"]
        if request.category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}")

    product = await update_product(
        product_id=product_id,
        name=request.name,
        description=request.description,
        price=request.price,
        category=request.category,
        image=request.image,
        is_available=request.isAvailable
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "message": "Product updated successfully",
        "product": product
    }

@router.get("/customers")
async def get_all_customers(current_user: dict = Depends(get_current_user)):
    """Obtener todos los clientes con sus direcciones (solo admin)"""
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")

    customers = await get_all_customers_with_addresses()
    return {"customers": customers}

@router.options("/coupons")
async def admin_coupons_preflight():
    """Responder preflight CORS para /coupons"""
    return Response(status_code=200)

@router.get("/coupons")
async def admin_list_coupons():
    """Listar cupones (sin autenticación temporal para pruebas)"""
    coupons = await list_coupons()
    return {"coupons": coupons}

@router.post("/coupons")
async def admin_create_coupon(request: CreateCouponRequest):
    """Crear cupón (sin autenticación temporal para pruebas)"""
    # Convertir fechas ISO (string) a datetime para Postgres
    def parse_dt(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            # admitir formatos 'YYYY-MM-DDTHH:MM' y completos con segundos
            return datetime.fromisoformat(value)
        except Exception:
            # intentar agregar ":00" si faltan segundos
            try:
                return datetime.fromisoformat(value + ":00")
            except Exception:
                raise HTTPException(status_code=400, detail="Fechas inválidas: usar formato ISO yyyy-MM-ddTHH:mm")
    dt = request.discountType
    if dt not in ("AMOUNT", "PERCENTAGE"):
        raise HTTPException(status_code=400, detail="discountType debe ser AMOUNT o PERCENTAGE")
    if dt == "AMOUNT" and (request.amount is None or request.amount <= 0):
        raise HTTPException(status_code=400, detail="amount requerido y > 0 para AMOUNT")
    if dt == "PERCENTAGE" and (request.percentage is None or request.percentage <= 0 or request.percentage > 100):
        raise HTTPException(status_code=400, detail="percentage requerido (1-100) para PERCENTAGE")
    coupon = await create_coupon(
        code=request.code.upper(), description=request.description, discount_type=dt,
        amount=request.amount if dt == "AMOUNT" else None,
        percentage=request.percentage if dt == "PERCENTAGE" else None,
        valid_from=parse_dt(request.validFrom), valid_to=parse_dt(request.validTo),
        max_uses=request.maxUses, per_user_limit=request.perUserLimit,
        applicable_user_id=request.applicableUserId, is_active=request.isActive
    )
    if not coupon:
        raise HTTPException(status_code=500, detail="Error creando cupón")
    return {"message": "Coupon created", "coupon": coupon}

@router.put("/coupons/{coupon_id}")
async def admin_update_coupon(coupon_id: str, request: UpdateCouponRequest):
    """Actualizar cupón (sin autenticación temporal para pruebas)"""
    # Convertir fechas ISO (string) a datetime para Postgres
    def parse_dt(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            try:
                return datetime.fromisoformat(value + ":00")
            except Exception:
                raise HTTPException(status_code=400, detail="Fechas inválidas: usar formato ISO yyyy-MM-ddTHH:mm")

    fields = {}
    if request.description is not None: fields["description"] = request.description
    if request.discountType is not None:
        if request.discountType not in ("AMOUNT", "PERCENTAGE"):
            raise HTTPException(status_code=400, detail="discountType inválido")
        fields["discount_type"] = request.discountType
        # Limpiar amount/percentage según tipo
        if request.discountType == "AMOUNT":
            if request.amount is not None and request.amount <= 0:
                raise HTTPException(status_code=400, detail="amount debe ser > 0")
            fields["amount"] = request.amount
            fields["percentage"] = None
        elif request.discountType == "PERCENTAGE":
            if request.percentage is not None and (request.percentage <= 0 or request.percentage > 100):
                raise HTTPException(status_code=400, detail="percentage debe estar entre 1 y 100")
            fields["percentage"] = request.percentage
            fields["amount"] = None
    if request.validFrom is not None: fields["valid_from"] = parse_dt(request.validFrom)
    if request.validTo is not None: fields["valid_to"] = parse_dt(request.validTo)
    if request.maxUses is not None: fields["max_uses"] = request.maxUses
    if request.perUserLimit is not None: fields["per_user_limit"] = request.perUserLimit
    if request.applicableUserId is not None: fields["applicable_user_id"] = request.applicableUserId
    if request.isActive is not None: fields["is_active"] = request.isActive
    if request.amount is not None and "discount_type" not in fields:
        fields["amount"] = request.amount
    if request.percentage is not None and "discount_type" not in fields:
        fields["percentage"] = request.percentage
    coupon = await update_coupon(coupon_id, **fields)
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found or no fields to update")
    return {"message": "Coupon updated", "coupon": coupon}

@router.delete("/coupons/{coupon_id}")
async def admin_delete_coupon(coupon_id: str):
    """Eliminar cupón (sin autenticación temporal para pruebas)"""
    ok = await delete_coupon(coupon_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return {"message": "Coupon deleted"}
