from django.http import JsonResponse
def debug_inventory_cache(request):
    products = cache.get("inventory_products", {})
    return JsonResponse(products)
from django.shortcuts import render, redirect
from .models import Order, Product
from .messaging import publish_event
from django.core.cache import cache
import uuid


def order_create(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity"))
        user_id = "guest"
        status = "created"
        total_price = 100.0  # or fetch from inventory if you want
        order_id = uuid.uuid4().hex
        order = Order.objects.create(
            id=order_id,
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            status=status,
            total_price=total_price,
        )
        # Always send items as a list of dicts with product_id and quantity
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
        return redirect("order_success")
    inventory_products = Product.objects.all()
    return render(request, "order_create.html", {"inventory_products": inventory_products})


def order_success(request):
    return render(request, "order_success.html")