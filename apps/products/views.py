from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsSellerOrAdmin

class ProductCreateView(generics.CreateAPIView):
    """Only sellers or admins can add products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class ProductListView(generics.ListAPIView):
    """Anyone can view products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a single product."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductUpdateView(generics.UpdateAPIView):
    """Only sellers or admins can update products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOrAdmin]

    def perform_update(self, serializer):
        product = self.get_object()
        if self.request.user != product.seller and not self.request.user.is_staff:
            raise PermissionDenied("You are not authorized to update this product.")
        serializer.save()

class ProductDeleteView(generics.DestroyAPIView):
    """Only sellers or admins can delete products."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOrAdmin]

    def perform_destroy(self, instance):
        if self.request.user != instance.seller and not self.request.user.is_staff:
            raise PermissionDenied("You are not authorized to delete this product.")
        instance.delete()