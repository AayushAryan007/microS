# models.py
from django.db import models

class Order(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    user_id = models.CharField(max_length=64)
    product_id = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=32, default='pending')
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'