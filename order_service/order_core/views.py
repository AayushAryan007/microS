from django.http import JsonResponse
def debug_inventory_cache(request):
    products = cache.get("inventory_products", {})
    return JsonResponse(products)
from django.shortcuts import render, redirect
from .models import Order, Product
from .messaging import publish_event
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import uuid

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_create(request):
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity"))
    user_id = str(request.user.id)  # Get user ID from JWT token
    status = "created"
    total_price = 100.0  # Or fetch from inventory

    order_id = uuid.uuid4().hex
    order = Order.objects.create(
        id=order_id,
        user_id=user_id,
        product_id=product_id,
        quantity=quantity,
        status=status,
        total_price=total_price,
    )
    payload = {
        "order_id": order.id,
        "items": [
            {
                "product_id": order.product_id,
                "quantity": order.quantity,
            }
        ],
        "user_id": order.user_id,
        "total_price": float(order.total_price),
    }
    publish_event("order.created", payload)
    return Response({'message': 'Order created', 'order_id': order.id})

def order_success(request):
    return render(request, "order_success.html")

from .models import Order

def orders_list(request):
    orders = list(Order.objects.values(
        'id',
        'user_id',
        'product_id',
        'quantity',
        'status',
        'total_price',
        'created_at',
        'updated_at'
    ))
    return JsonResponse(orders, safe=False)