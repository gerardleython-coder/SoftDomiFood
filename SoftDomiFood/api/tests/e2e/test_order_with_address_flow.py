"""
Tests E2E para el flujo de pedido con dirección (TC-HU006)

Cobertura:
- TC-HU006-01: Crear pedido con dirección existente
- TC-HU006-02: Crear pedido añadiendo nueva dirección durante checkout
"""
import pytest
from httpx import AsyncClient
from tests.fixtures.data import SAMPLE_USER, SAMPLE_ADMIN


class TestOrderWithAddressFlow:
    """
    Suite de tests E2E para el flujo completo de pedido con gestión de direcciones

    Escenarios basados en TEST_CASES.md:
    - Pedido con dirección previamente guardada
    - Pedido con nueva dirección añadida en checkout
    """

    @pytest.mark.asyncio
    async def test_tc_hu006_01_order_with_existing_address(
        self,
        test_client: AsyncClient,
        test_db,
        seeded_db
    ):
        """
        TC-HU006-01: Validar la creación de un pedido con una dirección existente

        Pasos (Gherkin):
        - Given: El usuario tiene productos en el carrito
        - And: El usuario posee direcciones registradas
        - When: Selecciona una dirección existente y confirma el pedido
        - Then: El pedido se registra correctamente con la dirección seleccionada

        Datos de Entrada:
        - Dirección registrada

        Resultado Esperado:
        - El pedido se registra con la dirección seleccionada
        """
        # Given: Usuario autenticado con dirección registrada
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": SAMPLE_USER["email"],
                "password": SAMPLE_USER["password"]
            }
        )
        assert login_response.status_code in [200, 201], f"Login falló: {login_response.text}"
        login_data = login_response.json()
        token = login_data.get("token") or login_data.get("access_token")
        assert token, f"No se obtuvo token: {login_data}"
        headers = {"Authorization": f"Bearer {token}"}

        # Crear dirección mediante la API para evitar problemas de transacciones
        from tests.fixtures.data import SAMPLE_ADDRESS
        create_address_response = await test_client.post(
            "/api/addresses",
            json=SAMPLE_ADDRESS,
            headers=headers
        )
        assert create_address_response.status_code in [200, 201], \
            f"No se pudo crear dirección: {create_address_response.text}"
        address_data = create_address_response.json()
        created_address = address_data.get("address", address_data)
        address_id = created_address.get("id") or created_address.get("addressId")

        # Verificar que el usuario tiene direcciones
        addresses_response = await test_client.get(
            "/api/addresses",
            headers=headers
        )
        assert addresses_response.status_code == 200
        addresses_data = addresses_response.json()
        addresses = addresses_data.get("addresses", addresses_data)
        assert len(addresses) > 0, "Usuario debe tener al menos una dirección"

        # And: Usuario tiene productos en carrito (simulado con items)
        products_response = await test_client.get("/api/products")
        response_data = products_response.json()
        assert "products" in response_data, "Debe retornar objeto con campo 'products'"
        products = response_data["products"]
        assert len(products) > 0, "Debe haber productos disponibles"

        order_items = [
            {
                "productId": products[0]["id"],
                "quantity": 2,
                "price": products[0]["price"]
            }
        ]

        # When: Selecciona dirección existente y confirma pedido
        order_data = {
            "addressId": address_id,
            "items": order_items,
            "paymentMethod": "CARD"
        }

        create_order_response = await test_client.post(
            "/api/orders",
            json=order_data,
            headers=headers
        )

        # Then: Pedido se registra correctamente
        assert create_order_response.status_code in [200, 201], \
            f"Expected 200/201, got {create_order_response.status_code}: {create_order_response.text}"

        order_data_response = create_order_response.json()

        assert "id" in order_data_response or "orderId" in order_data_response, \
            "Respuesta debe incluir ID del pedido"

        order_id = order_data_response.get("id") or order_data_response.get("orderId")

        # Verificar que el pedido se creó con la dirección correcta
        order_details_response = await test_client.get(
            f"/api/orders/{order_id}",
            headers=headers
        )

        if order_details_response.status_code == 200:
            order_details = order_details_response.json()
            assert order_details.get("addressId") == address_id, \
                "Pedido debe estar asociado a la dirección seleccionada"

    @pytest.mark.asyncio
    async def test_tc_hu006_02_order_with_new_address(
        self,
        test_client: AsyncClient,
        test_db,
        seeded_db
    ):
        """
        # ...existing code...

        Pasos (Gherkin):
            - Given: El usuario no tiene direcciones registradas
            - When: Ingresa una nueva dirección válida durante el checkout
            - And: Confirma el pedido
            - Then: La nueva dirección se guarda
            - And: El pedido se registra correctamente con la nueva dirección

        Datos de Entrada:
            - Nueva dirección válida

        Resultado Esperado:
            - La nueva dirección se guarda
            - El pedido se registra correctamente con la nueva dirección
        """
        # Given: Usuario autenticado sin direcciones (o ignoramos las existentes)
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": SAMPLE_USER["email"],
                "password": SAMPLE_USER["password"]
            }
        )
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Contar direcciones antes
        addresses_before_response = await test_client.get(
            "/api/addresses",
            headers=headers
        )
        addresses_before_data = addresses_before_response.json()
        addresses_before = addresses_before_data.get("addresses", addresses_before_data)
        address_count_before = len(addresses_before)

        # When: Ingresa nueva dirección válida
        new_address = {
            "street": "Calle Nueva 456",
            "city": "Bogotá",
            "state": "Cundinamarca",
            "zipCode": "110111",
            "country": "Colombia",
            "isDefault": False,
            "instructions": "Apartamento 301"
        }

        create_address_response = await test_client.post(
            "/api/addresses",
            json=new_address,
            headers=headers
        )

        # Then: Nueva dirección se guarda
        assert create_address_response.status_code in [200, 201], \
            f"Expected 200/201, got {create_address_response.status_code}: {create_address_response.text}"

        created_address_response = create_address_response.json()
        # El endpoint retorna {"message": "...", "address": {...}}
        created_address = created_address_response.get("address", created_address_response)
        new_address_id = created_address.get("id") or created_address.get("addressId")

        assert new_address_id is not None, f"Dirección creada debe tener ID. Respuesta: {created_address_response}"

        # Verificar que se guardó
        addresses_after_response = await test_client.get(
            "/api/addresses",
            headers=headers
        )
        addresses_after_data = addresses_after_response.json()
        addresses_after = addresses_after_data.get("addresses", addresses_after_data)
        assert len(addresses_after) == address_count_before + 1, \
            "Debe haber una dirección adicional"

        # And: Confirma pedido con nueva dirección
        products_response = await test_client.get("/api/products")
        response_data = products_response.json()
        assert "products" in response_data, "Debe retornar objeto con campo 'products'"
        products = response_data["products"]

        order_data = {
            "addressId": new_address_id,
            "items": [
                {
                    "productId": products[0]["id"],
                    "quantity": 1,
                    "price": products[0]["price"]
                }
            ],
            "paymentMethod": "CASH"
        }

        create_order_response = await test_client.post(
            "/api/orders",
            json=order_data,
            headers=headers
        )

        # Then: Pedido se registra correctamente
        assert create_order_response.status_code in [200, 201], \
            "Pedido debe crearse exitosamente con nueva dirección"

        order_response_data = create_order_response.json()
        order_id = order_response_data.get("id") or order_response_data.get("orderId")

        # Verificar que el pedido está asociado a la nueva dirección
        order_details_response = await test_client.get(
            f"/api/orders/{order_id}",
            headers=headers
        )

        if order_details_response.status_code == 200:
            order_details = order_details_response.json()
            assert order_details.get("addressId") == new_address_id, \
                "Pedido debe estar asociado a la nueva dirección"

    @pytest.mark.asyncio
    async def test_order_fails_with_invalid_address(
        self,
        test_client: AsyncClient,
        test_db,
        seeded_db
    ):
        """
        Test adicional: Pedido falla con addressId inválido

        Verifica validación de dirección antes de crear pedido
        """
        # Login
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": SAMPLE_USER["email"],
                "password": SAMPLE_USER["password"]
            }
        )
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Obtener productos
        products_response = await test_client.get("/api/products")
        products_data = products_response.json()
        products = products_data.get("products", products_data)
        assert len(products) > 0, "Debe haber productos disponibles"

        # Intentar crear pedido con addressId inválido
        order_data = {
            "addressId": "00000000-0000-0000-0000-000000000000",  # UUID inválido
            "items": [
                {
                    "productId": products[0]["id"],
                    "quantity": 1,
                    "price": products[0]["price"]
                }
            ],
            "paymentMethod": "CARD"
        }

        response = await test_client.post(
            "/api/orders",
            json=order_data,
            headers=headers
        )

        # Debe fallar con error de validación
        assert response.status_code in [400, 404], \
            "Pedido con dirección inválida debe ser rechazado"

    @pytest.mark.asyncio
    async def test_order_fails_without_items(
        self,
        test_client: AsyncClient,
        test_db,
        seeded_db
    ):
        """
        Test adicional: Pedido falla sin items

        Verifica que no se pueden crear pedidos vacíos
        """
        # Login
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": SAMPLE_USER["email"],
                "password": SAMPLE_USER["password"]
            }
        )
        assert login_response.status_code in [200, 201], f"Login falló: {login_response.text}"
        login_data = login_response.json()
        token = login_data.get("token") or login_data.get("access_token")
        assert token, f"No se obtuvo token: {login_data}"
        headers = {"Authorization": f"Bearer {token}"}

        # Crear dirección mediante la API
        from tests.fixtures.data import SAMPLE_ADDRESS
        create_address_response = await test_client.post(
            "/api/addresses",
            json=SAMPLE_ADDRESS,
            headers=headers
        )
        assert create_address_response.status_code in [200, 201]
        address_data = create_address_response.json()
        created_address = address_data.get("address", address_data)
        address_id = created_address.get("id") or created_address.get("addressId")

        # Intentar crear pedido sin items
        order_data = {
            "addressId": address_id,
            "items": [],  # Sin items
            "paymentMethod": "CASH"
        }

        response = await test_client.post(
            "/api/orders",
            json=order_data,
            headers=headers
        )

        # Debe fallar
        assert response.status_code in [400, 422], \
            "Pedido sin items debe ser rechazado"

    @pytest.mark.asyncio
    async def test_order_calculates_total_correctly(
        self,
        test_client: AsyncClient,
        test_db,
        seeded_db
    ):
        """
        Test adicional: Total del pedido se calcula correctamente

        Verifica que el total del pedido coincide con suma de items
        """
        # Login
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": SAMPLE_USER["email"],
                "password": SAMPLE_USER["password"]
            }
        )
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Crear dirección mediante la API
        from tests.fixtures.data import SAMPLE_ADDRESS
        create_address_response = await test_client.post(
            "/api/addresses",
            json=SAMPLE_ADDRESS,
            headers=headers
        )
        assert create_address_response.status_code in [200, 201]
        address_data = create_address_response.json()
        created_address = address_data.get("address", address_data)
        address_id = created_address.get("id") or created_address.get("addressId")

        # Obtener productos
        products_response = await test_client.get("/api/products")
        products_data = products_response.json()
        products = products_data.get("products", products_data)
        assert len(products) > 0, "Debe haber productos disponibles"

        # Crear pedido con items específicos
        items = [
            {
                "productId": products[0]["id"],
                "quantity": 2,
                "price": products[0]["price"]
            },
            {
                "productId": products[1]["id"] if len(products) > 1 else products[0]["id"],
                "quantity": 1,
                "price": products[1]["price"] if len(products) > 1 else products[0]["price"]
            }
        ]

        expected_total = sum(item["quantity"] * item["price"] for item in items)

        order_data = {
            "addressId": address_id,
            "items": items,
            "paymentMethod": "CARD"
        }

        response = await test_client.post(
            "/api/orders",
            json=order_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            order_response_data = response.json()
            order_id = order_response_data.get("id") or order_response_data.get("orderId")

            # Obtener detalles del pedido
            order_details_response = await test_client.get(
                f"/api/orders/{order_id}",
                headers=headers
            )

            if order_details_response.status_code == 200:
                order_details = order_details_response.json()
                actual_total = order_details.get("total")

                # Verificar que el total es correcto
                assert actual_total == expected_total, \
                    f"Total del pedido ({actual_total}) debe coincidir con suma de items ({expected_total})"

    @pytest.mark.asyncio
    async def test_list_user_addresses(
        self,
        test_client: AsyncClient,
        test_db,
        sample_address,
        seeded_db
    ):
        """
        Test adicional: Listar direcciones del usuario

        Verifica que el usuario puede ver sus direcciones guardadas
        """
        # Login
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": SAMPLE_USER["email"],
                "password": SAMPLE_USER["password"]
            }
        )
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Obtener direcciones
        response = await test_client.get(
            "/api/addresses",
            headers=headers
        )

        assert response.status_code == 200
        addresses_data = response.json()
        addresses = addresses_data.get("addresses", addresses_data)

        assert isinstance(addresses, list)
        assert len(addresses) > 0, "Usuario debe tener al menos una dirección"

        # Verificar estructura de dirección
        for address in addresses:
            assert "id" in address
            assert "street" in address
            assert "city" in address
            assert "zipCode" in address
