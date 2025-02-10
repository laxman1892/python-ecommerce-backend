import uuid
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from orders.models import Order
from .serializers import PaymentSerializer

class ProcessPaymentView(generics.CreateAPIView):
    """Payment processing with dummy payment gateway"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        order_id = request.data.get('order_id')
        amount = request.data.get('amount')

        order = get_object_or_404(Order, id=order_id, user=user)

        if order.total_price != float(amount):
            return Response({
                'error': "Invalid payment amount"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #* Simulating a dummy payment gateway response
        transation_id = uuid.uuid4()
        payment = Payment.objects.create(
            user=user,
            order=order,
            amount=amount,
            status="completed",
            transation_id=transation_id,
        )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
    
class PaymentHistoryView(generics.ListAPIView):
    """Retrieves all past payments of the authenticated user."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')
    
class PaymentDetailView(generics.RetrieveAPIView):
    """Retrieves a single payment record."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)