"""
Order Validation Service - Business Logic for Order Creation

Servicio que encapsula la lógica de validación de pedidos (HU-02, HU-04).
Aplica principios SOLID para separar responsabilidades y mejorar testabilidad.

Principios SOLID aplicados:
- SRP: Cada método tiene una responsabilidad única de validación
- OCP: Extensible para agregar nuevas validaciones sin modificar existentes
- DIP: Depende de abstracciones (funciones de database_service)

Autor: Senior Fullstack Developer
Fecha: 16 de Diciembre 2025
"""

from typing import List, Dict, Any, Optional, Tuple
from fastapi import HTTPException
from services.database_service import (
    get_address_by_id,
    get_product_by_id,
    validate_coupon_for_user,
    get_coupon_by_code
)


class OrderValidationError(Exception):
    """Excepción personalizada para errores de validación de pedidos"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class OrderValidationService:
    """
    Servicio para validar todos los aspectos de un pedido antes de su creación.

    Responsibilities:
    - Validar dirección de entrega (HU-02)
    - Validar items del pedido
    - Validar cupones de descuento
    - Calcular totales con descuentos
    """

    @staticmethod
    async def validate_address_for_order(
        address_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Validar que la dirección existe y pertenece al usuario (HU-02 Criterio 2).

        Args:
            address_id: ID de la dirección seleccionada
            user_id: ID del usuario que crea el pedido

        Returns:
            Dict con datos de la dirección validada

        Raises:
            OrderValidationError: Si la dirección no existe o no pertenece al usuario
        """
        if not address_id or not address_id.strip():
            raise OrderValidationError(
                "Debe seleccionar una dirección de entrega válida. "
                "Por favor, elija una dirección de la lista o agregue una nueva.",
                status_code=422
            )

        address = await get_address_by_id(address_id.strip())

        if not address:
            raise OrderValidationError(
                "La dirección seleccionada no existe. "
                "Por favor, seleccione una dirección válida de su lista de direcciones.",
                status_code=404
            )

        if str(address.get("userId")) != str(user_id):
            raise OrderValidationError(
                "La dirección seleccionada no pertenece a su cuenta. "
                "Por favor, seleccione una de sus direcciones guardadas.",
                status_code=403
            )

        # Validar que la dirección tenga los campos mínimos requeridos
        required_fields = ["street", "city", "state", "zipCode"]
        missing_fields = [field for field in required_fields if not address.get(field)]

        if missing_fields:
            raise OrderValidationError(
                f"La dirección seleccionada está incompleta (faltan: {', '.join(missing_fields)}). "
                "Por favor, seleccione otra dirección o complete la información.",
                status_code=422
            )

        return address

    @staticmethod
    async def validate_and_calculate_items(
        items: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Validar items del pedido y calcular total.

        Args:
            items: Lista de items con productId, quantity, price opcional

        Returns:
            Tuple (validated_items, calculated_total)

        Raises:
            OrderValidationError: Si algún item es inválido
        """
        if not items or len(items) == 0:
            raise OrderValidationError(
                "El pedido debe contener al menos un producto. "
                "Por favor, agregue productos antes de continuar.",
                status_code=422
            )

        validated_items = []
        calculated_total = 0.0

        for index, item in enumerate(items, start=1):
            # Validar cantidad
            quantity = item.get("quantity", 0)
            if not isinstance(quantity, int) or quantity <= 0:
                raise OrderValidationError(
                    f"La cantidad del producto #{index} debe ser un número entero mayor a 0. "
                    "Por favor, ajuste la cantidad e intente nuevamente.",
                    status_code=422
                )

            # Validar producto existe
            product_id = item.get("productId")
            if not product_id:
                raise OrderValidationError(
                    f"El producto #{index} no tiene un ID válido.",
                    status_code=422
                )

            product = await get_product_by_id(product_id)
            if not product:
                raise OrderValidationError(
                    f"El producto #{index} (ID: {product_id}) no fue encontrado. "
                    "Es posible que haya sido eliminado del catálogo.",
                    status_code=404
                )

            # Validar disponibilidad
            if not product.get("isAvailable", True):
                product_name = product.get("name", "Desconocido")
                raise OrderValidationError(
                    f"El producto '{product_name}' no está disponible en este momento. "
                    "Por favor, elimínelo del carrito para continuar.",
                    status_code=400
                )

            # Calcular precio
            item_price = item.get("price")
            if item_price is None:
                item_price = float(product.get("price", 0))
            else:
                item_price = float(item_price)

            if item_price < 0:
                raise OrderValidationError(
                    f"El precio del producto #{index} no puede ser negativo.",
                    status_code=422
                )

            item_total = item_price * quantity
            calculated_total += item_total

            validated_items.append({
                "productId": product_id,
                "quantity": quantity,
                "price": item_price
            })

        if calculated_total <= 0:
            raise OrderValidationError(
                "El total del pedido debe ser mayor a 0.",
                status_code=422
            )

        return validated_items, calculated_total

    @staticmethod
    async def validate_and_apply_coupon(
        coupon_code: Optional[str],
        user_id: str,
        order_total: float
    ) -> Tuple[float, float]:
        """
        Validar cupón y calcular descuento aplicable.

        Args:
            coupon_code: Código del cupón (opcional)
            user_id: ID del usuario
            order_total: Total del pedido antes de descuento

        Returns:
            Tuple (discount_applied, final_total)

        Raises:
            OrderValidationError: Si el cupón es inválido
        """
        if not coupon_code or not coupon_code.strip():
            return 0.0, order_total

        validation = await validate_coupon_for_user(coupon_code.strip(), user_id)

        if not validation.get("valid"):
            reason = validation.get("reason", "Cupón inválido")
            raise OrderValidationError(
                f"No se pudo aplicar el cupón '{coupon_code}': {reason}. "
                "Puede continuar sin cupón o ingresar uno válido.",
                status_code=400
            )

        coupon = validation.get("coupon", {})
        discount_applied = 0.0

        discount_type = coupon.get("discount_type")
        if discount_type == "PERCENTAGE":
            percentage = float(coupon.get("percentage", 0))
            if percentage < 0 or percentage > 100:
                raise OrderValidationError(
                    "El cupón tiene un porcentaje de descuento inválido.",
                    status_code=500
                )
            discount_applied = round(order_total * (percentage / 100.0), 2)
        elif discount_type == "AMOUNT":
            amount = float(coupon.get("amount", 0))
            if amount < 0:
                raise OrderValidationError(
                    "El cupón tiene un monto de descuento inválido.",
                    status_code=500
                )
            discount_applied = amount
        else:
            raise OrderValidationError(
                "El cupón tiene un tipo de descuento no soportado.",
                status_code=500
            )

        # El descuento no puede exceder el total ni ser negativo
        discount_applied = max(0.0, min(discount_applied, order_total))
        final_total = round(order_total - discount_applied, 2)

        # El total final debe ser al menos 0
        final_total = max(0.0, final_total)

        return discount_applied, final_total

    @staticmethod
    def validate_order_total(
        provided_total: Optional[float],
        calculated_total: float
    ) -> float:
        """
        Validar y determinar el total final del pedido.

        Args:
            provided_total: Total proporcionado por el cliente (opcional)
            calculated_total: Total calculado por el servidor

        Returns:
            Total validado a usar

        Raises:
            OrderValidationError: Si hay inconsistencia crítica
        """
        if provided_total is None:
            return calculated_total

        provided_total = float(provided_total)

        # Permitir pequeña diferencia por redondeo (0.01)
        difference = abs(provided_total - calculated_total)
        if difference > 0.01:
            raise OrderValidationError(
                f"El total proporcionado (${provided_total:.2f}) no coincide con el total calculado (${calculated_total:.2f}). "
                "Por favor, actualice su carrito e intente nuevamente.",
                status_code=422
            )

        return provided_total if provided_total > 0 else calculated_total


# Factory function para obtener instancia del servicio
def get_order_validation_service() -> OrderValidationService:
    """
    Obtener instancia del servicio de validación de pedidos.

    Returns:
        Instancia de OrderValidationService

    Example:
        validator = get_order_validation_service()
        address = await validator.validate_address_for_order(address_id, user_id)
    """
    return OrderValidationService()
