from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now, timedelta
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from django.db import transaction

class CartView(generics.RetrieveAPIView):
    """Retrieve the authenticated user's cart."""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(generics.CreateAPIView):
    """Add an item to the authenticated user's cart."""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart, product=product)

        if not item_created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)

        cart_item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class RemoveFromCartView(generics.DestroyAPIView):
    """Remove an item from the authenticated user's cart."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')

        try:
            cart = Cart.objects.get(user=user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response({'message': "Item removed from cart."}, status=status.HTTP_200_OK)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({'message': "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)
        
class ClearCartView(generics.DestroyAPIView):
    """Clear the authenticated user's cart."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            cart.items.all().delete()
            return Response({'message': "Cart cleared."}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'error': "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        
class ExpiredCartCleanupView(generics.DestroyAPIView):
    """Remove carts older than 24 hours."""
    def delete(self, request, *args, **kwargs):
        expiration_time = now() - timedelta(hours=24)
        expired_carts = Cart.objects.filter(updated_at_lt=expiration_time)
        expired_carts.delete()
        return Response({'message': "Expired carts removed."}, status=status.HTTP_200_OK)
    
class PlaceOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({'error': "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get shipping address and payment method from request data
        shipping_address = request.data.get('shipping_address')
        payment_method = request.data.get('payment_method')

        if not shipping_address or not payment_method:
            return Response({'error': "Shipping address and payment method are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                shipping_address=shipping_address,
                payment_method=payment_method, 
                total_price=cart.get_total_price()
            )

        for item in cart_items:
            #! Ensure enough stock is available
            if item.quantity > item.product.stock:
                return Response({
                    'error': f"Not enough stock for {item.product.name}."
                }, status=status.HTTP_400_BAD_REQUEST)

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price * item.quantity
            )

            #? Reduce the stock of the product
            item.product.stock -= item.quantity
            item.product.save()

        cart.items.all().delete() #! Clearing the carts after placing order
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)