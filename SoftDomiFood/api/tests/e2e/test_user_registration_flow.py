"""
Tests E2E para el flujo de registro de usuario (TC-HU001)

Cobertura:
- TC-HU001-01: Registro exitoso con email y contraseña válidos
- TC-HU001-02: Error al intentar registrarse con email existente
"""
import pytest
from httpx import AsyncClient
from tests.fixtures.data import SAMPLE_USER, SAMPLE_ADMIN
import uuid


class TestUserRegistrationFlow:
    """
    Suite de tests E2E para el flujo completo de registro de usuario

    Escenarios basados en TEST_CASES.md:
    - Registro exitoso
    - Validación de email duplicado
    """

    @pytest.mark.asyncio
    async def test_tc_hu001_01_successful_registration(self, test_client: AsyncClient, test_db):
        """
        TC-HU001-01: Validar el registro exitoso de un cliente con email y contraseña válidos

        Pasos (Gherkin):
        - Given: El usuario se encuentra en la pantalla de registro
        - And: El email no existe previamente en el sistema
        - When: El usuario ingresa un email válido y una contraseña válida
        - And: Envía el formulario de registro
        - Then: La cuenta es creada exitosamente
        - And: El usuario puede iniciar sesión en el sistema

        Datos de Entrada:
        - Email: usuario_nuevo@correo.com
        - Contraseña: Prueba@123456

        Resultado Esperado:
        - La cuenta es creada exitosamente
        - El usuario puede iniciar sesión
        """
        # Given: Usuario en pantalla de registro con email único
        unique_id = str(uuid.uuid4())[:8]
        registration_data = {
            "email": f"usuario_nuevo_{unique_id}@correo.com",
            "password": "Prueba@123456",
            "name": "Usuario Nuevo",
            "phone": "+57 300 999 8888"
        }

        # When: Envía formulario de registro
        response = await test_client.post(
            "/api/auth/register",
            json=registration_data
        )

        # Then: La cuenta es creada exitosamente
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()

        assert "user" in data
        assert data["user"]["email"] == registration_data["email"]
        assert data["user"]["name"] == registration_data["name"]
        assert "id" in data["user"]

        # And: El usuario puede iniciar sesión
        login_response = await test_client.post(
            "/api/auth/login",
            json={
                "email": registration_data["email"],
                "password": registration_data["password"]
            }
        )

        assert login_response.status_code in [200, 201], f"Login failed: {login_response.text}"
        login_data = login_response.json()
        token = login_data.get("token") or login_data.get("access_token")
        assert token, f"Debe retornar token JWT, respuesta: {login_data}"
        assert login_data["user"]["email"] == registration_data["email"]

    @pytest.mark.asyncio
    async def test_tc_hu001_02_duplicate_email_error(self, test_client: AsyncClient, test_db):
        """
        TC-HU001-02: Validar el mensaje de error al intentar registrarse con un email ya existente

        Pasos (Gherkin):
        - Given: El usuario se encuentra en la pantalla de registro
        - And: El email ya existe en el sistema
        - When: El usuario ingresa el email existente y una contraseña válida
        - And: Envía el formulario de registro
        - Then: El sistema muestra un mensaje indicando que el email ya está en uso
        - And: La cuenta no es creada

        Datos de Entrada:
        - Email: usuario_existente@correo.com (sample_user email)
        - Contraseña: Prueba@123456

        Resultado Esperado:
        - El sistema informa que el email ya está en uso
        - No se crea la cuenta
        """
        # Given: Usuario con email que ya existe (sample_user)
        existing_email = SAMPLE_USER["email"]

        # Verificar que el usuario existe
        user_count_before = await test_db.fetchval(
            "SELECT COUNT(*) FROM users WHERE email = $1",
            existing_email
        )
        assert user_count_before == 1, "El usuario de prueba debe existir"

        # When: Intenta registrarse con email existente
        registration_data = {
            "email": existing_email,  # Email duplicado
            "password": "Prueba@123456",
            "name": "Otro Usuario",
            "phone": "+57 300 111 2222"
        }

        response = await test_client.post(
            "/api/auth/register",
            json=registration_data
        )

        # Then: Sistema rechaza el registro
        assert response.status_code in [400, 409], f"Expected 400/409, got {response.status_code}"
        data = response.json()

        assert "detail" in data or "message" in data
        error_message = data.get("detail", data.get("message", "")).lower()
        assert any(keyword in error_message for keyword in ["already", "exists", "registered", "duplicado"]), \
            f"Error message should indicate email already exists. Got: {error_message}"

        # And: No se creó una cuenta adicional
        user_count_after = await test_db.fetchval(
            "SELECT COUNT(*) FROM users WHERE email = $1",
            existing_email
        )
        assert user_count_after == 1, "No debería crearse un usuario duplicado"

    @pytest.mark.asyncio
    async def test_registration_with_invalid_email_format(self, test_client: AsyncClient, test_db):
        """
        Test adicional: Validación de formato de email inválido

        Verifica que el sistema rechaza emails con formato incorrecto
        """
        invalid_emails = [
            "not-an-email",
            "@missing-local.com",
            "missing-at-sign.com",
            "double@@at.com"
        ]

        for invalid_email in invalid_emails:
            response = await test_client.post(
                "/api/auth/register",
                json={
                    "email": invalid_email,
                    "password": "ValidPass123!",
                    "name": "Test User",
                    "phone": "+57 300 000 0000"
                }
            )

            assert response.status_code == 422, \
                f"Email '{invalid_email}' debería ser rechazado con 422 Validation Error"

    @pytest.mark.asyncio
    async def test_registration_with_weak_password(self, test_client: AsyncClient, test_db):
        """
        Test adicional: Validación de contraseña débil

        Verifica que el sistema rechaza contraseñas que no cumplen requisitos de seguridad
        """
        weak_passwords = [
            "123",           # Muy corta
            "password",      # Sin números ni caracteres especiales
            "12345678",      # Solo números
            "abcdefgh"       # Solo letras
        ]

        for weak_password in weak_passwords:
            unique_id = str(uuid.uuid4())[:8]
            response = await test_client.post(
                "/api/auth/register",
                json={
                    "email": f"test_{unique_id}@example.com",
                    "password": weak_password,
                    "name": "Test User",
                    "phone": "+57 300 000 0000"
                }
            )

            # Puede ser 422 (validation error) o 400 (business rule)
            assert response.status_code in [400, 422], \
                f"Password débil '{weak_password}' debería ser rechazada"
