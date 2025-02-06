from django.urls import path
from .views import (
    CartView, AddToCartView, RemoveFromCartView, 
    ClearCartView, ExpiredCartCleanupView
)

urlpatterns = [
    path('', CartView.as_view(), name='cart-detail'),
    path('add/', AddToCartView.as_view(), name='cart-add'),
    path('remove/', RemoveFromCartView.as_view(), name='cart-remove'),
    path('clear/', ClearCartView.as_view(), name='cart-clear'),
    path('cleanup/', ExpiredCartCleanupView.as_view(), name='cart-cleanup'),
]