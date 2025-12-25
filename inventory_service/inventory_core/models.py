from django.db import models

class Product(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.BigIntegerField()  # int64 in Go; store smallest currency unit (e.g., cents)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'