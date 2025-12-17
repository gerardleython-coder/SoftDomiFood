import aio_pika
import json
import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from services.secrets_manager import get_rabbitmq_url  # HU-05

QUEUE_NAME = "order_queue"

def _get_rabbitmq_url() -> str:
    """Obtener RABBITMQ_URL con auditoría (HU-05)"""
    return get_rabbitmq_url()

# Variables globales para conexión persistente
_connection: Optional[aio_pika.RobustConnection] = None
_channel: Optional[aio_pika.RobustChannel] = None

async def get_connection() -> aio_pika.RobustConnection:
    """Obtener o crear conexión persistente a RabbitMQ"""
    global _connection
    if _connection is None or _connection.is_closed:
        try:
            rabbitmq_url = _get_rabbitmq_url()
            _connection = await aio_pika.connect_robust(rabbitmq_url)
            # Ocultar contraseña en logs
            safe_url = rabbitmq_url.split('@')[0].split(':')[0] + '://****@' + '@'.join(rabbitmq_url.split('@')[1:]) if '@' in rabbitmq_url else rabbitmq_url
            print(f"[OK] Conexión RabbitMQ establecida: {safe_url}")
        except Exception as e:
            print(f"[ERROR] Error conectando a RabbitMQ: {e}")
            _connection = None
            raise
    return _connection

async def get_channel() -> aio_pika.RobustChannel:
    """Obtener o crear canal persistente"""
    global _channel
    connection = await get_connection()
    if _channel is None or _channel.is_closed:
        _channel = await connection.channel()
        # Declarar cola al crear el canal
        await _channel.declare_queue(QUEUE_NAME, durable=True)
        print(f"[OK] Canal RabbitMQ creado y cola '{QUEUE_NAME}' declarada")
    return _channel

async def close_connection():
    """Cerrar conexión RabbitMQ (útil para shutdown)"""
    global _connection, _channel
    if _channel and not _channel.is_closed:
        await _channel.close()
        _channel = None
    if _connection and not _connection.is_closed:
        await _connection.close()
        _connection = None
    print("[RABBITMQ] Conexión cerrada")

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

async def publish_order(order_data: Dict[str, Any]):
    """
    Publicar mensaje de pedido a la cola order_queue
    El formato debe ser compatible con el worker que espera:
    {
        "orderId": str,
        "userId": str,
        "addressId": str,
        "items": [...],
        "total": float,
        "notes": str (opcional)
    }
    """
    try:
        channel = await get_channel()

        # Formatear mensaje para el worker
        # Asegurar que los items tengan el formato correcto (productId, quantity, price)
        items = []
        for item in order_data.get("items", []):
            items.append({
                "productId": str(item.get("productId", item.get("product_id", ""))),
                "quantity": int(item.get("quantity", 0)),
                "price": float(item.get("price", 0))
            })

        message = {
            "orderId": str(order_data.get("id", "")),
            "userId": str(order_data.get("userId", "")),
            "addressId": str(order_data.get("addressId", "")),
            "items": items,
            "total": float(order_data.get("total", 0)),
            "notes": order_data.get("notes")
        }

        # Publicar mensaje (convertir datetime y UUID a formatos serializables)
        message_body = json.dumps(message, default=json_serial)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=QUEUE_NAME
        )

        print(f"[OK] Mensaje publicado a {QUEUE_NAME}: {message.get('orderId')}")
        return True
    except aio_pika.exceptions.ConnectionClosed:
        # Reconectar si la conexión se cerró
        print("[WARNING] Conexión RabbitMQ cerrada, reconectando...")
        global _connection, _channel
        _connection = None
        _channel = None
        # Reintentar una vez
        channel = await get_channel()
        message_body = json.dumps(message, default=json_serial)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=QUEUE_NAME
        )
        print(f"[OK] Mensaje publicado a {QUEUE_NAME} (después de reconexión): {message.get('orderId')}")
        return True
    except Exception as e:
        print(f"[ERROR] Error publicando mensaje: {e}")
        import traceback
        traceback.print_exc()
        raise
