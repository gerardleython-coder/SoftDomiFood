"""
Tests para HU-02: Finalizar un pedido usando una dirección existente

Valida que el sistema cumpla con los criterios de aceptación:
1. Muestra lista de direcciones guardadas
2. Al seleccionar dirección, datos se registran correctamente
3. Sin dirección válida, impide paso y muestra mensaje claro

Autor: Senior Fullstack Developer
Fecha: 16 de Diciembre 2025
"""

import pytest
from services.order_validation_service import (
    OrderValidationService,
    OrderValidationError
)
from services.database_service import (
    create_address,
    get_user_addresses,
    create_user
)
from services.auth_service import get_password_hash
from unittest.mock import AsyncMock, patch


class TestHU02OrderWithAddress:
    """
    Test Suite para HU-02: Finalizar pedido con dirección existente.

    Criterios de Aceptación:
    1. Lista de direcciones guardadas visible
    2. Selección de dirección registra datos correctamente
    3. Sin dirección válida = error claro
    """

    @pytest.fixture
    def validator(self):
        """Instancia del servicio de validación"""
        return OrderValidationService()

    @pytest.fixture
    async def test_user_with_address(self):
        """Crear usuario de prueba con una dirección"""
        import asyncio
        email = f"address_test_{asyncio.get_event_loop().time()}@test.com"
        password = get_password_hash("TestPass123!")

        try:
            user = await create_user(
                email=email,
                hashed_password=password,
                name="Address Test User",
                phone="1234567890"
            )

            # Crear dirección para el usuario
            address = await create_address(
                user_id=user["id"],
                street="Calle 123",
                city="Bogotá",
                state="Cundinamarca",
                zip_code="110111",
                country="Colombia",
                is_default=True,
                instructions="Casa blanca"
            )

            return {
                "user_id": user["id"],
                "email": email,
                "address_id": address["id"],
                "address": address
            }
        except Exception as e:
            pytest.skip(f"No se pudo crear usuario de prueba: {e}")

    # ============================================================
    # CRITERIO 1: Lista de direcciones guardadas
    # ============================================================

    @pytest.mark.asyncio
    async def test_user_can_list_saved_addresses(self, test_user_with_address):
        """
        Test: Usuario puede ver lista de sus direcciones guardadas.
        HU-02 Criterio 1: "El sistema muestra una lista clara de al menos una dirección"
        """
        user_id = test_user_with_address["user_id"]

        # Obtener direcciones del usuario
        addresses = await get_user_addresses(user_id)

        # Validar que tiene al menos una dirección
        assert len(addresses) >= 1, "Usuario debe tener al menos una dirección"

        # Validar que la dirección tiene campos requeridos
        first_address = addresses[0]
        required_fields = ["id", "userId", "street", "city", "state", "zipCode"]
        for field in required_fields:
            assert field in first_address, f"Dirección debe tener campo '{field}'"
            assert first_address[field], f"Campo '{field}' no debe estar vacío"

    @pytest.mark.asyncio
    async def test_addresses_ordered_by_default_first(self, test_user_with_address):
        """
        Test: Direcciones se muestran con la predeterminada primero.
        Mejora UX para selección rápida.
        """
        user_id = test_user_with_address["user_id"]

        # Crear segunda dirección NO predeterminada
        await create_address(
            user_id=user_id,
            street="Carrera 45",
            city="Medellín",
            state="Antioquia",
            zip_code="050001",
            country="Colombia",
            is_default=False,
            instructions="Apartamento"
        )

        addresses = await get_user_addresses(user_id)

        # La primera dirección debe ser la predeterminada
        assert len(addresses) >= 2
        assert addresses[0]["isDefault"] == True, "Primera dirección debe ser la predeterminada"

    # ============================================================
    # CRITERIO 2: Selección de dirección registra correctamente
    # ============================================================

    @pytest.mark.asyncio
    async def test_validate_existing_address_success(self, validator, test_user_with_address):
        """
        Test: Dirección existente y válida pasa validación.
        HU-02 Criterio 2: "Al seleccionar, datos se actualizan y registran correctamente"
        """
        address_id = test_user_with_address["address_id"]
        user_id = test_user_with_address["user_id"]

        # Validar dirección
        validated_address = await validator.validate_address_for_order(address_id, user_id)

        # Verificar que retorna la dirección completa
        assert validated_address is not None
        assert validated_address["id"] == address_id
        assert validated_address["userId"] == user_id
        assert "street" in validated_address
        assert "city" in validated_address

    @pytest.mark.asyncio
    async def test_validate_address_belongs_to_user(self, validator, test_user_with_address):
        """
        Test: Solo puede usar direcciones que le pertenecen.
        Seguridad: previene uso de direcciones de otros usuarios.
        """
        address_id = test_user_with_address["address_id"]
        wrong_user_id = "wrong-user-id-12345"

        # Intentar validar con usuario diferente
        with pytest.raises(OrderValidationError) as exc_info:
            await validator.validate_address_for_order(address_id, wrong_user_id)

        assert exc_info.value.status_code == 403
        assert "no pertenece" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_validate_address_has_required_fields(self, validator):
        """
        Test: Dirección debe tener campos mínimos requeridos.
        HU-02 Criterio 2: Datos completos para entrega.
        """
        # Mock dirección incompleta
        with patch('services.order_validation_service.get_address_by_id') as mock_get:
            mock_get.return_value = {
                "id": "addr-123",
                "userId": "user-123",
                "street": "Calle 1",
                # Faltan city, state, zipCode
            }

            with pytest.raises(OrderValidationError) as exc_info:
                await validator.validate_address_for_order("addr-123", "user-123")

            assert exc_info.value.status_code == 422
            assert "incompleta" in exc_info.value.message.lower()

    # ============================================================
    # CRITERIO 3: Sin dirección válida = mensaje claro
    # ============================================================

    @pytest.mark.asyncio
    async def test_empty_address_id_shows_clear_message(self, validator):
        """
        Test: Dirección vacía muestra mensaje claro.
        HU-02 Criterio 3: "impide el paso y muestra un mensaje de advertencia claro"
        """
        with pytest.raises(OrderValidationError) as exc_info:
            await validator.validate_address_for_order("", "user-123")

        assert exc_info.value.status_code == 422
        assert "seleccionar una dirección" in exc_info.value.message.lower()
        assert "lista" in exc_info.value.message.lower() or "agregar" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_address_shows_clear_message(self, validator):
        """
        Test: Dirección inexistente muestra mensaje claro.
        HU-02 Criterio 3: Usuario entiende el problema y cómo resolverlo.
        """
        fake_address_id = "nonexistent-address-id-999"

        with pytest.raises(OrderValidationError) as exc_info:
            await validator.validate_address_for_order(fake_address_id, "user-123")

        assert exc_info.value.status_code == 404
        assert "no existe" in exc_info.value.message.lower()
        assert "seleccione" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_null_address_id_shows_clear_message(self, validator):
        """
        Test: None como address_id muestra mensaje claro.
        Edge case importante para UX.
        """
        with pytest.raises(OrderValidationError) as exc_info:
            await validator.validate_address_for_order(None, "user-123")

        assert exc_info.value.status_code == 422
        assert "seleccionar" in exc_info.value.message.lower()

    # ============================================================
    # TESTS ADICIONALES: Robustez y Edge Cases
    # ============================================================

    @pytest.mark.asyncio
    async def test_address_with_whitespace_is_trimmed(self, validator, test_user_with_address):
        """
        Test: Address ID con espacios se maneja correctamente.
        Clean Code: normalizar inputs.
        """
        address_id = test_user_with_address["address_id"]
        user_id = test_user_with_address["user_id"]

        # Agregar espacios al address_id
        address_id_with_spaces = f"  {address_id}  "

        # Debe funcionar después de trim
        validated_address = await validator.validate_address_for_order(
            address_id_with_spaces,
            user_id
        )

        assert validated_address is not None
        assert validated_address["id"] == address_id

    @pytest.mark.asyncio
    async def test_error_messages_are_user_friendly(self, validator):
        """
        Test: Mensajes de error son amigables para usuario final.
        HU-02 Criterio 3: Claridad en comunicación de errores.
        """
        test_cases = [
            ("", "address_id vacío"),
            (None, "address_id null"),
            ("fake-id", "address_id inexistente")
        ]

        for address_id, description in test_cases:
            try:
                await validator.validate_address_for_order(address_id, "user-123")
                pytest.fail(f"Debería lanzar error para: {description}")
            except OrderValidationError as e:
                # Verificar que el mensaje NO contiene jerga técnica
                message_lower = e.message.lower()
                assert "exception" not in message_lower
                assert "null" not in message_lower
                assert "none" not in message_lower

                # Verificar que el mensaje SÍ contiene orientación
                has_guidance = any(word in message_lower for word in [
                    "seleccione", "elija", "agregue", "intente", "por favor"
                ])
                assert has_guidance, f"Mensaje debe dar orientación al usuario: {e.message}"


