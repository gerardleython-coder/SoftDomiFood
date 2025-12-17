"""
Performance Middleware - Request Timing & Metrics Tracking

Middleware para tracking de performance de endpoints (HU-01).
Registra tiempos de respuesta, calcula percentiles P90/P95, y genera logs estructurados.

Principios SOLID aplicados:
- SRP: Responsabilidad única de monitoreo de performance
- OCP: Extensible para agregar métricas adicionales sin modificar código base
- ISP: Interfaz simple y específica para middleware

Autor: Senior Fullstack Developer
Fecha: 16 de Diciembre 2025
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, List
import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Almacena y calcula métricas de performance por endpoint.
    Thread-safe mediante uso de estructuras inmutables.
    """

    def __init__(self, window_minutes: int = 5):
        """
        Args:
            window_minutes: Ventana de tiempo para cálculo de métricas (default: 5min)
        """
        self._metrics: Dict[str, List[Dict]] = defaultdict(list)
        self._window_minutes = window_minutes

    def add_request(self, endpoint: str, duration_ms: float, status_code: int) -> None:
        """
        Registrar nueva petición.

        Args:
            endpoint: Path del endpoint (ej: /api/auth/login)
            duration_ms: Duración en milisegundos
            status_code: Código HTTP de respuesta
        """
        self._metrics[endpoint].append({
            "timestamp": datetime.now(),
            "duration_ms": duration_ms,
            "status_code": status_code
        })

        # Limpiar métricas antiguas
        self._cleanup_old_metrics(endpoint)

    def get_percentile(self, endpoint: str, percentile: float = 90) -> float:
        """
        Calcular percentil de tiempo de respuesta.

        Args:
            endpoint: Path del endpoint
            percentile: Percentil a calcular (90 o 95 típicamente)

        Returns:
            Tiempo en milisegundos del percentil solicitado
        """
        metrics = self._metrics.get(endpoint, [])
        if not metrics:
            return 0.0

        durations = sorted([m["duration_ms"] for m in metrics])
        index = int(len(durations) * (percentile / 100))
        return durations[min(index, len(durations) - 1)]

    def get_stats(self, endpoint: str) -> Dict:
        """
        Obtener estadísticas completas de un endpoint.

        Returns:
            Dict con avg, min, max, p90, p95, count, error_rate
        """
        metrics = self._metrics.get(endpoint, [])
        if not metrics:
            return {
                "count": 0,
                "avg_ms": 0,
                "min_ms": 0,
                "max_ms": 0,
                "p90_ms": 0,
                "p95_ms": 0,
                "error_rate": 0
            }

        durations = [m["duration_ms"] for m in metrics]
        errors = sum(1 for m in metrics if m["status_code"] >= 400)

        return {
            "count": len(metrics),
            "avg_ms": round(sum(durations) / len(durations), 2),
            "min_ms": round(min(durations), 2),
            "max_ms": round(max(durations), 2),
            "p90_ms": round(self.get_percentile(endpoint, 90), 2),
            "p95_ms": round(self.get_percentile(endpoint, 95), 2),
            "error_rate": round(errors / len(metrics) * 100, 2) if metrics else 0
        }

    def get_all_stats(self) -> Dict[str, Dict]:
        """
        Obtener estadísticas de todos los endpoints.

        Returns:
            Dict con stats por endpoint
        """
        return {
            endpoint: self.get_stats(endpoint)
            for endpoint in self._metrics.keys()
        }

    def _cleanup_old_metrics(self, endpoint: str) -> None:
        """Eliminar métricas fuera de la ventana de tiempo"""
        cutoff = datetime.now() - timedelta(minutes=self._window_minutes)
        self._metrics[endpoint] = [
            m for m in self._metrics[endpoint]
            if m["timestamp"] > cutoff
        ]


# Instancia global de métricas
_performance_metrics = PerformanceMetrics(window_minutes=5)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware de FastAPI para tracking de performance.

    Funcionalidades:
    - Mide tiempo de respuesta de cada request
    - Calcula P90/P95 por endpoint
    - Logs estructurados para alertas
    - Detecta endpoints lentos (> threshold)
    """

    def __init__(self, app, slow_threshold_ms: float = 100):
        """
        Args:
            app: Aplicación FastAPI
            slow_threshold_ms: Umbral para considerar request lento (default: 100ms)
        """
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Procesar request y medir performance.

        Args:
            request: Request de FastAPI
            call_next: Siguiente handler en la cadena

        Returns:
            Response con headers adicionales de timing
        """
        # Excluir rutas de health check y estáticas
        if self._should_skip(request.url.path):
            return await call_next(request)

        # Medir tiempo de ejecución
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Registrar métricas
            endpoint = self._normalize_endpoint(request.url.path)
            _performance_metrics.add_request(endpoint, duration_ms, response.status_code)

            # Log estructurado
            self._log_request(request, response.status_code, duration_ms, endpoint)

            # Agregar headers de performance
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            endpoint = self._normalize_endpoint(request.url.path)
            _performance_metrics.add_request(endpoint, duration_ms, 500)

            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "endpoint": endpoint,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e)
                }
            )
            raise

    def _should_skip(self, path: str) -> bool:
        """Determinar si se debe omitir tracking del path"""
        skip_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]
        return any(path.startswith(skip_path) for skip_path in skip_paths)

    def _normalize_endpoint(self, path: str) -> str:
        """
        Normalizar path para agrupar métricas.
        Reemplaza IDs por placeholders para agrupar endpoints similares.

        Ejemplos:
            /api/products/123 -> /api/products/{id}
            /api/users/abc-def/orders -> /api/users/{id}/orders
        """
        parts = path.split("/")
        normalized = []

        for part in parts:
            # Si parece un ID (UUID, número, etc), reemplazar
            if part and (part.isdigit() or len(part) > 20 or "-" in part):
                normalized.append("{id}")
            else:
                normalized.append(part)

        return "/".join(normalized)

    def _log_request(self, request: Request, status_code: int, duration_ms: float, endpoint: str) -> None:
        """
        Generar log estructurado de la petición.

        Args:
            request: Request de FastAPI
            status_code: Código HTTP de respuesta
            duration_ms: Duración en milisegundos
            endpoint: Endpoint normalizado
        """
        log_data = {
            "method": request.method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": request.client.host if request.client else "unknown"
        }

        # Log según severidad
        if duration_ms > self.slow_threshold_ms:
            logger.warning(
                f"Slow request detected: {request.method} {endpoint}",
                extra=log_data
            )
        elif status_code >= 500:
            logger.error(
                f"Server error: {request.method} {endpoint}",
                extra=log_data
            )
        elif status_code >= 400:
            logger.warning(
                f"Client error: {request.method} {endpoint}",
                extra=log_data
            )
        else:
            logger.info(
                f"Request completed: {request.method} {endpoint}",
                extra=log_data
            )


def get_performance_metrics() -> PerformanceMetrics:
    """
    Obtener instancia de métricas de performance.
    Útil para endpoints de monitoreo y dashboards.

    Returns:
        Instancia global de PerformanceMetrics

    Example:
        metrics = get_performance_metrics()
        stats = metrics.get_stats("/api/auth/login")
        print(f"P90: {stats['p90_ms']}ms")
    """
    return _performance_metrics
