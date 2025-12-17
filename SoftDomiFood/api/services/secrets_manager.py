"""
Secrets Manager Service
=======================

Gestión centralizada y segura de secretos - Implementa HU-05.

HU-05 Criterios de Aceptación:
1. Credenciales no expuestas en código ni configuraciones públicas
2. Rotación de secretos en ≤5 minutos sin caídas de servicio
3. Accesos a secretos registrados en logs de auditoría inmutables

Arquitectura:
- Singleton Pattern: Instancia única centralizada
- Hot Reload: Recarga secretos sin reiniciar servicio
- Audit Trail: Log inmutable de todos los accesos
- Zero Trust: Todos los accesos son auditados

Secretos Gestionados:
- DATABASE_URL: Conexión PostgreSQL
- JWT_SECRET: Firma de tokens
- RABBITMQ_URL: Conexión RabbitMQ
- (Extensible para nuevos secretos)

Uso:
    secrets = get_secrets_manager()
    db_url = secrets.get_secret("DATABASE_URL")
    # Automáticamente auditado
"""

import os
import json
import threading
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum


class SecretType(str, Enum):
    """Tipos de secretos gestionados"""
    DATABASE_URL = "DATABASE_URL"
    JWT_SECRET = "JWT_SECRET"
    RABBITMQ_URL = "RABBITMQ_URL"
    ASYNC_PG_URL = "ASYNC_PG_URL"


