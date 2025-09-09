# items/models.py
from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    image_url = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class PickupHub(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    total_slots = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_address = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    pickup_hub = models.ForeignKey('PickupHub', on_delete=models.SET_NULL, null=True, blank=True)
    pickup_datetime = models.DateTimeField(null=True, blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
        ('failed', 'Failed'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.item.name}"

