from django.urls import path
from . import views

urlpatterns = [
    # Define your URL patterns here
    # Example:
    path('shipping/', views.shipping_home, name='shipping_home'),
]