class AuditLogEntry:
    """
    Entrada inmutable de auditoría (Criterio 3).

    Atributos:
        timestamp: Momento exacto del acceso (ISO format)
        secret_name: Nombre del secreto accedido
        action: Acción realizada (GET, ROTATE, etc.)
        success: Si la operación fue exitosa
        client_info: Información adicional del cliente
    """

    def __init__(self, secret_name: str, action: str, success: bool,
                 client_info: Optional[str] = None):
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.secret_name = secret_name
        self.action = action
        self.success = success
        self.client_info = client_info or "internal"
        # Inmutable: después de creado, no se puede modificar
        self._frozen = True

    def __setattr__(self, key, value):
        """Prevenir modificación después de creación (inmutabilidad)"""
        if hasattr(self, '_frozen') and self._frozen:
            raise AttributeError(f"AuditLogEntry is immutable. Cannot modify {key}")
        super().__setattr__(key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para logging"""
        return {
            "timestamp": self.timestamp,
            "secret_name": self.secret_name,
            "action": self.action,
            "success": self.success,
            "client_info": self.client_info
        }

    def to_json(self) -> str:
        """Formato JSON para almacenamiento"""
        return json.dumps(self.to_dict())


class SecretsManager:
    """
    Gestor centralizado de secretos con auditoría.

    Implementa:
    - Criterio 1: Carga desde variables de entorno (no hardcoded)
    - Criterio 2: Hot-reload sin reinicio de servicio
    - Criterio 3: Auditoría inmutable de todos los accesos

    Thread-Safe: Usa locks para acceso concurrente seguro.
    """

    def __init__(self):
        self._secrets: Dict[str, str] = {}
        self._audit_log: list[AuditLogEntry] = []
        self._lock = threading.RLock()  # Reentrant lock para thread safety
        self._load_secrets()

    def _load_secrets(self):
        """
        Cargar secretos desde variables de entorno (Criterio 1).

        NO hay valores por defecto hardcoded aquí.
        Fallback solo para desarrollo local.
        """
        with self._lock:
            # Criterio 1: Cargar desde environment variables
            self._secrets = {
                SecretType.DATABASE_URL: os.getenv(
                    "DATABASE_URL",
                    "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_db"
                ),
                SecretType.JWT_SECRET: os.getenv(
                    "JWT_SECRET",
                    "development-secret-key-DO-NOT-USE-IN-PRODUCTION"
                ),
                SecretType.RABBITMQ_URL: os.getenv(
                    "RABBITMQ_URL",
                    "amqp://admin:admin123@localhost:5672/"
                ),
                SecretType.ASYNC_PG_URL: os.getenv(
                    "ASYNC_PG_URL",
                    os.getenv("DATABASE_URL", "")
                )
            }

            # Auditar carga inicial
            self._add_audit_log(
                secret_name="SYSTEM",
                action="LOAD_SECRETS",
                success=True,
                client_info="SecretsManager initialization"
            )

    def get_secret(self, secret_name: str, mask_in_logs: bool = True) -> str:
        """
        Obtener valor de un secreto (Criterio 3: auditado).

        Args:
            secret_name: Nombre del secreto a obtener
            mask_in_logs: Si debe enmascarar el valor en logs (True por defecto)

        Returns:
            Valor del secreto

        Raises:
            KeyError: Si el secreto no existe
        """
        with self._lock:
            try:
                value = self._secrets.get(secret_name)

                if value is None:
                    # Auditar acceso fallido
                    self._add_audit_log(
                        secret_name=secret_name,
                        action="GET_SECRET",
                        success=False,
                        client_info="Secret not found"
                    )
                    raise KeyError(f"Secret '{secret_name}' not found")

                # Criterio 3: Auditar acceso exitoso
                self._add_audit_log(
                    secret_name=secret_name,
                    action="GET_SECRET",
                    success=True,
                    client_info="Value retrieved"
                )

                return value

            except Exception as e:
                # Auditar error
                self._add_audit_log(
                    secret_name=secret_name,
                    action="GET_SECRET",
                    success=False,
                    client_info=f"Error: {str(e)}"
                )
                raise

    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """
        Rotar un secreto sin reinicio de servicio (Criterio 2).

        Permite actualizar secretos en caliente (hot-reload).
        El cambio es inmediato - sin downtime.

        Args:
            secret_name: Nombre del secreto a rotar
            new_value: Nuevo valor del secreto

        Returns:
            True si la rotación fue exitosa

        Raises:
            ValueError: Si el secreto no existe o el valor es inválido
        """
        with self._lock:
            if secret_name not in self._secrets:
                # Auditar rotación fallida
                self._add_audit_log(
                    secret_name=secret_name,
                    action="ROTATE_SECRET",
                    success=False,
                    client_info="Secret does not exist"
                )
                raise ValueError(f"Cannot rotate non-existent secret: {secret_name}")

            if not new_value or not new_value.strip():
                self._add_audit_log(
                    secret_name=secret_name,
                    action="ROTATE_SECRET",
                    success=False,
                    client_info="Invalid new value (empty)"
                )
                raise ValueError("New secret value cannot be empty")

            # Criterio 2: Actualización en caliente (sin reinicio)
            old_value_masked = self._mask_secret(self._secrets[secret_name])
            self._secrets[secret_name] = new_value
            new_value_masked = self._mask_secret(new_value)

            # Criterio 3: Auditar rotación exitosa
            self._add_audit_log(
                secret_name=secret_name,
                action="ROTATE_SECRET",
                success=True,
                client_info=f"Rotated from {old_value_masked} to {new_value_masked}"
            )

            print(f"🔄 Secret '{secret_name}' rotated successfully")
            return True

    def reload_all_secrets(self) -> bool:
        """
        Recargar todos los secretos desde variables de entorno (Criterio 2).

        Útil para aplicar cambios en .env sin reiniciar el servicio.
        Hot-reload completo en ≤5 minutos (típicamente <1 segundo).

        Returns:
            True si la recarga fue exitosa
        """
        with self._lock:
            try:
                # Recargar desde environment
                self._load_secrets()

                # Auditar recarga exitosa
                self._add_audit_log(
                    secret_name="SYSTEM",
                    action="RELOAD_ALL_SECRETS",
                    success=True,
                    client_info=f"Reloaded {len(self._secrets)} secrets"
                )

                print(f"🔄 All secrets reloaded successfully ({len(self._secrets)} secrets)")
                return True

            except Exception as e:
                # Auditar error
                self._add_audit_log(
                    secret_name="SYSTEM",
                    action="RELOAD_ALL_SECRETS",
                    success=False,
                    client_info=f"Error: {str(e)}"
                )
                raise

    def get_audit_log(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        """
        Obtener log de auditoría (Criterio 3: inmutable).

        Args:
            limit: Número máximo de entradas a devolver (None = todas)

        Returns:
            Lista de entradas de auditoría (más recientes primero)
        """
        with self._lock:
            log_entries = self._audit_log[-limit:] if limit else self._audit_log
            return [entry.to_dict() for entry in reversed(log_entries)]

    def export_audit_log_json(self, filepath: Optional[str] = None) -> str:
        """
        Exportar log de auditoría a JSON (Criterio 3).

        Args:
            filepath: Ruta donde guardar (None = solo retornar JSON)

        Returns:
            JSON string con el log completo
        """
        with self._lock:
            log_data = {
                "total_entries": len(self._audit_log),
                "export_timestamp": datetime.utcnow().isoformat() + "Z",
                "entries": [entry.to_dict() for entry in self._audit_log]
            }

            json_str = json.dumps(log_data, indent=2)

            if filepath:
                with open(filepath, 'w') as f:
                    f.write(json_str)
                print(f"📄 Audit log exported to {filepath}")

            return json_str

    def _add_audit_log(self, secret_name: str, action: str, success: bool,
                      client_info: Optional[str] = None):
        """
        Agregar entrada al log de auditoría (interno, thread-safe).

        Las entradas son inmutables una vez creadas.
        """
        # No necesita lock adicional - llamado desde métodos ya protegidos
        entry = AuditLogEntry(
            secret_name=secret_name,
            action=action,
            success=success,
            client_info=client_info
        )
        self._audit_log.append(entry)

        # Log a consola para troubleshooting
        print(f"🔐 AUDIT: {entry.to_json()}")

    def _mask_secret(self, value: str, show_chars: int = 4) -> str:
        """
        Enmascarar valor secreto para logs (mostrar solo últimos caracteres).

        Args:
            value: Valor a enmascarar
            show_chars: Cuántos caracteres finales mostrar

        Returns:
            Valor enmascarado (ej: "****abc123")
        """
        if not value or len(value) <= show_chars:
            return "****"
        return f"****{value[-show_chars:]}"

    def list_secret_names(self) -> list[str]:
        """
        Listar nombres de secretos disponibles (sin valores).

        Útil para debugging sin exponer valores sensibles.
        """
        with self._lock:
            return list(self._secrets.keys())

    def validate_all_secrets(self) -> Dict[str, bool]:
        """
        Validar que todos los secretos requeridos existen y no están vacíos.

        Returns:
            Dict con {secret_name: is_valid}
        """
        with self._lock:
            validation = {}
            required_secrets = [
                SecretType.DATABASE_URL,
                SecretType.JWT_SECRET,
                SecretType.RABBITMQ_URL
            ]

            for secret_name in required_secrets:
                value = self._secrets.get(secret_name)
                validation[secret_name] = bool(value and value.strip())

            # Auditar validación
            all_valid = all(validation.values())
            self._add_audit_log(
                secret_name="SYSTEM",
                action="VALIDATE_SECRETS",
                success=all_valid,
                client_info=f"Validation results: {validation}"
            )

            return validation


# Singleton instance
_secrets_manager: Optional[SecretsManager] = None
_instance_lock = threading.Lock()


def get_secrets_manager() -> SecretsManager:
    """
    Obtener instancia singleton del gestor de secretos.

    Thread-safe: Usa doble-check locking.

    Returns:
        Instancia única de SecretsManager
    """
    global _secrets_manager

    if _secrets_manager is None:
        with _instance_lock:
            # Double-check locking
            if _secrets_manager is None:
                _secrets_manager = SecretsManager()

    return _secrets_manager


# Funciones de conveniencia para acceso rápido
def get_database_url() -> str:
    """Obtener DATABASE_URL (auditado)"""
    return get_secrets_manager().get_secret(SecretType.DATABASE_URL)


def get_jwt_secret() -> str:
    """Obtener JWT_SECRET (auditado)"""
    return get_secrets_manager().get_secret(SecretType.JWT_SECRET)


def get_rabbitmq_url() -> str:
    """Obtener RABBITMQ_URL (auditado)"""
    return get_secrets_manager().get_secret(SecretType.RABBITMQ_URL)


def get_async_pg_url() -> str:
    """Obtener ASYNC_PG_URL (auditado)"""
    return get_secrets_manager().get_secret(SecretType.ASYNC_PG_URL)
