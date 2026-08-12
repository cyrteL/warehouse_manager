from django.db import models


class Ware(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    inventory = models.CharField(max_length=50, unique=True, null=True)
    serial = models.CharField(max_length=50, null=True)
    quantity = models.FloatField(default=1.)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

