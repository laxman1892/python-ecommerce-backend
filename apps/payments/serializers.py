from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Payment.STATUS_CHOICES, read_only=True)
    transaction_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'order', 'amount', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['id', 'status', 'transaction_id', 'created_at']