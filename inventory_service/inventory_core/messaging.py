import os
import json
import pika
from dotenv import load_dotenv

load_dotenv()

EXCHANGE_NAME = "inventory.events"
EXCHANGE_TYPE = "topic"

def _params():
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@127.0.0.1:5672/%2F")
    params = pika.URLParameters(url)
    params.heartbeat = 600
    params.blocked_connection_timeout = 300
    return params

def publish_inventory_update(event_type, payload):
    conn = pika.BlockingConnection(_params())
    try:
        ch = conn.channel()
        ch.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)
        ch.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=event_type,
            body=json.dumps(payload).encode("utf-8"),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
    finally:
        conn.close()