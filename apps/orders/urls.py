from django.urls import path
from cart.views import OrderDetailView, PlaceOrderView, UserOrderListView

urlpatterns = [
    path('', UserOrderListView.as_view(), name='order-list'),
    path('place/', PlaceOrderView.as_view(), name='order-place'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]
