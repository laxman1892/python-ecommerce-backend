from django.urls import path
from .views import (
    CartView, AddToCartView, RemoveFromCartView, 
    ClearCartView, ExpiredCartCleanupView, UserOrderListView, PlaceOrderView, OrderDetailView
)

urlpatterns = [
    # Cart endpoints
    path('', CartView.as_view(), name='cart-detail'),
    path('add/', AddToCartView.as_view(), name='cart-add'),
    path('remove/', RemoveFromCartView.as_view(), name='cart-remove'),
    path('clear/', ClearCartView.as_view(), name='cart-clear'),
    path('cleanup/', ExpiredCartCleanupView.as_view(), name='cart-cleanup'),

    # Order endpoints
    path('orders/', UserOrderListView.as_view(), name='order-list'),
    path('orders/place/', PlaceOrderView.as_view(), name='order-place'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]