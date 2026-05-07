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
        return obj.get_total_price()
    
class CartAddUpdateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=False)
    product = serializers.IntegerField(required=False, write_only=True)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        product_id = data.get('product_id') or data.get('product')
        if not product_id:
            raise serializers.ValidationError({"product": "Product ID is required."})

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product": "Invalid product ID."})

        cart = self.context.get('cart')
        existing_quantity = 0
        if cart:
            existing_quantity = CartItem.objects.filter(cart=cart, product=product).values_list('quantity', flat=True).first() or 0

        requested_total = existing_quantity + data['quantity']
        if requested_total > product.stock:
            raise serializers.ValidationError("Requested quantity exceeds available stock.")

        data['product'] = product
        data['quantity'] = requested_total
        data.pop('product_id', None)
        return data

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")
        return value
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'created_at', 'updated_at', 'items', 'shipping_address', 'payment_method']
        read_only_fields = ['id', 'user', 'total_price', 'status', 'created_at', 'updated_at']

    def validate_payment_method(self, value):
        valid_methods = ['cod', 'card', 'paypal']
        if value not in valid_methods:
            raise serializers.ValidationError("Invalid payment method selected.")
        return value