class TestOrderValidationServiceIntegration:
    """Tests de integración para validación completa de pedidos"""

    @pytest.fixture
    def validator(self):
        return OrderValidationService()

    @pytest.mark.asyncio
    async def test_complete_order_validation_flow(self, validator):
        """
        Test: Flujo completo de validación de pedido.
        Simula HU-02 + HU-04 juntos.
        """
        # Mock de datos de prueba
        with patch('services.order_validation_service.get_address_by_id') as mock_addr, \
             patch('services.order_validation_service.get_product_by_id') as mock_prod:

            # Setup mocks
            mock_addr.return_value = {
                "id": "addr-123",
                "userId": "user-123",
                "street": "Calle Principal",
                "city": "Bogotá",
                "state": "Cundinamarca",
                "zipCode": "110111"
            }

            mock_prod.return_value = {
                "id": "prod-123",
                "name": "Producto Test",
                "price": 10.0,
                "isAvailable": True
            }

            # 1. Validar dirección
            address = await validator.validate_address_for_order("addr-123", "user-123")
            assert address is not None

            # 2. Validar items
            items = [{"productId": "prod-123", "quantity": 2}]
            validated_items, total = await validator.validate_and_calculate_items(items)
            assert len(validated_items) == 1
            assert total == 20.0

            # 3. Validar total
            final_total = validator.validate_order_total(None, total)
            assert final_total == 20.0

            # ✅ Todos los pasos pasaron - pedido válido


# ============================================================
# CONFIGURACIÓN PYTEST
# ============================================================

@pytest.fixture(scope="session")
def anyio_backend():
    """Configuración para pytest-asyncio"""
    return "asyncio"
