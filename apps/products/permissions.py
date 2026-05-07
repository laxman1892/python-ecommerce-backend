from rest_framework import permissions

class IsSellerOrAdmin(permissions.BasePermission):
    """Custom permission class to allow only sellers or admins to add/edit/delete products."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ["seller", "admin"] or request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the seller or admin."""
        return request.user == obj.seller or request.user.role == "admin" or request.user.is_staff
