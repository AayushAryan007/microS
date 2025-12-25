import os, json, time
import pika
from django.core.management.base import BaseCommand
from order_core.models import Product
from dotenv import load_dotenv

load_dotenv()

EXCHANGE_NAME = "inventory.events"
QUEUE_NAME = "order.inventory.updated"
ROUTING_KEY = "inventory.updated"

def _params():
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@127.0.0.1:5672/%2F")
    params = pika.URLParameters(url)
    params.heartbeat = 600
    params.blocked_connection_timeout = 300
    return params

class Command(BaseCommand):
    help = "Consume inventory update events and update Product table"

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

        # Track if we're in a sync session
        self.syncing = False
        self.synced_ids = set()

        def on_message(channel, method, properties, body):
            payload = json.loads(body.decode("utf-8"))
            action = payload.get("action")
            product = payload.get("product", {})
            pid = product.get("id")
            if not pid:
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return

            if action == "synced":
                # On first "synced" message, start a sync session
                if not self.syncing:
                    self.syncing = True
                    self.synced_ids = set()
                    Product.objects.all().delete()
                # Add/update this product
                Product.objects.update_or_create(
                    id=pid,
                    defaults={
                        "name": product.get("name", ""),
                        "description": product.get("description", ""),
                        "price": product.get("price", 0),
                        "stock": product.get("stock", 0),
                    }
                )
                self.synced_ids.add(pid)
                self.stdout.write(f"Synced product {pid}")
            elif action == "deleted":
                Product.objects.filter(id=pid).delete()
                self.stdout.write(f"Deleted product {pid}")
            else:
                Product.objects.update_or_create(
                    id=pid,
                    defaults={
                        "name": product.get("name", ""),
                        "description": product.get("description", ""),
                        "price": product.get("price", 0),
                        "stock": product.get("stock", 0),
                    }
                )
                self.stdout.write(f"Updated/created product {pid}")

            channel.basic_ack(delivery_tag=method.delivery_tag)

        ch.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)
        self.stdout.write("Inventory consumer started. Waiting for messages...")
        try:
            ch.start_consuming()
        finally:
            if not connection.is_closed:
                connection.close()