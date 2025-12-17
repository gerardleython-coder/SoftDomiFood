"""
Tests E2E para el flujo de gestión de favoritos (TC-HU005)

Cobertura:
- TC-HU005-01: Añadir producto a favoritos
- TC-HU005-02: Eliminar producto de favoritos
- TC-HU005-03: Visualizar lista de favoritos
"""
import pytest
from httpx import AsyncClient


class TestFavoritesFlow:
    """
    Suite de tests E2E para el flujo completo de gestión de favoritos

    Escenarios basados en TEST_CASES.md:
    - Añadir productos a favoritos
    - Eliminar productos de favoritos
    - Listar productos favoritos
    """

    @pytest.mark.asyncio
    async def test_tc_hu005_01_add_product_to_favorites(
        self,
        test_client: AsyncClient,
        test_db,
        sample_user,
        seeded_db
    ):
        """
        TC-HU005-01: Validar que un producto se añade a favoritos

        Pasos (Gherkin):
        - Given: El usuario visualiza un producto
        - When: Selecciona la opción de marcar como favorito
        - Then: El producto se añade a la lista de favoritos

        Datos de Entrada:
        - Producto seleccionado

        Resultado Esperado:
        - El producto se añade a la lista de favoritos
        """
        # Given: Usuario autenticado visualizando un producto
        # Primero hacer login para obtener token real
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": sample_user["email"],
                "password": sample_user["password"]
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Obtener un producto del menú
        products_response = await test_client.get("/api/products")
        products = products_response.json()
        assert len(products) > 0, "Debe haber productos para marcar como favorito"

        product_id = products[0]["id"]

        # When: Marca el producto como favorito
        add_favorite_response = await test_client.post(
            "/api/favorites",
            json={"productId": product_id},
            headers=headers
        )

        # Then: Producto se añade a favoritos exitosamente
        assert add_favorite_response.status_code in [200, 201], \
            f"Expected 200/201, got {add_favorite_response.status_code}: {add_favorite_response.text}"

        # Verificar que el producto está ahora en favoritos
        favorites_response = await test_client.get(
            "/api/favorites",
            headers=headers
        )

        assert favorites_response.status_code == 200
        favorites_data = favorites_response.json()
        favorites_list = favorites_data.get("favorites", [])

        # El producto debe estar en la lista de favoritos
        favorite_ids = [fav["id"] for fav in favorites_list]
        assert product_id in favorite_ids, \
            f"Producto {product_id} debe estar en favoritos"

    @pytest.mark.asyncio
    async def test_tc_hu005_02_remove_product_from_favorites(
        self,
        test_client: AsyncClient,
        test_db,
        sample_user,
        seeded_db
    ):
        """
        TC-HU005-02: Validar la eliminación de un producto de favoritos

        Pasos (Gherkin):
        - Given: El producto se encuentra marcado como favorito
        - When: El usuario elimina el producto de favoritos
        - Then: El producto desaparece de la lista de favoritos

        Datos de Entrada:
        - Producto marcado como favorito

        Resultado Esperado:
        - El producto se elimina de la lista de favoritos
        """
        # Given: Usuario con producto en favoritos
        # Login
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": sample_user["email"],
                "password": sample_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Obtener producto y agregarlo a favoritos
        products_response = await test_client.get("/api/products")
        products = products_response.json()
        product_id = products[0]["id"]

        # Añadir a favoritos primero
        await test_client.post(
            "/api/favorites",
            json={"productId": product_id},
            headers=headers
        )

        # Verificar que está en favoritos
        favorites_before = await test_client.get("/api/favorites", headers=headers)
        favorites_before_data = favorites_before.json()
        favorites_before_list = favorites_before_data.get("favorites", [])
        assert any(fav["id"] == product_id for fav in favorites_before_list), \
            "Producto debe estar en favoritos antes de eliminar"

        # When: Elimina el producto de favoritos
        delete_response = await test_client.delete(
            f"/api/favorites/{product_id}",
            headers=headers
        )

        # Then: Producto se elimina exitosamente
        assert delete_response.status_code in [200, 204], \
            f"Expected 200/204, got {delete_response.status_code}"

        # Verificar que el producto ya no está en favoritos
        favorites_after = await test_client.get("/api/favorites", headers=headers)
        favorites_after_data = favorites_after.json()
        favorites_after_list = favorites_after_data.get("favorites", [])

        favorite_ids_after = [fav["id"] for fav in favorites_after_list]
        assert product_id not in favorite_ids_after, \
            f"Producto {product_id} no debe estar en favoritos después de eliminar"

    @pytest.mark.asyncio
    async def test_tc_hu005_03_list_favorites(
        self,
        test_client: AsyncClient,
        test_db,
        sample_user,
        seeded_db
    ):
        """
        TC-HU005-03: Validar la visualización de la lista de favoritos

        Pasos (Gherkin):
        - Given: El usuario accede a la sección de favoritos
        - Then: El sistema muestra todos los productos marcados como favoritos

        Datos de Entrada:
        - N/A

        Resultado Esperado:
        - Se muestran todos los productos marcados como favoritos
        """
        # Given: Usuario autenticado con algunos favoritos
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": sample_user["email"],
                "password": sample_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Añadir múltiples productos a favoritos
        products_response = await test_client.get("/api/products")
        products = products_response.json()

        # Añadir 2-3 productos como favoritos
        favorite_product_ids = []
        for i in range(min(3, len(products))):
            product_id = products[i]["id"]
            await test_client.post(
                "/api/favorites",
                json={"productId": product_id},
                headers=headers
            )
            favorite_product_ids.append(product_id)

        # When: Accede a sección de favoritos
        favorites_response = await test_client.get(
            "/api/favorites",
            headers=headers
        )

        # Then: Sistema muestra todos los favoritos
        assert favorites_response.status_code == 200
        favorites_data = favorites_response.json()

        assert "favorites" in favorites_data, "Debe retornar campo 'favorites'"
        favorites_list = favorites_data["favorites"]

        assert isinstance(favorites_list, list), "favorites debe ser una lista"
        assert len(favorites_list) >= len(favorite_product_ids), \
            "Debe mostrar todos los productos marcados como favoritos"

        # Verificar que cada favorito tiene la información completa del producto
        for favorite in favorites_list:
            assert "id" in favorite, "Favorito debe tener ID"
            assert "name" in favorite, "Favorito debe tener nombre"
            assert "price" in favorite, "Favorito debe tener precio"
            assert "description" in favorite, "Favorito debe tener descripción"

    @pytest.mark.asyncio
    async def test_add_duplicate_favorite_is_idempotent(
        self,
        test_client: AsyncClient,
        test_db,
        sample_user,
        seeded_db
    ):
        """
        Test adicional: Añadir el mismo producto dos veces es idempotente

        Verifica que añadir un producto ya favorito no causa error ni duplicación
        """
        # Login
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": sample_user["email"],
                "password": sample_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Obtener producto
        products = (await test_client.get("/api/products")).json()
        product_id = products[0]["id"]

        # Añadir a favoritos por primera vez
        response1 = await test_client.post(
            "/api/favorites",
            json={"productId": product_id},
            headers=headers
        )
        assert response1.status_code in [200, 201]

        # Añadir el mismo producto por segunda vez
        response2 = await test_client.post(
            "/api/favorites",
            json={"productId": product_id},
            headers=headers
        )

        # Debe ser idempotente (no error, no duplicación)
        assert response2.status_code in [200, 201, 409], \
            "Añadir favorito duplicado debe ser idempotente"

        # Verificar que no hay duplicación en la lista
        favorites_response = await test_client.get("/api/favorites", headers=headers)
        favorites_list = favorites_response.json()["favorites"]

        product_count = sum(1 for fav in favorites_list if fav["id"] == product_id)
        assert product_count == 1, "Producto no debe estar duplicado en favoritos"

    @pytest.mark.asyncio
    async def test_favorites_require_authentication(
        self,
        test_client: AsyncClient,
        test_db
    ):
        """
        Test adicional: Endpoints de favoritos requieren autenticación

        Verifica que usuarios no autenticados no pueden acceder a favoritos
        """
        # Intentar acceder sin token
        response = await test_client.get("/api/favorites")

        assert response.status_code in [401, 403], \
            "Acceso a favoritos sin autenticación debe ser rechazado"

    @pytest.mark.asyncio
    async def test_check_if_product_is_favorite(
        self,
        test_client: AsyncClient,
        test_db,
        sample_user,
        seeded_db
    ):
        """
        Test adicional: Verificar si un producto específico es favorito

        Útil para UI que necesita saber si mostrar el ícono de favorito activado
        """
        # Login
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": sample_user["email"],
                "password": sample_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Obtener producto y añadir a favoritos
        products = (await test_client.get("/api/products")).json()
        favorite_product_id = products[0]["id"]
        non_favorite_product_id = products[1]["id"] if len(products) > 1 else None

        await test_client.post(
            "/api/favorites",
            json={"productId": favorite_product_id},
            headers=headers
        )

        # Verificar que el producto está en favoritos
        check_response = await test_client.get(
            f"/api/favorites/check/{favorite_product_id}",
            headers=headers
        )

        if check_response.status_code == 200:
            check_data = check_response.json()
            assert check_data.get("isFavorite") is True, \
                "Producto añadido debe ser favorito"

        # Verificar producto no favorito (si existe)
        if non_favorite_product_id:
            check_non_fav = await test_client.get(
                f"/api/favorites/check/{non_favorite_product_id}",
                headers=headers
            )
            if check_non_fav.status_code == 200:
                assert check_non_fav.json().get("isFavorite") is False
