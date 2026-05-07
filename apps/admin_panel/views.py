from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, Order
from payments.models import Payment
from products.models import Product
from shipping.models import ShipmentTracking


class IsAdminRole(BasePermission):
    """Allow Django staff users or users with the project's admin role."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.role == 'admin')
        )


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        User = get_user_model()
        return Response({
            'users': User.objects.count(),
            'products': Product.objects.count(),
            'carts': Cart.objects.count(),
            'orders': Order.objects.count(),
            'payments': Payment.objects.count(),
            'shipments': ShipmentTracking.objects.count(),
        })
