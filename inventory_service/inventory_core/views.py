from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Product

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
            Product.objects.create(
                name=name,
                description=description or "",
                price=price,
                stock=stock,
            )
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
        return redirect("inventory_index")

class DeleteProductView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return redirect("inventory_index")