"""
Cache Service - In-Memory Cache with TTL Management

Implementa patrón Singleton para cache en memoria con gestión de TTL (Time To Live).
Diseñado para optimizar performance de operaciones frecuentes (HU-01).

Principios SOLID aplicados:
- SRP: Responsabilidad única de gestión de cache
- OCP: Abierto para extensión (fácil migrar a Redis si se necesita)
- DIP: Dependencia de abstracciones (CacheInterface)

Autor: Senior Fullstack Developer
Fecha: 16 de Diciembre 2025
"""

from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import threading
from abc import ABC, abstractmethod


class CacheInterface(ABC):
    """
    Abstracción de cache para cumplir DIP (Dependency Inversion Principle).
    Permite migrar a Redis u otros backends sin cambiar código cliente.
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Obtener valor de cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        """Establecer valor en cache con TTL"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Eliminar clave específica"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Limpiar todo el cache"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        pass


class InMemoryCache(CacheInterface):
    """
    Implementación de cache en memoria con TTL.
    Thread-safe usando locks para entornos con múltiples workers.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern para garantizar instancia única"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializar estructuras de cache"""
        if self._initialized:
            return

        self._cache: Dict[str, Any] = {}
        self._expiry: Dict[str, datetime] = {}
        self._hits = 0
        self._misses = 0
        self._lock = threading.Lock()
        self._initialized = True

    def get(self, key: str) -> Optional[Any]:
        """
        Obtener valor de cache si existe y no ha expirado.

        Args:
            key: Clave de cache

        Returns:
            Valor cacheado o None si no existe/expiró
        """
        with self._lock:
            # Verificar si la clave existe
            if key not in self._cache:
                self._misses += 1
                return None

            # Verificar si ha expirado
            if self._is_expired(key):
                self._delete_internal(key)
                self._misses += 1
                return None

            self._hits += 1
            return self._cache[key]

    def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        """
        Establecer valor en cache con TTL.

        Args:
            key: Clave de cache
            value: Valor a cachear
            ttl_seconds: Tiempo de vida en segundos (default: 60s)
        """
        with self._lock:
            self._cache[key] = value
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)

    def delete(self, key: str) -> None:
        """
        Eliminar clave específica del cache.

        Args:
            key: Clave a eliminar
        """
        with self._lock:
            self._delete_internal(key)

    def clear(self) -> None:
        """Limpiar todo el cache y resetear estadísticas"""
        with self._lock:
            self._cache.clear()
            self._expiry.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del cache.

        Returns:
            Dict con hits, misses, hit_rate, size
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "size": len(self._cache),
                "keys": list(self._cache.keys())
            }

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidar claves que coincidan con un patrón.
        Útil para invalidar grupos (ej: "user:*", "product:*")

        Args:
            pattern: Patrón de búsqueda (soporta wildcard *)

        Returns:
            Número de claves eliminadas
        """
        with self._lock:
            keys_to_delete = []
            pattern_prefix = pattern.replace("*", "")

            for key in list(self._cache.keys()):
                if key.startswith(pattern_prefix):
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                self._delete_internal(key)

            return len(keys_to_delete)

    def cleanup_expired(self) -> int:
        """
        Limpiar entradas expiradas (útil para background task).

        Returns:
            Número de claves eliminadas
        """
        with self._lock:
            expired_keys = [
                key for key in list(self._cache.keys())
                if self._is_expired(key)
            ]

            for key in expired_keys:
                self._delete_internal(key)

            return len(expired_keys)

    # Métodos internos (no thread-safe, usar con lock)

    def _is_expired(self, key: str) -> bool:
        """Verificar si una clave ha expirado"""
        if key not in self._expiry:
            return True
        return datetime.now() > self._expiry[key]

    def _delete_internal(self, key: str) -> None:
        """Eliminar clave sin lock (uso interno)"""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)


# Factory function para obtener instancia de cache
def get_cache() -> CacheInterface:
    """
    Obtener instancia del cache (Singleton).

    Returns:
        Instancia de InMemoryCache

    Example:
        cache = get_cache()
        cache.set("user:123", {"name": "John"}, ttl_seconds=120)
        user = cache.get("user:123")
    """
    return InMemoryCache()


# Utilidades para cache keys estandarizados
class CacheKeys:
    """Generadores de cache keys estandarizados"""

    @staticmethod
    def user_by_email(email: str) -> str:
        """Key para usuario por email"""
        return f"user:email:{email}"

    @staticmethod
    def user_by_id(user_id: str) -> str:
        """Key para usuario por ID"""
        return f"user:id:{user_id}"

    @staticmethod
    def product_by_id(product_id: str) -> str:
        """Key para producto por ID"""
        return f"product:id:{product_id}"

    @staticmethod
    def user_addresses(user_id: str) -> str:
        """Key para direcciones de usuario"""
        return f"addresses:user:{user_id}"

    @staticmethod
    def products_all() -> str:
        """Key para lista completa de productos"""
        return "products:all"
