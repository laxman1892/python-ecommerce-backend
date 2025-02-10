from rest_framework import serializers
from .models import ShippingAddress, ShipmentTracking

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = "__all__"
        read_only_fields = ['user', 'order', 'created_at']

class ShipmentTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentTracking
        fields = "__all__"
        read_only_fields = ['order', 'tracking_number', 'updated_at', 'delivered_at']
        