"""
Tests para HU-05: Protección segura de la información del sistema (Secrets Management)

Criterios de Aceptación:
1. Las credenciales de base de datos y llaves API sensibles no están expuestas
2. El sistema permite rotación de secretos en max 5 minutos sin caídas
3. Todo acceso a información sensible queda registrado en logs de auditoría inmutables

Tests:
- test_no_hardcoded_secrets: Verificar que los secrets no están hardcoded
- test_secrets_loaded_from_env: Verificar que los secrets se cargan de variables de entorno
- test_audit_log_entry_immutable: Verificar que AuditLogEntry es inmutable
- test_get_secret_creates_audit_entry: Verificar que cada acceso genera log de auditoría
- test_rotate_secret_hot_reload: Verificar hot-reload sin restart (<5 min)
- test_reload_all_secrets_performance: Verificar que reload_all_secrets termina en <5 min
- test_audit_log_export_json: Verificar exportación de audit log a JSON
- test_thread_safety_concurrent_access: Verificar thread-safety con accesos concurrentes
- test_integration_auth_service: Verificar integración con auth_service
- test_integration_database_service: Verificar integración con database_service
- test_integration_rabbitmq_service: Verificar integración con rabbitmq service
"""
import pytest
import os
import json
import time
import threading
from datetime import datetime
from services.secrets_manager import (
    SecretsManager,
    AuditLogEntry,
    SecretType,
    get_database_url,
    get_jwt_secret,
    get_rabbitmq_url,
    get_async_pg_url,
    get_secrets_manager
)


