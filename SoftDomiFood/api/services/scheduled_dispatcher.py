# services/scheduled_dispatcher.py
import asyncio
import os
from services.database_service import (
    get_due_scheduled_order_ids,
    claim_scheduled_order,
    get_order_by_id_full,
    update_order_status,
)
from services.rabbitmq import publish_order

POLL_SECONDS = int(os.getenv("SCHEDULED_POLL_SECONDS", "30"))
BATCH_SIZE = int(os.getenv("SCHEDULED_BATCH_SIZE", "50"))

async def _loop():
    print(f"⏱️  Scheduled dispatcher activo (cada {POLL_SECONDS}s)...")
    while True:
        try:
            ids = await get_due_scheduled_order_ids(BATCH_SIZE)
            if ids:
                for order_id in ids:
                    claimed = await claim_scheduled_order(order_id)
                    if not claimed:
                        continue

                    order = await get_order_by_id_full(order_id)
                    if not order:
                        continue

                    try:
                        await publish_order(order)
                        print(f"[OK] Pedido programado liberado a Rabbit: {order_id}")
                    except Exception as e:
                        # Si falla Rabbit, revertimos para reintentar en el siguiente ciclo
                        print(f"[WARNING] No se pudo publicar pedido programado {order_id}: {e}")
                        try:
                            await update_order_status(order_id, "SCHEDULED")
                        except Exception as e2:
                            print(f"[ERROR] Error intentando revertir a SCHEDULED {order_id}: {e2}")

        except asyncio.CancelledError:
            print("[DISPATCHER] Scheduled dispatcher detenido.")
            raise
        except Exception as e:
            print(f"[WARNING] Error en dispatcher: {e}")

        await asyncio.sleep(POLL_SECONDS)

def start_scheduled_dispatcher() -> asyncio.Task:
    return asyncio.create_task(_loop())

async def stop_scheduled_dispatcher(task: asyncio.Task):
    if not task:
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
