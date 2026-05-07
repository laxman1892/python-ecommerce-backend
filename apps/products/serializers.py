from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 'created_at', 'updated_at', 'seller']
        read_only_fields = ['id', 'created_at', 'updated_at', 'seller']

    def create(self, validated_data):
        """"Ensures only seller/admins can create products."""
        request = self.context['request']
        user = request.user

        if user.role not in ['seller', 'admin'] and not user.is_staff:
            raise serializers.ValidationError("You are not authorized to create products.")
        
        validated_data['seller'] = user
        return super().create(validated_data)
