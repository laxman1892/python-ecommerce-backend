from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
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
    
class CartAddUpdateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")
        return value
    
    def validate(self, data):
        product = Product.objects.get(id=data['product_id'])
        if data['quantity'] > product.stock:
            raise serializers.ValidationError("Requested quantity exceeds available stock.")
        return data
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='order_items')

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'created_at', 'updated_at', 'items', 'shipping_address', 'payment_method']
        read_only_fields = ['id', 'user', 'total_price', 'status', 'created_at', 'updated_at']

    def validate_payment_method(self, value):
        valid_methods = ['cod', 'card', 'paypal']
        if value not in valid_methods:
            raise serializers.ValidationError("Invalid payment method selected.")
        return value