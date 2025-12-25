from django.core.management.base import BaseCommand
from inventory_core.models import Product
from inventory_core.messaging import publish_inventory_update

class Command(BaseCommand):
    help = "Publish the full inventory to the order service"

    def handle(self, *args, **options):
        products = Product.objects.all()
        for product in products:
            publish_inventory_update("inventory.updated", {
                "action": "synced",
                "product": {
                    "id": str(product.id),
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock,
                }
            })
        self.stdout.write(self.style.SUCCESS("Published full inventory."))