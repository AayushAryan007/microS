import json, os, time
import pika
from django.core.management.base import BaseCommand
from django.db import transaction
from dotenv import load_dotenv
from inventory_core.models import Product

load_dotenv()

EXCHANGE_NAME = "order.events"
QUEUE_NAME = "inventory.order.created"
ROUTING_KEY = "order.created"

def _params():
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")
    params = pika.URLParameters(url)
    params.heartbeat = 600
    params.blocked_connection_timeout = 300
    return params

class Command(BaseCommand):
    help = "Consume order events and update inventory"

    def handle(self, *args, **options):
        while True:
            try:
                self.stdout.write(f"Connecting to {os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/%2F')}")
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
                product_id = payload["product_id"]
                qty = int(payload["quantity"])

                with transaction.atomic():
                    prod = Product.objects.select_for_update().get(id=product_id)
                    new_stock = max(0, prod.stock - qty)
                    prod.stock = new_stock
                    prod.save(update_fields=["stock", "updated_at"])
                self.stdout.write(f"Updated stock for product {product_id} by -{qty}")
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Product.DoesNotExist:
                self.stderr.write(f"Product {payload.get('product_id')} not found; acking.")
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as ex:
                self.stderr.write(f"Processing error: {ex}; acking to avoid redelivery loop.")
                channel.basic_ack(delivery_tag=method.delivery_tag)

        ch.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)
        self.stdout.write("Consumer started. Waiting for messages...")
        try:
            ch.start_consuming()
        finally:
            if not connection.is_closed:
                connection.close()