class TestHU05SecretsManager:
    """Tests para HU-05: Secrets Management"""

    def setup_method(self):
        """Setup antes de cada test"""
        # Resetear singleton para cada test
        SecretsManager._instance = None
        SecretsManager._lock = threading.RLock()

        # Configurar environment variables de prueba
        os.environ["DATABASE_URL"] = "postgresql://test_user:test_pass@localhost:5432/test_db"
        os.environ["JWT_SECRET"] = "test-jwt-secret-key-123456789"
        os.environ["RABBITMQ_URL"] = "amqp://test:test@localhost:5672/"
        os.environ["ASYNC_PG_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test_db"

    def teardown_method(self):
        """Cleanup después de cada test"""
        # Resetear singleton
        SecretsManager._instance = None

    # ========== CRITERIO 1: Secrets no expuestos ==========

    def test_no_hardcoded_secrets(self):
        """
        HU-05 Criterio 1: Verificar que no hay secrets hardcoded

        Verifica que:
        - Los secrets se cargan de variables de entorno
        - No hay valores hardcoded en el código
        """
        manager = SecretsManager()

        # Verificar que los valores vienen del ambiente
        assert manager.get_secret(SecretType.DATABASE_URL) == os.environ["DATABASE_URL"]
        assert manager.get_secret(SecretType.JWT_SECRET) == os.environ["JWT_SECRET"]
        assert manager.get_secret(SecretType.RABBITMQ_URL) == os.environ["RABBITMQ_URL"]
        assert manager.get_secret(SecretType.ASYNC_PG_URL) == os.environ["ASYNC_PG_URL"]

    def test_secrets_loaded_from_env(self):
        """
        HU-05 Criterio 1: Verificar que secrets se cargan de environment

        Verifica que:
        - Cada secret se lee de os.environ
        - Los valores corresponden exactamente a las variables de entorno
        """
        # Cambiar valores en ambiente
        os.environ["JWT_SECRET"] = "new-test-secret-987"

        # Crear nueva instancia después del cambio
        SecretsManager._instance = None
        manager = SecretsManager()

        # Verificar que lee el nuevo valor
        assert manager.get_secret(SecretType.JWT_SECRET) == "new-test-secret-987"

    # ========== CRITERIO 2: Hot-reload sin caídas ==========

    def test_rotate_secret_hot_reload(self):
        """
        HU-05 Criterio 2: Verificar hot-reload con rotate_secret

        Verifica que:
        - rotate_secret actualiza el secret sin reiniciar
        - El cambio se refleja inmediatamente
        - El proceso toma menos de 5 minutos
        """
        manager = SecretsManager()

        # Valor original
        original = manager.get_secret(SecretType.JWT_SECRET)

        # Medir tiempo de rotación
        start_time = time.time()

        # Rotar secret - NOTA: rotate_secret requiere new_value
        new_value = "rotated-jwt-secret-456"
        success = manager.rotate_secret(SecretType.JWT_SECRET, new_value)

        elapsed_time = time.time() - start_time

        # Verificaciones
        assert success, "rotate_secret debe retornar True"
        assert elapsed_time < 300, f"Rotación tomó {elapsed_time}s, debe ser <300s (5 min)"
        assert manager.get_secret(SecretType.JWT_SECRET) == new_value
        assert manager.get_secret(SecretType.JWT_SECRET) != original

    def test_reload_all_secrets_performance(self):
        """
        HU-05 Criterio 2: Verificar reload_all_secrets completa en <5 min

        Verifica que:
        - reload_all_secrets actualiza todos los secrets
        - El proceso toma menos de 5 minutos (300 segundos)
        - Todos los secrets se actualizan correctamente
        """
        manager = SecretsManager()

        # Cambiar todos los secrets en ambiente
        os.environ["DATABASE_URL"] = "postgresql://new:new@localhost:5432/new_db"
        os.environ["JWT_SECRET"] = "new-jwt-123"
        os.environ["RABBITMQ_URL"] = "amqp://new:new@localhost:5672/"
        os.environ["ASYNC_PG_URL"] = "postgresql+asyncpg://new:new@localhost:5432/new_db"

        # Medir tiempo de reload
        start_time = time.time()
        success = manager.reload_all_secrets()
        elapsed_time = time.time() - start_time

        # Verificaciones de performance
        assert success, "reload_all_secrets debe retornar True"
        assert elapsed_time < 300, f"reload_all_secrets tomó {elapsed_time}s, debe ser <300s (5 min)"
        assert elapsed_time < 1, f"reload_all_secrets debería ser casi instantáneo, tomó {elapsed_time}s"

        # Verificar que todos los secrets se actualizaron
        assert manager.get_secret(SecretType.DATABASE_URL) == "postgresql://new:new@localhost:5432/new_db"
        assert manager.get_secret(SecretType.JWT_SECRET) == "new-jwt-123"
        assert manager.get_secret(SecretType.RABBITMQ_URL) == "amqp://new:new@localhost:5672/"
        assert manager.get_secret(SecretType.ASYNC_PG_URL) == "postgresql+asyncpg://new:new@localhost:5432/new_db"

    # ========== CRITERIO 3: Audit trail inmutable ==========

    def test_audit_log_entry_immutable(self):
        """
        HU-05 Criterio 3: Verificar que AuditLogEntry es inmutable

        Verifica que:
        - No se puede modificar un AuditLogEntry después de creación
        - __setattr__ previene modificaciones
        """
        # AuditLogEntry constructor: secret_name, action, success, client_info
        entry = AuditLogEntry(
            secret_name="JWT_SECRET",
            action="TEST_ACTION",
            success=True,
            client_info="Test client"
        )

        # Intentar modificar debe fallar
        with pytest.raises(AttributeError) as exc_info:
            entry.secret_name = "MODIFIED"

        assert "immutable" in str(exc_info.value).lower()

        # Intentar modificar otros campos
        with pytest.raises(AttributeError):
            entry.action = "MODIFIED"

        with pytest.raises(AttributeError):
            entry.success = False

    def test_get_secret_creates_audit_entry(self):
        """
        HU-05 Criterio 3: Verificar que get_secret genera audit log

        Verifica que:
        - Cada llamada a get_secret crea un AuditLogEntry
        - El audit log contiene timestamp, action, secret_name, success
        - El audit log es persistente entre llamadas
        """
        manager = SecretsManager()

        # Limpiar audit log previo
        manager._audit_log.clear()

        # Acceder a un secret
        _ = manager.get_secret(SecretType.JWT_SECRET)

        # Verificar que se creó un audit entry
        audit_log = manager.get_audit_log()
        assert len(audit_log) == 1

        entry = audit_log[0]
        assert entry["action"] == "GET_SECRET"
        # Campo es "secret_name" no "secret_type"
        assert entry["secret_name"] == "JWT_SECRET"
        assert entry["success"] is True
        assert "timestamp" in entry

        # Acceder a otro secret
        _ = manager.get_secret(SecretType.DATABASE_URL)

        # Verificar que se agregó otro entry
        audit_log = manager.get_audit_log()
        assert len(audit_log) == 2
        # Verificar que DATABASE_URL está en el log (puede no ser el índice 1 si hay cache)
        db_entries = [e for e in audit_log if e["secret_name"] == "DATABASE_URL"]
        assert len(db_entries) >= 1

    def test_audit_log_export_json(self):
        """
        HU-05 Criterio 3: Verificar exportación de audit log a JSON

        Verifica que:
        - export_audit_log_json retorna JSON válido
        - El JSON contiene todos los audit entries
        - Los campos están correctamente serializados
        """
        manager = SecretsManager()
        manager._audit_log.clear()

        # Generar varios accesos
        _ = manager.get_secret(SecretType.JWT_SECRET)
        _ = manager.get_secret(SecretType.DATABASE_URL)
        # rotate_secret requiere new_value
        manager.rotate_secret(SecretType.JWT_SECRET, "new-value-123")

        # Exportar a JSON
        json_str = manager.export_audit_log_json()

        # Verificar que es JSON válido
        audit_data = json.loads(json_str)
        # export_audit_log_json retorna un dict con 'entries', 'total_entries', etc.
        assert isinstance(audit_data, dict)
        assert "entries" in audit_data
        assert "total_entries" in audit_data
        assert audit_data["total_entries"] == 3
        assert len(audit_data["entries"]) == 3

        # Verificar estructura de cada entry
        for entry in audit_data["entries"]:
            assert "timestamp" in entry
            assert "secret_name" in entry
            assert "action" in entry
            assert "success" in entry

    def test_thread_safety_concurrent_access(self):
        """
        HU-05: Verificar thread-safety con accesos concurrentes

        Verifica que:
        - Múltiples threads pueden acceder concurrentemente
        - No hay race conditions
        - Todos los accesos se auditan correctamente
        """
        manager = SecretsManager()
        manager._audit_log.clear()

        results = []
        errors = []

        def access_secret(secret_type, iterations):
            try:
                for _ in range(iterations):
                    value = manager.get_secret(secret_type)
                    results.append((secret_type, value))
            except Exception as e:
                errors.append(e)

        # Crear threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=access_secret, args=(SecretType.JWT_SECRET, 10))
            threads.append(t)
            t.start()

        # Esperar a que terminen
        for t in threads:
            t.join()

        # Verificaciones
        assert len(errors) == 0, f"Se produjeron errores: {errors}"
        assert len(results) == 50  # 5 threads * 10 iterations
        # Verificar audit log
        audit_log = manager.get_audit_log()
        assert len(audit_log) == 50

    # ========== TESTS DE INTEGRACIÓN ==========

    def test_integration_auth_service(self):
        """
        HU-05: Verificar integración con auth_service

        Verifica que:
        - auth_service puede obtener JWT_SECRET
        - El acceso queda registrado en audit log
        """
        # Usar get_secrets_manager() para obtener la instancia singleton
        manager = get_secrets_manager()
        manager._audit_log.clear()

        # Simular acceso desde auth_service
        jwt_secret = get_jwt_secret()

        # Verificaciones
        assert jwt_secret is not None
        assert len(jwt_secret) > 0
        assert jwt_secret == os.environ["JWT_SECRET"]

        # Verificar audit log
        audit_log = manager.get_audit_log()
        assert len(audit_log) >= 1
        # Debe haber al menos un acceso a JWT_SECRET
        jwt_accesses = [e for e in audit_log if e["secret_name"] == "JWT_SECRET"]
        assert len(jwt_accesses) >= 1

    def test_integration_database_service(self):
        """
        HU-05: Verificar integración con database_service

        Verifica que:
        - database_service puede obtener DATABASE_URL y ASYNC_PG_URL
        - Los accesos quedan registrados en audit log
        """
        # Usar get_secrets_manager() para obtener la instancia singleton
        manager = get_secrets_manager()
        manager._audit_log.clear()

        # Simular accesos desde database_service
        db_url = get_database_url()
        async_pg_url = get_async_pg_url()

        # Verificaciones
        assert db_url is not None
        assert async_pg_url is not None
        assert db_url == os.environ["DATABASE_URL"]
        assert async_pg_url == os.environ["ASYNC_PG_URL"]

        # Verificar audit log
        audit_log = manager.get_audit_log()
        assert len(audit_log) >= 2
        # Debe haber accesos a DATABASE_URL y ASYNC_PG_URL
        db_accesses = [e for e in audit_log if e["secret_name"] in ["DATABASE_URL", "ASYNC_PG_URL"]]
        assert len(db_accesses) >= 2

    def test_integration_rabbitmq_service(self):
        """
        HU-05: Verificar integración con rabbitmq service

        Verifica que:
        - rabbitmq service puede obtener RABBITMQ_URL
        - El acceso queda registrado en audit log
        """
        # Usar get_secrets_manager() para obtener la instancia singleton
        manager = get_secrets_manager()
        manager._audit_log.clear()

        # Simular acceso desde rabbitmq service
        rabbitmq_url = get_rabbitmq_url()

        # Verificaciones
        assert rabbitmq_url is not None
        assert len(rabbitmq_url) > 0
        assert rabbitmq_url == os.environ["RABBITMQ_URL"]

        # Verificar audit log
        audit_log = manager.get_audit_log()
        assert len(audit_log) >= 1
        # Debe haber accesos a RABBITMQ_URL
        rabbitmq_accesses = [e for e in audit_log if e["secret_name"] == "RABBITMQ_URL"]
        assert len(rabbitmq_accesses) >= 1

    # ========== TESTS ADICIONALES ==========

    def test_singleton_pattern(self):
        """Verificar que get_secrets_manager devuelve singleton"""
        # Usar get_secrets_manager() en lugar de constructor
        manager1 = get_secrets_manager()
        manager2 = get_secrets_manager()

        assert manager1 is manager2, "get_secrets_manager() debe devolver siempre la misma instancia"

    def test_get_secret_missing_env_var(self):
        """Verificar comportamiento con variable de entorno faltante"""
        # Eliminar una variable
        if "JWT_SECRET" in os.environ:
            del os.environ["JWT_SECRET"]

        # Resetear singleton
        SecretsManager._instance = None

        manager = SecretsManager()

        # Verificar que retorna valor por defecto (el implementado en secrets_manager)
        jwt_secret = manager.get_secret(SecretType.JWT_SECRET)
        # El fallback real es "development-secret-key-DO-NOT-USE-IN-PRODUCTION"
        assert jwt_secret == "development-secret-key-DO-NOT-USE-IN-PRODUCTION"

    def test_rotate_secret_audit_trail(self):
        """Verificar que rotate_secret genera audit entries"""
        manager = SecretsManager()
        manager._audit_log.clear()

        # Rotar secret - rotate_secret requiere new_value
        os.environ["JWT_SECRET"] = "new-rotated-value"
        manager.rotate_secret(SecretType.JWT_SECRET, "new-rotated-value")

        # Verificar audit log
        audit_log = manager.get_audit_log()
        assert len(audit_log) >= 1

        # Verificar que hay un entry de ROTATE_SECRET
        rotate_entries = [e for e in audit_log if e["action"] == "ROTATE_SECRET"]
        assert len(rotate_entries) >= 1
        assert rotate_entries[0]["secret_name"] == "JWT_SECRET"
        assert rotate_entries[0]["success"] is True
