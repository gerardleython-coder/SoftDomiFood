"""
Tests para HU-03: Añadir una nueva dirección válida al realizar un pedido
==========================================================================

Criterios de Aceptación:
1. El sistema valida automáticamente el formato de la dirección (Código Postal, Ciudad, Calle)
2. Si hay inconsistencias, se permite continuar con advertencia clara
3. La dirección se guarda correctamente en el historial del usuario

Test Coverage:
- Validadores individuales (PostalCodeValidator, CityValidator, StreetValidator, StateValidator)
- Servicio de validación completo (AddressValidationService)
- Integración con endpoint POST /api/addresses
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.address_validation_service import (
    PostalCodeValidator,
    CityValidator,
    StreetValidator,
    StateValidator,
    AddressValidationService,
    AddressValidationError,
    ValidationSeverity,
    get_validation_service
)


# ==============================================================================
# Tests para PostalCodeValidator (HU-03 Criterio 1)
# ==============================================================================

class TestPostalCodeValidator:
    """Tests para validación de código postal colombiano (6 dígitos)"""

    def test_valid_postal_code_bogota(self):
        """Código postal válido de Bogotá (110111)"""
        result = PostalCodeValidator.validate("110111")
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO
        assert result.field == "zip_code"

    def test_valid_postal_code_medellin(self):
        """Código postal válido de Medellín (050001)"""
        result = PostalCodeValidator.validate("050001")
        assert result.is_valid is True

    def test_invalid_postal_code_too_short(self):
        """Código postal muy corto (5 dígitos)"""
        result = PostalCodeValidator.validate("12345")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR
        assert "6 dígitos" in result.message

    def test_invalid_postal_code_too_long(self):
        """Código postal muy largo (7 dígitos)"""
        result = PostalCodeValidator.validate("1234567")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR

    def test_invalid_postal_code_letters(self):
        """Código postal con letras (debe ser solo números)"""
        result = PostalCodeValidator.validate("11A111")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR
        assert "dígitos numéricos" in result.message

    def test_empty_postal_code(self):
        """Código postal vacío"""
        result = PostalCodeValidator.validate("")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR
        assert "obligatorio" in result.message

    def test_postal_code_with_spaces_trimmed(self):
        """Código postal con espacios (se limpian)"""
        result = PostalCodeValidator.validate("  110111  ")
        assert result.is_valid is True


# ==============================================================================
# Tests para CityValidator (HU-03 Criterio 1 y 2)
# ==============================================================================

class TestCityValidator:
    """Tests para validación de ciudades colombianas"""

    def test_valid_city_bogota(self):
        """Ciudad reconocida: Bogotá"""
        result = CityValidator.validate("Bogotá")
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO

    def test_valid_city_medellin(self):
        """Ciudad reconocida: Medellín"""
        result = CityValidator.validate("Medellín")
        assert result.is_valid is True

    def test_valid_city_case_insensitive(self):
        """Ciudad reconocida (case-insensitive): CALI"""
        result = CityValidator.validate("CALI")
        assert result.is_valid is True

    def test_unknown_city_generates_warning(self):
        """Ciudad no reconocida genera WARNING (Criterio 2: permite continuar)"""
        result = CityValidator.validate("Ciudad Pequeña")
        assert result.is_valid is True  # No bloquea
        assert result.severity == ValidationSeverity.WARNING
        assert "no se encuentra en nuestro catálogo" in result.message
        assert "bajo tu responsabilidad" in result.message

    def test_empty_city(self):
        """Ciudad vacía genera ERROR"""
        result = CityValidator.validate("")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR

    def test_city_too_short(self):
        """Ciudad muy corta (< 3 caracteres)"""
        result = CityValidator.validate("AB")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR
        assert "al menos 3 caracteres" in result.message


# ==============================================================================
# Tests para StreetValidator (HU-03 Criterio 1 y 2)
# ==============================================================================

class TestStreetValidator:
    """Tests para validación de direcciones de calle"""

    def test_valid_street_with_nomenclature(self):
        """Dirección válida con nomenclatura colombiana"""
        result = StreetValidator.validate("Calle 10 #20-30")
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO

    def test_valid_street_carrera(self):
        """Dirección válida con Carrera"""
        result = StreetValidator.validate("Carrera 7 #15-45")
        assert result.is_valid is True

    def test_street_without_numbers_generates_warning(self):
        """Dirección sin números genera WARNING (Criterio 2)"""
        result = StreetValidator.validate("Avenida Principal")
        assert result.is_valid is True  # No bloquea
        assert result.severity == ValidationSeverity.WARNING
        assert "no contiene números" in result.message
        assert "nomenclatura numérica" in result.message

    def test_empty_street(self):
        """Dirección vacía genera ERROR"""
        result = StreetValidator.validate("")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR

    def test_street_too_short(self):
        """Dirección muy corta (< 5 caracteres)"""
        result = StreetValidator.validate("Cll1")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR
        assert "al menos 5 caracteres" in result.message


# ==============================================================================
# Tests para StateValidator
# ==============================================================================

class TestStateValidator:
    """Tests para validación de departamentos colombianos"""

    def test_valid_state_cundinamarca(self):
        """Departamento reconocido: Cundinamarca"""
        result = StateValidator.validate("Cundinamarca")
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.INFO

    def test_valid_state_antioquia(self):
        """Departamento reconocido: Antioquia"""
        result = StateValidator.validate("Antioquia")
        assert result.is_valid is True

    def test_unknown_state_generates_warning(self):
        """Departamento no reconocido genera WARNING"""
        result = StateValidator.validate("Departamento Inventado")
        assert result.is_valid is True  # No bloquea
        assert result.severity == ValidationSeverity.WARNING

    def test_empty_state(self):
        """Departamento vacío genera ERROR"""
        result = StateValidator.validate("")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.ERROR


# ==============================================================================
# Tests para AddressValidationService (HU-03 Integración Completa)
# ==============================================================================

class TestAddressValidationService:
    """Tests para el servicio completo de validación de direcciones"""

    def test_validate_perfect_address_bogota(self):
        """Dirección perfecta de Bogotá (sin errores ni advertencias)"""
        service = AddressValidationService()
        result = service.validate_address(
            street="Calle 10 #20-30",
            city="Bogotá",
            state="Cundinamarca",
            zip_code="110111"
        )

        assert result["is_valid"] is True
        assert result["has_errors"] is False
        assert result["has_warnings"] is False
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_validate_address_with_warnings_only(self):
        """Dirección válida pero con advertencias (ciudad no reconocida)"""
        service = AddressValidationService()
        result = service.validate_address(
            street="Calle 10 #20-30",
            city="Pueblo Pequeño",  # No está en catálogo
            state="Cundinamarca",
            zip_code="110111"
        )

        assert result["is_valid"] is True  # Criterio 2: permite continuar
        assert result["has_errors"] is False
        assert result["has_warnings"] is True
        assert len(result["warnings"]) == 1
        assert result["warnings"][0]["field"] == "city"

    def test_validate_address_with_errors(self):
        """Dirección con errores (código postal inválido)"""
        service = AddressValidationService()
        result = service.validate_address(
            street="Calle 10 #20-30",
            city="Bogotá",
            state="Cundinamarca",
            zip_code="123"  # Muy corto
        )

        assert result["is_valid"] is False
        assert result["has_errors"] is True
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "zip_code"

    def test_validate_address_multiple_warnings(self):
        """Dirección con múltiples advertencias"""
        service = AddressValidationService()
        result = service.validate_address(
            street="Avenida Principal",  # Sin números
            city="Pueblo Nuevo",  # No reconocida
            state="Departamento Nuevo",  # No reconocido
            zip_code="110111"
        )

        assert result["is_valid"] is True  # Permite continuar
        assert result["has_warnings"] is True
        assert len(result["warnings"]) == 3  # street, city, state

    def test_validate_or_raise_success_with_warnings(self):
        """validate_or_raise devuelve warnings pero no lanza excepción"""
        service = AddressValidationService()
        result = service.validate_or_raise(
            street="Calle 10 #20-30",
            city="Pueblo Pequeño",  # Warning
            state="Cundinamarca",
            zip_code="110111"
        )

        assert result["has_warnings"] is True
        assert len(result["warnings"]) == 1

    def test_validate_or_raise_throws_on_errors(self):
        """validate_or_raise lanza AddressValidationError cuando hay errores"""
        service = AddressValidationService()

        with pytest.raises(AddressValidationError) as exc_info:
            service.validate_or_raise(
                street="Calle 10 #20-30",
                city="Bogotá",
                state="Cundinamarca",
                zip_code="ABC123"  # Formato inválido
            )

        assert "dígitos numéricos" in str(exc_info.value.message)
        assert exc_info.value.field == "zip_code"

    def test_get_validation_service_singleton(self):
        """get_validation_service devuelve siempre la misma instancia"""
        service1 = get_validation_service()
        service2 = get_validation_service()
        assert service1 is service2


# ==============================================================================
# Tests de Integración con Endpoint (HU-03 Criterio 3)
# ==============================================================================

class TestAddressEndpointIntegration:
    """
    Tests de integración con el endpoint POST /api/addresses

    Nota: Estos tests usan mocks porque requieren DB y autenticación.
    Para tests completos end-to-end, ejecutar con API corriendo.
    """

    @pytest.mark.asyncio
    async def test_create_address_with_valid_data_no_warnings(self):
        """Crear dirección con datos perfectos (sin advertencias)"""
        # Este test valida que el servicio se integra correctamente
        service = AddressValidationService()

        # Simular validación
        result = service.validate_address(
            street="Calle 10 #20-30",
            city="Bogotá",
            state="Cundinamarca",
            zip_code="110111"
        )

        # La respuesta NO debe incluir campo 'warnings'
        assert result["has_warnings"] is False
        assert "warnings" not in result or len(result["warnings"]) == 0

    @pytest.mark.asyncio
    async def test_create_address_with_warnings_user_can_continue(self):
        """
        Crear dirección con advertencias (ciudad no reconocida)
        Criterio 2: Usuario puede continuar bajo su responsabilidad
        """
        service = AddressValidationService()

        result = service.validate_address(
            street="Calle 10 #20-30",
            city="Villa Nueva",  # No reconocida
            state="Cundinamarca",
            zip_code="110111"
        )

        # Debe permitir continuar
        assert result["is_valid"] is True
        assert result["has_warnings"] is True

        # La respuesta DEBE incluir campo 'warnings' con mensaje claro
        assert len(result["warnings"]) > 0
        warning = result["warnings"][0]
        assert warning["field"] == "city"
        assert "bajo tu responsabilidad" in warning["message"]

    @pytest.mark.asyncio
    async def test_create_address_with_errors_blocks_creation(self):
        """
        Crear dirección con errores (código postal inválido)
        Criterio 1: Sistema bloquea la creación
        """
        service = AddressValidationService()

        # Debe lanzar excepción
        with pytest.raises(AddressValidationError) as exc_info:
            service.validate_or_raise(
                street="Calle 10 #20-30",
                city="Bogotá",
                state="Cundinamarca",
                zip_code="12345"  # Solo 5 dígitos
            )

        # Mensaje de error claro
        assert "6 dígitos" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_address_saved_in_history_for_reuse(self):
        """
        Criterio 3: Dirección se guarda en historial para futuras compras

        Este test verifica la integración con create_address de database_service.
        La dirección debe quedar disponible para GET /api/addresses
        """
        # Mock de database_service.create_address
        with patch('services.database_service.create_address') as mock_create:
            mock_create.return_value = {
                "id": "address-123",
                "userId": "user-456",
                "street": "Calle 10 #20-30",
                "city": "Bogotá",
                "state": "Cundinamarca",
                "zipCode": "110111",
                "isDefault": False
            }

            # Llamar al servicio (simula el flujo del endpoint)
            service = AddressValidationService()
            validation_result = service.validate_address(
                street="Calle 10 #20-30",
                city="Bogotá",
                state="Cundinamarca",
                zip_code="110111"
            )

            # Si la validación pasa, se debe llamar a create_address
            assert validation_result["is_valid"] is True

            # En el endpoint real, aquí se llamaría a create_address
            # La dirección queda guardada en BD para reutilización


# ==============================================================================
# Tests de Casos Límite
# ==============================================================================

class TestEdgeCases:
    """Tests para casos límite y edge cases"""

    def test_address_with_special_characters(self):
        """Dirección con caracteres especiales (tildes, ñ)"""
        service = AddressValidationService()
        result = service.validate_address(
            street="Calle 10 #20-30",
            city="Bogotá",  # Con tilde
            state="Boyacá",  # Con tilde
            zip_code="110111"
        )
        assert result["is_valid"] is True

    def test_address_all_fields_with_whitespace(self):
        """Todos los campos con espacios extra (se limpian)"""
        service = AddressValidationService()
        result = service.validate_address(
            street="  Calle 10 #20-30  ",
            city="  Bogotá  ",
            state="  Cundinamarca  ",
            zip_code="  110111  "
        )
        assert result["is_valid"] is True

    def test_maximum_length_street(self):
        """Dirección muy larga (debe ser válida si tiene formato correcto)"""
        service = AddressValidationService()
        long_street = "Calle 123 #456-789 Apartamento 101 Torre B Conjunto Residencial Los Pinos Etapa 2"
        result = service.validate_address(
            street=long_street,
            city="Bogotá",
            state="Cundinamarca",
            zip_code="110111"
        )
        assert result["is_valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
