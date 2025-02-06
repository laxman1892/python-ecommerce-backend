from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source= "product.name")
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'quantity', 'total_price']
        
    def get_total_price(self, obj):
        return obj.product.price * obj.quantity
    
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True) #? Nested serialization for cart items
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_cost']
        read_only_fields = ['id', 'user', 'items']

    def get_total_cost(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())