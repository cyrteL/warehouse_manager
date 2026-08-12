from django.db import models


class Ware(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.CharField(max_length=50)
    serial = models.CharField(max_length=50)
    quantity = models.IntegerField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Returns a readable string representation in the admin panel
    def __str__(self):
        return self.name

