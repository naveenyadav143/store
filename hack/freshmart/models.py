from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Store(models.Model):
    store_name = models.CharField(max_length=100, verbose_name="Store Name")
    address = models.TextField(verbose_name="Address")
    owner_name = models.CharField(max_length=100, verbose_name="Owner Name")
    contact_number = models.CharField(max_length=20, verbose_name="Contact Number")
    image = models.URLField(blank=True, null=True, verbose_name="Image URL")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stores", verbose_name="Owner")

    def __str__(self):
        return self.store_name


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Store")
    name = models.CharField(max_length=100, verbose_name="Product Name")
    price = models.FloatField(default=0.0, verbose_name="Price")
    quantity = models.IntegerField(default=0, verbose_name="Quantity")
    image = models.URLField(blank=True, null=True, verbose_name="Image URL")
    sold_quantity = models.IntegerField(default=0, verbose_name="Sold Quantity")

    def sell(self, quantity):
        """Decrease stock and increase sold quantity."""
        if quantity > self.quantity:
            raise ValueError("Not enough stock to sell.")
        self.quantity -= quantity
        self.sold_quantity += quantity
        self.save()

    def __str__(self):
        return self.name
