"""
Tests E2E para el flujo de inicio de sesión (TC-HU002)

Cobertura:
- TC-HU002-01: Inicio de sesión con credenciales válidas
- TC-HU002-02: Error al iniciar sesión con credenciales inválidas
- TC-HU002-03: Acceso al panel administrativo con rol de administrador
"""
import pytest
from httpx import AsyncClient


class TestUserLoginFlow:
    """
    Suite de tests E2E para el flujo completo de inicio de sesión

    Escenarios basados en TEST_CASES.md:
    - Login exitoso con credenciales válidas
    - Login fallido con credenciales inválidas
    - Acceso diferenciado por rol (admin vs customer)
    """

    @pytest.mark.asyncio
    async def test_tc_hu002_01_valid_credentials_login(self, test_client: AsyncClient, test_db, sample_user):
        """
        TC-HU002-01: Validar el inicio de sesión con credenciales válidas

        Pasos (Gherkin):
        - Given: El usuario se encuentra en la pantalla de inicio de sesión
        - And: Las credenciales ingresadas son válidas
        - When: El usuario envía el formulario de inicio de sesión
        - Then: El usuario accede al sistema
        - And: Es redirigido a su panel correspondiente

        Datos de Entrada:
        - Usuario: cliente@correo.com
        - Contraseña: Valida@123456

        Resultado Esperado:
        - El usuario accede al sistema
        - Es redirigido a su panel correspondiente
        """
        # Given: Usuario en pantalla de login con credenciales válidas
        login_data = {
            "email": sample_user["email"],
            "password": sample_user["password"]
        }

        # When: Envía formulario de login
        response = await test_client.post(
            "/api/auth/login",
            json=login_data
        )

        # Then: Accede al sistema exitosamente
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert "access_token" in data, "Debe retornar access_token"
        assert data["token_type"] == "bearer", "Token type debe ser bearer"
        assert "user" in data, "Debe retornar información del usuario"

        # Verificar información del usuario
        assert data["user"]["email"] == sample_user["email"]
        assert data["user"]["name"] == sample_user["name"]
        assert data["user"]["role"] == sample_user["role"]

        # And: Token debe ser válido para acceder a endpoints protegidos
        # Verificar acceso al perfil con el token
        profile_response = await test_client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )

        assert profile_response.status_code == 200, "Token debe permitir acceso a endpoints protegidos"
        profile_data = profile_response.json()
        assert profile_data["email"] == sample_user["email"]

    @pytest.mark.asyncio
    async def test_tc_hu002_02_invalid_credentials_error(self, test_client: AsyncClient, test_db, sample_user):
        """
        TC-HU002-02: Validar el mensaje de error al iniciar sesión con credenciales inválidas

        Pasos (Gherkin):
        - Given: El usuario se encuentra en la pantalla de inicio de sesión
        - And: Las credenciales ingresadas son inválidas
        - When: El usuario envía el formulario de inicio de sesión
        - Then: El sistema muestra un mensaje de error
        - And: No se permite el acceso al sistema

        Datos de Entrada:
        - Usuario: cliente@correo.com
        - Contraseña: Incorrecta123

        Resultado Esperado:
        - El sistema muestra un mensaje de error
        - No se permite el acceso
        """
        # Given: Usuario con contraseña incorrecta
        login_data = {
            "email": sample_user["email"],
            "password": "ContraseñaIncorrecta123!"  # Contraseña inválida
        }

        # When: Intenta hacer login
        response = await test_client.post(
            "/api/auth/login",
            json=login_data
        )

        # Then: Sistema rechaza el acceso
        assert response.status_code in [401, 403], \
            f"Expected 401/403 Unauthorized, got {response.status_code}"

        data = response.json()
        assert "detail" in data or "message" in data, "Debe retornar mensaje de error"

        error_message = data.get("detail", data.get("message", "")).lower()
        assert any(keyword in error_message for keyword in ["invalid", "incorrect", "wrong", "inválid", "credencial"]), \
            f"Error message should indicate invalid credentials. Got: {error_message}"

        # And: No se retorna token de acceso
        assert "access_token" not in data, "No debería retornar token con credenciales inválidas"

    @pytest.mark.asyncio
    async def test_tc_hu002_03_admin_panel_access(self, test_client: AsyncClient, test_db, sample_admin):
        """
        TC-HU002-03: Validar el acceso al panel administrativo cuando el usuario es administrador

        Pasos (Gherkin):
        - Given: El usuario se encuentra en la pantalla de inicio de sesión
        - And: El usuario tiene rol de administrador
        - When: El usuario ingresa credenciales válidas de administrador
        - And: Envía el formulario
        - Then: El sistema permite el acceso
        - And: Redirige al panel administrativo

        Datos de Entrada:
        - Usuario: admin@correo.com
        - Contraseña: Admin@123456

        Resultado Esperado:
        - El usuario accede al panel administrativo
        """
        # Given: Usuario admin con credenciales válidas
        login_data = {
            "email": sample_admin["email"],
            "password": sample_admin["password"]
        }

        # When: Admin hace login
        response = await test_client.post(
            "/api/auth/login",
            json=login_data
        )

        # Then: Accede exitosamente
        assert response.status_code == 200, f"Admin login should succeed, got {response.status_code}"
        data = response.json()

        assert "access_token" in data
        assert data["user"]["role"] == "ADMIN", "El rol debe ser ADMIN"
        assert data["user"]["email"] == sample_admin["email"]

        # And: Token de admin debe permitir acceso a endpoints administrativos
        admin_token = data["access_token"]

        # Intentar acceder a endpoint de admin (ej: gestión de cupones)
        admin_response = await test_client.get(
            "/api/admin/coupons",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # El endpoint debe responder (puede ser 200 con datos o 200 con lista vacía)
        # No debe ser 403 Forbidden
        assert admin_response.status_code != 403, \
            "Admin token debe permitir acceso a endpoints administrativos"

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email(self, test_client: AsyncClient, test_db):
        """
        Test adicional: Login con email que no existe en el sistema

        Verifica que el sistema rechaza intentos de login con usuarios inexistentes
        """
        login_data = {
            "email": "usuario_inexistente@example.com",
            "password": "CualquierPassword123!"
        }

        response = await test_client.post(
            "/api/auth/login",
            json=login_data
        )

        assert response.status_code in [401, 404], \
            "Login con email inexistente debe ser rechazado"

        data = response.json()
        assert "access_token" not in data, "No debería retornar token"

    @pytest.mark.asyncio
    async def test_customer_cannot_access_admin_endpoints(self, test_client: AsyncClient, test_db, sample_user):
        """
        Test adicional: Validar que usuario regular no puede acceder a endpoints de admin

        Verifica separación de permisos por rol
        """
        # Given: Usuario regular hace login
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": sample_user["email"],
                "password": sample_user["password"]
            }
        )

        assert login_response.status_code == 200
        customer_token = login_response.json()["access_token"]

        # When: Intenta acceder a endpoint de admin
        admin_response = await test_client.get(
            "/api/admin/coupons",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        # Then: Acceso es denegado
        assert admin_response.status_code == 403, \
            "Usuario CUSTOMER no debe acceder a endpoints de admin"

    @pytest.mark.asyncio
    async def test_login_without_credentials(self, test_client: AsyncClient, test_db):
        """
        Test adicional: Login sin credenciales

        Verifica manejo de requests malformados
        """
        response = await test_client.post(
            "/api/auth/login",
            json={}
        )

        assert response.status_code == 422, \
            "Login sin credenciales debe retornar 422 Validation Error"
