"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # User management
    path('api/products/', include('products.urls')),  # Products
    path('api/cart/', include('cart.urls')),  # Shopping cart
    # path('api/orders/', include('apps.orders.urls')),  # Orders
    path('api/payments/', include('payments.urls')),  # Payments
    # path('api/shipping/', include('apps.shipping.urls')),  # Shipping & tracking
    # path('api/admin-panel/', include('apps.admin_panel.urls')),  # Admin dashboard
]
