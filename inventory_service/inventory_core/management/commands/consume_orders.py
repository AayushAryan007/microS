import json, os, time
import pika
from django.core.management.base import BaseCommand
from django.db import transaction
from dotenv import load_dotenv
from inventory_core.models import Product
from inventory_core.messaging import publish_inventory_update

load_dotenv()

EXCHANGE_NAME = "order.events"
QUEUE_NAME = "inventory.order.created"
ROUTING_KEY = "order.created"

def _params():
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@127.0.0.1:5672/%2F")
    params = pika.URLParameters(url)
    params.heartbeat = 600
    params.blocked_connection_timeout = 300
    return params

class Command(BaseCommand):
    help = "Consume order events and update inventory"

    def handle(self, *args, **options):
        while True:
            try:
                self.consume()
            except Exception as e:
                import traceback
                self.stderr.write(f"Consumer error: {e!r}. Reconnecting in 5s...")
                traceback.print_exc()
                time.sleep(5)

    def consume(self):
        connection = pika.BlockingConnection(_params())
        ch = connection.channel()
        ch.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
        ch.queue_declare(queue=QUEUE_NAME, durable=True)
        ch.queue_bind(queue=QUEUE_NAME, exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY)
        ch.basic_qos(prefetch_count=1)

        def on_message(channel, method, properties, body):
            try:
                payload = json.loads(body.decode("utf-8"))
                self.stdout.write(f"Received payload: {payload}")
                items = payload.get("items", [])
                for item in items:
                    if "product_id" not in item or "quantity" not in item:
                        raise KeyError("product_id or quantity missing in item")
                    product_id = item["product_id"]
                    qty = int(item["quantity"])
                    with transaction.atomic():
                        prod = Product.objects.select_for_update().get(id=product_id)
                        prod.stock = max(0, prod.stock - qty)
                        prod.save(update_fields=["stock", "updated_at"])
                        self.stdout.write(f"Updated stock for product {product_id} by -{qty}")
                        publish_inventory_update("inventory.updated", {
                            "action": "stock_changed",
                            "product": {
                                "id": str(prod.id),
                                "name": prod.name,
                                "description": prod.description,
                                "price": prod.price,
                                "stock": prod.stock,
                            }
                        })
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Product.DoesNotExist:
                self.stderr.write(f"Product {product_id} not found in payload: {payload}; acking.")
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as ex:
                self.stderr.write(f"Processing error: {ex}; payload: {payload}; acking to avoid redelivery loop.")
                channel.basic_ack(delivery_tag=method.delivery_tag)

        ch.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)
        self.stdout.write("Consumer started. Waiting for messages...")
        try:
            ch.start_consuming()
        finally:
            if not connection.is_closed:
                connection.close()