from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from cart.models import Cart, CartItem, Order
from payments.models import Payment
from products.models import Product
from shipping.models import ShipmentTracking, ShippingAddress


User = get_user_model()


class EcommerceFlowTests(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='password123',
            role='seller',
        )
        self.admin_user = User.objects.create_user(
            username='store-admin',
            email='admin@example.com',
            password='password123',
            role='admin',
        )
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='password123',
            role='buyer',
        )
        self.product = Product.objects.create(
            name='Widget',
            description='A useful widget',
            price=Decimal('10.00'),
            stock=5,
            category='others',
            seller=self.seller,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_admin_role_can_create_product(self):
        self.authenticate(self.admin_user)

        response = self.client.post('/api/products/create/', {
            'name': 'Admin Widget',
            'description': 'Created by an admin role user',
            'price': '15.00',
            'stock': 3,
            'category': 'others',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name='Admin Widget').exists())

    def test_cart_add_rejects_quantity_above_stock(self):
        self.authenticate(self.buyer)

        response = self.client.post('/api/cart/add/', {
            'product': self.product.id,
            'quantity': 99,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(CartItem.objects.filter(cart__user=self.buyer).exists())

    def test_order_payment_and_shipping_flow(self):
        self.authenticate(self.buyer)

        add_response = self.client.post('/api/cart/add/', {
            'product': self.product.id,
            'quantity': 2,
        }, format='json')
        self.assertEqual(add_response.status_code, status.HTTP_200_OK)

        order_response = self.client.post('/api/cart/orders/place/', {
            'shipping_address': '123 Test Street',
            'payment_method': 'cod',
        }, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order_response.data['total_price'], '20.00')
        self.assertEqual(len(order_response.data['items']), 1)

        order = Order.objects.get(id=order_response.data['id'])
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertFalse(CartItem.objects.filter(cart__user=self.buyer).exists())

        payment_response = self.client.post('/api/payments/process/', {
            'order_id': order.id,
            'amount': '20.00',
        }, format='json')
        self.assertEqual(payment_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.get(order=order).status, 'completed')

        shipping_response = self.client.post('/api/shipping/shipping/add/', {
            'order': order.id,
            'full_name': 'Test Buyer',
            'phone_number': '1234567890',
            'address_line': '123 Test Street',
            'city': 'Testville',
            'state': 'TS',
            'postal_code': '12345',
            'country': 'Testland',
        }, format='json')
        self.assertEqual(shipping_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ShippingAddress.objects.filter(order=order).exists())

    def test_payment_rejects_duplicate_completed_payment(self):
        order = Order.objects.create(
            user=self.buyer,
            total_price=Decimal('10.00'),
            shipping_address='123 Test Street',
            payment_method='card',
        )
        Payment.objects.create(
            user=self.buyer,
            order=order,
            amount=order.total_price,
            status='completed',
        )
        self.authenticate(self.buyer)

        response = self.client.post('/api/payments/process/', {
            'order_id': order.id,
            'amount': '10.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.filter(order=order, status='completed').count(), 1)

    def test_dummy_payment_can_record_failed_payment(self):
        order = Order.objects.create(
            user=self.buyer,
            total_price=Decimal('10.00'),
            shipping_address='123 Test Street',
            payment_method='card',
        )
        self.authenticate(self.buyer)

        response = self.client.post('/api/payments/process/', {
            'order_id': order.id,
            'amount': '10.00',
            'simulate_result': 'failed',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(Payment.objects.get(order=order).status, 'failed')

    def test_seller_can_only_update_tracking_for_their_products(self):
        other_seller = User.objects.create_user(
            username='other-seller',
            email='other@example.com',
            password='password123',
            role='seller',
        )
        other_product = Product.objects.create(
            name='Other Widget',
            description='Owned by another seller',
            price=Decimal('20.00'),
            stock=2,
            category='others',
            seller=other_seller,
        )
        own_order = Order.objects.create(
            user=self.buyer,
            total_price=Decimal('10.00'),
            shipping_address='123 Test Street',
            payment_method='cod',
        )
        other_order = Order.objects.create(
            user=self.buyer,
            total_price=Decimal('20.00'),
            shipping_address='123 Test Street',
            payment_method='cod',
        )
        own_order.items.create(product=self.product, quantity=1, price=Decimal('10.00'))
        other_order.items.create(product=other_product, quantity=1, price=Decimal('20.00'))
        own_tracking = ShipmentTracking.objects.create(order=own_order, tracking_number='OWN123')
        other_tracking = ShipmentTracking.objects.create(order=other_order, tracking_number='OTHER123')

        self.authenticate(self.seller)
        own_response = self.client.patch(f'/api/shipping/tracking/update/{own_tracking.id}/', {
            'status': 'shipped',
        }, format='json')
        other_response = self.client.patch(f'/api/shipping/tracking/update/{other_tracking.id}/', {
            'status': 'shipped',
        }, format='json')

        self.assertEqual(own_response.status_code, status.HTTP_200_OK)
        self.assertEqual(other_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profile_can_be_updated(self):
        self.authenticate(self.buyer)

        response = self.client.patch('/api/users/profile/', {
            'first_name': 'Updated',
            'address': '456 New Street',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.first_name, 'Updated')
        self.assertEqual(self.buyer.address, '456 New Street')

    def test_expired_cart_cleanup_uses_valid_lookup(self):
        self.authenticate(self.admin_user)
        cart = Cart.objects.create(user=self.buyer)
        Cart.objects.filter(id=cart.id).update(updated_at=timezone.now() - timezone.timedelta(days=2))

        response = self.client.delete('/api/cart/cleanup/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Cart.objects.filter(id=cart.id).exists())

    def test_orders_api_lists_authenticated_users_orders(self):
        order = Order.objects.create(
            user=self.buyer,
            total_price=Decimal('10.00'),
            shipping_address='123 Test Street',
            payment_method='cod',
        )
        Order.objects.create(
            user=self.admin_user,
            total_price=Decimal('20.00'),
            shipping_address='456 Admin Street',
            payment_method='cod',
        )
        self.authenticate(self.buyer)

        response = self.client.get('/api/orders/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order.id)

    def test_admin_panel_dashboard_is_admin_only(self):
        self.authenticate(self.buyer)
        buyer_response = self.client.get('/api/admin-panel/')
        self.assertEqual(buyer_response.status_code, status.HTTP_403_FORBIDDEN)

        self.authenticate(self.admin_user)
        admin_response = self.client.get('/api/admin-panel/')

        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data['users'], 3)
        self.assertEqual(admin_response.data['products'], 1)

    def test_public_registration_cannot_choose_privileged_role(self):
        response = self.client.post('/api/users/register/', {
            'email': 'new-admin@example.com',
            'username': 'new-admin',
            'first_name': 'New',
            'last_name': 'Admin',
            'role': 'admin',
            'password': 'password123',
            'confirm_password': 'password123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='new-admin')
        self.assertEqual(user.role, 'buyer')
