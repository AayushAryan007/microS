import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from . import messaging

@csrf_exempt
@require_GET
def publish_order(request):
    oid = uuid.uuid4().hex
    order = Order.objects.create(
        id=oid, user_id="u1", product_id="p1",
        quantity=1, status="created", total_price=100.00
    )
    payload = {
        "id": order.id,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": order.status,
        "total_price": float(order.total_price),
        "created_at": order.created_at.isoformat(),
    }
    messaging.publish_event("order.created", payload)
    return JsonResponse({"published": True, "order_id": oid})