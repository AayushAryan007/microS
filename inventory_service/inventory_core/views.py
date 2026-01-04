from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Product
from .messaging import publish_inventory_update
import subprocess
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

class InventoryView(View):
    template_name = "inventory_index.html"

    def get(self, request):
        products = Product.objects.all()
        return render(request, self.template_name, {"products": products})

    def post(self, request):
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        if name and price and stock:
            product = Product.objects.create(
                name=name,
                description=description or "",
                price=price,
                stock=stock,
            )
            publish_inventory_update("inventory.updated", {
                "action": "created",
                "product": {
                    "id": str(product.id),
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock,
                }
            })
        return redirect("inventory_index")

class EditProductView(View):
    template_name = "edit_product.html"

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, self.template_name, {"product": product})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.save()
        publish_inventory_update("inventory.updated", {
            "action": "updated",
            "product": {
                "id": str(product.id),
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
            }
        })
        return redirect("inventory_index")

class DeleteProductView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product_id = str(product.id)
        product.delete()
        publish_inventory_update("inventory.updated", {
            "action": "deleted",
            "product": {
                "id": product_id,
            }
        })
        return redirect("inventory_index")

def refresh_order_page(request):
    subprocess.Popen(["python", "manage.py", "publish_full_inventory"])
    return HttpResponseRedirect(reverse("inventory_index"))

    
def products_list(request):
    products = list(Product.objects.values('id', 'name', 'description', 'price', 'stock'))
    return JsonResponse(products, safe=False)