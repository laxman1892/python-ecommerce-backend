from django.db import models
from django.contrib.auth import get_user_model
from cart.models import Order

User = get_user_model()

class ShippingAddress(models.Model):
    """Stores shipping address details for an order."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipping")
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    created_at = models.CharField(auto_now_add=True)

    def __str__(self):
        return f"Shipping Address for Order {self.order.id}"
    
class ShipmentTracking(models.Model):
    """Tracks the shipping status and delivery details of an order."""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipping")
    tracking_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

    STATUS_CHOICES = [
        ('pending', "Pending"),
        ('shipped', "Shipped"),
        ('out_for_delivery', "Out for delivery"),
        ('delivered', "Delivered"),
        ('cancelled', "Cancelled"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    estimated_delivery_date = models.DateField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tracking {self.tracking_number} - {self.status}"