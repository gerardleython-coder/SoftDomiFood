from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from routers import auth, products, orders, admin, addresses, reviews, favorites
from init_db import init_database, check_tables_exist, create_admin_user
from services.rabbitmq import get_channel, close_connection
from services.database_service import validate_coupon_for_user

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Inicializando base de datos...")
    try:
        tables_exist = await check_tables_exist()
        if not tables_exist:
            print("📊 Creando tablas en la base de datos...")
            success = await init_database()
            if success:
                print("✅ Base de datos inicializada correctamente")
            else:
                print("⚠️  Advertencia: No se pudieron crear todas las tablas")
                print("🔄 Intentando forzar creación de tablas...")
                await init_database()
        else:
            print("✅ Las tablas ya existen en la base de datos")
            await create_admin_user()
    except Exception as e:
        print(f"⚠️  Error al verificar/inicializar base de datos: {e}")
        import traceback
        traceback.print_exc()
        print("   Intentando forzar creación de tablas...")
        try:
            await init_database()
        except Exception as e2:
            print(f"   ❌ Error al forzar creación: {e2}")
            print("   Continuando de todas formas...")

    # RabbitMQ
    print("🐰 Inicializando conexión RabbitMQ...")
    try:
        await get_channel()
        print("✅ Conexión RabbitMQ inicializada correctamente")
    except Exception as e:
        print(f"⚠️  Error al inicializar RabbitMQ: {e}")
        print("   La aplicación continuará, pero los mensajes no se publicarán")
        import traceback
        traceback.print_exc()

    # ✅ Dispatcher de pedidos programados (SCHEDULED -> PENDING -> publish)
    print("⏱️  Iniciando dispatcher de pedidos programados...")
    scheduled_task = None
    try:
        from services.scheduled_dispatcher import start_scheduled_dispatcher
        scheduled_task = start_scheduled_dispatcher()
        print("✅ Dispatcher de pedidos programados iniciado")
    except Exception as e:
        print(f"⚠️  No se pudo iniciar dispatcher: {e}")

    yield

    # Shutdown
    print("🛑 Cerrando conexiones...")

    # ✅ Detener dispatcher
    try:
        if scheduled_task:
            from services.scheduled_dispatcher import stop_scheduled_dispatcher
            await stop_scheduled_dispatcher(scheduled_task)
    except Exception as e:
        print(f"⚠️  Error deteniendo dispatcher: {e}")

    # RabbitMQ shutdown
    try:
        await close_connection()
    except Exception as e:
        print(f"⚠️  Error al cerrar conexión RabbitMQ: {e}")

app = FastAPI(
    title="SoftDomiFood API",
    description="API Producer para sistema de pedidos",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================
# MIDDLEWARE - Performance Tracking (HU-01)
# ============================================================
from middleware.performance import PerformanceMiddleware

# Agregar middleware de performance (ANTES de CORS para medir todo)
app.add_middleware(PerformanceMiddleware, slow_threshold_ms=100)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5000",
        "http://127.0.0.1:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(addresses.router, prefix="/api", tags=["addresses"])
app.include_router(reviews.router, prefix="/api", tags=["reviews"])
app.include_router(favorites.router, prefix="/api", tags=["favorites"])

# Cupones
from fastapi import APIRouter, Depends
from routers.auth import get_current_user

coupons_router = APIRouter()

@coupons_router.post("/validate")
async def validate_coupon(code: dict, current_user: dict = Depends(get_current_user)):
    coupon_code = code.get("code")
    if not coupon_code:
        raise HTTPException(status_code=400, detail="Falta código de cupón")
    result = await validate_coupon_for_user(coupon_code, current_user.get("userId"))
    return result

app.include_router(coupons_router, prefix="/api/coupons", tags=["coupons"])

@app.get("/")
async def root():
    return {
        "message": "SoftDomiFood API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "message": "SoftDomiFood API is running",
        "service": "producer"
    }

@app.get("/api/metrics/performance")
async def get_performance_metrics():
    """
    Endpoint para obtener métricas de performance del sistema (HU-01).
    Retorna estadísticas de tiempos de respuesta por endpoint.
    """
    from middleware.performance import get_performance_metrics
    metrics = get_performance_metrics()
    return {
        "status": "ok",
        "metrics": metrics.get_all_stats()
    }

@app.get("/api/metrics/cache")
async def get_cache_metrics():
    """
    Endpoint para obtener estadísticas del cache en memoria (HU-01).
    Retorna hits, misses, hit_rate y tamaño del cache.
    """
    from services.cache_service import get_cache
    cache = get_cache()
    return {
        "status": "ok",
        "cache": cache.get_stats()
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    uvicorn.run(app, host=host, port=port)
