from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from . import messaging

@receiver(post_save, sender=Order)
def on_order_created(sender, instance: Order, created, **kwargs):
    if not created:
        return
    payload = {
        "id": instance.id,
        "user_id": instance.user_id,
        "product_id": instance.product_id,
        "quantity": instance.quantity,
        "status": instance.status,
        "total_price": float(instance.total_price),
        "created_at": instance.created_at.isoformat() if instance.created_at else None,
    }
    messaging.publish_event("order.created", payload)