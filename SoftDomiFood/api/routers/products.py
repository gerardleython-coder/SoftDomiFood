from fastapi import APIRouter, Query
from typing import Optional
from services.database_service import get_products, get_product_by_id

router = APIRouter()

@router.get("/")
async def get_products_list(
    category: Optional[str] = Query(None),
    available: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Obtener lista de productos"""
    products = await get_products(category=category, available=available, skip=skip, limit=limit)
    return {"products": products}

@router.get("/{product_id}")
async def get_product(product_id: str):
    """Obtener producto por ID"""
    product = await get_product_by_id(product_id)
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": product}
