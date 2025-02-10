from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ShippingAddress, ShipmentTracking
from .serializers import ShippingAddressSerializer, ShipmentTrackingSerializer
from cart.models import Order

class ShippingAddressView(generics.CreateAPIView):
    """Allows user to add a shipping address for their order."""
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        order_id = request.data.get('order')

        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response({
                'error': "Order not found or does not belong to you."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if ShippingAddress.objects.filter(order=order).exists:
            return Response({
                'error': "Shipping address already exists for this order."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserShippingAddressListView(generics.ListAPIView):
    """Retrieves all shipping addresses for the authenticated user."""
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)
    
class ShipmentTrackingView(generics.RetrieveAPIView):
    """Retrieves the shipment tracking details for an order."""
    serializer_class = ShipmentTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShipmentTracking.objects.filter(order__user=self.request.user)
    
class UpdateShipmentStatusView(generics.UpdateAPIView):
    """Allows admins or sellers to update the shipment tracking details."""
    serializer_class = ShipmentTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShipmentTracking.objects.all()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)