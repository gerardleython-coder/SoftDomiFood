"""
Address Validation Service
==========================

Valida direcciones con múltiples niveles:
1. Validación de formato (offline) - Obligatoria
2. Validación semántica (catálogo ciudades) - Genera advertencias
3. Geocoding (futuro) - Opcional

Implementación de HU-03:
- Criterio 1: Validación automática de formato (Código Postal, Ciudad, Calle)
- Criterio 2: Advertencias cuando hay inconsistencias (usuario puede continuar)
- Criterio 3: Dirección se guarda correctamente (ya implementado en database_service)

Patrones aplicados:
- Strategy Pattern: Diferentes validadores por nivel de severidad
- Chain of Responsibility: Validaciones en cadena
- SRP: Cada clase valida un aspecto específico
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ValidationSeverity(str, Enum):
    """Severidad de los problemas de validación"""
    ERROR = "error"      # Bloquea la creación
    WARNING = "warning"  # Permite continuar con advertencia
    INFO = "info"        # Información adicional


class ValidationResult:
    """Resultado de una validación individual"""

    def __init__(self, is_valid: bool, severity: ValidationSeverity,
                 field: str, message: str):
        self.is_valid = is_valid
        self.severity = severity
        self.field = field
        self.message = message

    def to_dict(self) -> Dict:
        return {
            "field": self.field,
            "severity": self.severity.value,
            "message": self.message,
            "is_valid": self.is_valid
        }


class AddressValidationError(Exception):
    """Excepción personalizada para errores de validación de dirección"""

    def __init__(self, message: str, field: str, validation_results: List[ValidationResult] = None):
        self.message = message
        self.field = field
        self.validation_results = validation_results or []
        super().__init__(self.message)


class PostalCodeValidator:
    """
    Valida códigos postales de Colombia.

    Formato: 6 dígitos (ej: 110111, 050001)
    Referencia: Sistema postal DIVIPOLA del DANE
    """

    POSTAL_CODE_PATTERN = re.compile(r'^\d{6}$')

    @staticmethod
    def validate(zip_code: str) -> ValidationResult:
        """
        Valida formato de código postal colombiano.

        Args:
            zip_code: Código postal a validar

        Returns:
            ValidationResult con el resultado de la validación
        """
        if not zip_code or not zip_code.strip():
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="zip_code",
                message="El código postal es obligatorio"
            )

        zip_code_clean = zip_code.strip()

        if not PostalCodeValidator.POSTAL_CODE_PATTERN.match(zip_code_clean):
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="zip_code",
                message="El código postal debe tener exactamente 6 dígitos numéricos. "
                       f"Ejemplo: 110111 (Bogotá), 050001 (Medellín). Recibido: '{zip_code_clean}'"
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            field="zip_code",
            message="Código postal válido"
        )


class CityValidator:
    """
    Valida ciudades de Colombia.

    Incluye catálogo de ciudades principales y capitales departamentales.
    Genera WARNING si la ciudad no está en el catálogo (no bloquea).
    """

    # Catálogo de ciudades principales de Colombia
    KNOWN_CITIES = {
        # Ciudades principales (más de 100k habitantes)
        "bogotá", "bogota", "medellín", "medellin", "cali", "barranquilla",
        "cartagena", "cúcuta", "cucuta", "soledad", "ibagué", "ibague",
        "bucaramanga", "soacha", "santa marta", "villavicencio", "valledupar",
        "pereira", "montería", "monteria", "manizales", "neiva", "pasto",
        "armenia", "sincelejo", "popayán", "popayan", "tunja", "florencia",
        "riohacha", "quibdó", "quibdo", "yopal", "leticia", "inírida", "inirida",
        "san josé del guaviare", "san jose del guaviare", "puerto carreño",
        "mocoa", "mitú", "mitu", "arauca",

        # Ciudades intermedias importantes
        "itagüí", "itagui", "palmira", "buenaventura", "tuluá", "tulua",
        "envigado", "bello", "girardot", "chía", "chia", "zipaquirá", "zipaquira",
        "facatativá", "facatativa", "madrid", "mosquera", "funza", "cajicá", "cajica"
    }

    @staticmethod
    def validate(city: str) -> ValidationResult:
        """
        Valida nombre de ciudad.

        Args:
            city: Nombre de la ciudad

        Returns:
            ValidationResult con el resultado de la validación
        """
        if not city or not city.strip():
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="city",
                message="El nombre de la ciudad es obligatorio"
            )

        city_clean = city.strip().lower()

        # Validación de formato básico
        if len(city_clean) < 3:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="city",
                message="El nombre de la ciudad debe tener al menos 3 caracteres"
            )

        # Verificar si está en el catálogo
        if city_clean not in CityValidator.KNOWN_CITIES:
            return ValidationResult(
                is_valid=True,  # No bloquea
                severity=ValidationSeverity.WARNING,
                field="city",
                message=f"La ciudad '{city.strip()}' no se encuentra en nuestro catálogo. "
                       "Por favor, verifica que esté correctamente escrita. "
                       "Puedes continuar bajo tu responsabilidad."
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            field="city",
            message="Ciudad reconocida"
        )


class StreetValidator:
    """
    Valida formato de calle/dirección.

    Validaciones:
    - Longitud mínima
    - Presencia de números/nomenclatura
    """

    @staticmethod
    def validate(street: str) -> ValidationResult:
        """
        Valida formato de calle.

        Args:
            street: Dirección de calle

        Returns:
            ValidationResult con el resultado de la validación
        """
        if not street or not street.strip():
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="street",
                message="La dirección de calle es obligatoria"
            )

        street_clean = street.strip()

        # Validación de longitud mínima
        if len(street_clean) < 5:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="street",
                message="La dirección debe tener al menos 5 caracteres. "
                       "Ejemplo: 'Calle 10 #20-30', 'Carrera 7 #15-45'"
            )

        # Validación de presencia de números (nomenclatura)
        has_numbers = bool(re.search(r'\d', street_clean))
        if not has_numbers:
            return ValidationResult(
                is_valid=True,  # No bloquea
                severity=ValidationSeverity.WARNING,
                field="street",
                message="La dirección no contiene números. Las direcciones en Colombia "
                       "suelen incluir nomenclatura numérica (ej: Calle 10 #20-30). "
                       "Verifica que la dirección esté completa."
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            field="street",
            message="Dirección válida"
        )


class StateValidator:
    """
    Valida departamentos de Colombia.
    """

    # Departamentos de Colombia
    KNOWN_STATES = {
        "amazonas", "antioquia", "arauca", "atlántico", "atlantico",
        "bolívar", "bolivar", "boyacá", "boyaca", "caldas", "caquetá", "caqueta",
        "casanare", "cauca", "cesar", "chocó", "choco", "córdoba", "cordoba",
        "cundinamarca", "guainía", "guainia", "guaviare", "huila", "la guajira",
        "magdalena", "meta", "nariño", "narino", "norte de santander",
        "putumayo", "quindío", "quindio", "risaralda", "san andrés y providencia",
        "san andres y providencia", "santander", "sucre", "tolima",
        "valle del cauca", "vaupés", "vaupes", "vichada"
    }

    @staticmethod
    def validate(state: str) -> ValidationResult:
        """
        Valida nombre de departamento.

        Args:
            state: Nombre del departamento

        Returns:
            ValidationResult con el resultado de la validación
        """
        if not state or not state.strip():
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="state",
                message="El departamento es obligatorio"
            )

        state_clean = state.strip().lower()

        if state_clean not in StateValidator.KNOWN_STATES:
            return ValidationResult(
                is_valid=True,  # No bloquea
                severity=ValidationSeverity.WARNING,
                field="state",
                message=f"El departamento '{state.strip()}' no se encuentra en nuestro catálogo. "
                       "Por favor, verifica que esté correctamente escrito."
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            field="state",
            message="Departamento reconocido"
        )


class AddressValidationService:
    """
    Servicio principal de validación de direcciones.

    Implementa HU-03:
    - Valida formato automáticamente (Criterio 1)
    - Genera advertencias claras (Criterio 2)
    - Permite continuar bajo responsabilidad del usuario

    Uso:
        service = AddressValidationService()
        result = service.validate_address(
            street="Calle 10 #20-30",
            city="Bogotá",
            state="Cundinamarca",
            zip_code="110111"
        )

        if result["has_errors"]:
            raise AddressValidationError(...)
        elif result["has_warnings"]:
            # Mostrar advertencias pero permitir continuar
            return {"warnings": result["warnings"]}
    """

    def __init__(self):
        self.postal_validator = PostalCodeValidator()
        self.city_validator = CityValidator()
        self.street_validator = StreetValidator()
        self.state_validator = StateValidator()

    def validate_address(self, street: str, city: str, state: str,
                        zip_code: str, country: str = "Colombia") -> Dict:
        """
        Valida una dirección completa.

        Args:
            street: Dirección de calle
            city: Ciudad
            state: Departamento
            zip_code: Código postal
            country: País (default: Colombia)

        Returns:
            Dict con estructura:
            {
                "is_valid": bool,
                "has_errors": bool,
                "has_warnings": bool,
                "errors": [ValidationResult],
                "warnings": [ValidationResult],
                "info": [ValidationResult]
            }

        Raises:
            AddressValidationError: Si hay errores críticos de validación
        """
        results = []

        # Ejecutar todas las validaciones
        results.append(self.postal_validator.validate(zip_code))
        results.append(self.city_validator.validate(city))
        results.append(self.street_validator.validate(street))
        results.append(self.state_validator.validate(state))

        # Clasificar por severidad
        errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
        warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
        info = [r for r in results if r.severity == ValidationSeverity.INFO]

        return {
            "is_valid": len(errors) == 0,
            "has_errors": len(errors) > 0,
            "has_warnings": len(warnings) > 0,
            "errors": [e.to_dict() for e in errors],
            "warnings": [w.to_dict() for w in warnings],
            "info": [i.to_dict() for i in info],
            "all_results": [r.to_dict() for r in results]
        }

    def validate_or_raise(self, street: str, city: str, state: str,
                         zip_code: str, country: str = "Colombia") -> Dict:
        """
        Valida dirección y lanza excepción si hay errores.

        Args:
            street, city, state, zip_code, country: Componentes de la dirección

        Returns:
            Dict con warnings si existen (pero no hay errores)

        Raises:
            AddressValidationError: Si hay errores de validación
        """
        result = self.validate_address(street, city, state, zip_code, country)

        if result["has_errors"]:
            # Crear mensaje de error detallado
            error_messages = [e["message"] for e in result["errors"]]
            main_error = result["errors"][0]  # Primer error

            raise AddressValidationError(
                message="; ".join(error_messages),
                field=main_error["field"],
                validation_results=[
                    ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.ERROR,
                        field=e["field"],
                        message=e["message"]
                    ) for e in result["errors"]
                ]
            )

        return result


# Singleton instance
_validation_service = AddressValidationService()


def get_validation_service() -> AddressValidationService:
    """Obtener instancia del servicio de validación"""
    return _validation_service
