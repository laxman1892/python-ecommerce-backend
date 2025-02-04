from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from datetime import timedelta

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, unique=True, null=True)
    # is_verified = models.BooleanField(default=False) #! for future reference
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    last_username_change = models.DateTimeField(null=True, blank=True)  
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')

    def can_change_username(self):
        """Checks if the user can change their username (once per month)"""
        if self.last_username_change:
            return now() >= self.last_username_change + timedelta(days=30)
        return True

    def __str__(self):
        return f"{self.username} ({self.role})"