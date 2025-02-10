from django.urls import path
from .views import (
    ShippingAddressView,
    UserShippingAddressListView,
    ShipmentTrackingView,
    UpdateShipmentStatusView
)

urlpatterns = [
    path('shipping/', UserShippingAddressListView.as_view(), name='user-shipping-addresses'),
    path('shipping/add/', ShippingAddressView.as_view(), name='add-shipping-address'),
    path('tracking/<int:pk>/', ShipmentTrackingView.as_view(), name='shipment-tracking'),
    path('tracking/update/<int:pk>/', UpdateShipmentStatusView.as_view(), name='update-shipment-status'),
]
