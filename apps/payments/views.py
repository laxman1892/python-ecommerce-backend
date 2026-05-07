from decimal import Decimal, InvalidOperation
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from cart.models import Order
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

        try:
            payment_amount = Decimal(str(amount))
        except (InvalidOperation, TypeError):
            return Response({'error': "Invalid payment amount"}, status=status.HTTP_400_BAD_REQUEST)

        if order.total_price != payment_amount:
            return Response({
                'error': "Invalid payment amount"
            }, status=status.HTTP_400_BAD_REQUEST)

        if Payment.objects.filter(order=order, status='completed').exists():
            return Response({
                'error': "This order has already been paid."
            }, status=status.HTTP_400_BAD_REQUEST)

        simulate_result = request.data.get('simulate_result', 'completed')
        if simulate_result not in ['completed', 'failed']:
            return Response({
                'error': "simulate_result must be either 'completed' or 'failed'."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Simulate a deterministic payment gateway response for local/dev use.
        payment = Payment.objects.create(
            user=user,
            order=order,
            amount=payment_amount,
            status=simulate_result,
        )

        if simulate_result == 'failed':
            return Response(PaymentSerializer(payment).data, status=status.HTTP_402_PAYMENT_REQUIRED)

        order.status = 'processing'
        order.save(update_fields=['status'])
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
