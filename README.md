# Python Ecommerce Backend

A Django REST Framework ecommerce backend with JWT authentication, product management, cart checkout, orders, dummy payments, shipping, and a small admin dashboard.

## Features

- Custom user model with `buyer`, `seller`, and `admin` roles
- JWT login, logout, and authenticated profile retrieval/update
- Product catalog list/detail endpoints
- Seller/admin product create, update, and delete permissions
- Authenticated shopping cart with stock validation
- Order placement from cart with stock reduction and cart clearing
- Dummy payment simulator with completed and failed payment outcomes
- Payment history and payment detail endpoints
- Shipping address creation and shipment tracking
- Seller-scoped shipment status updates
- Admin dashboard counts for users, products, carts, orders, payments, and shipments
- Automated API tests for the main ecommerce flow

## Tech Stack

- Python
- Django 5.1.5
- Django REST Framework 3.15.2
- Simple JWT
- SQLite for local development

## Setup

Create and activate a virtual environment:

```powershell
python -m venv ecomenv
.\ecomenv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Apply migrations:

```powershell
python manage.py migrate
```

Create an admin user if needed:

```powershell
python manage.py createsuperuser
```

Run the development server:

```powershell
python manage.py runserver
```

## Verification

Run Django checks:

```powershell
python manage.py check
```

Check for pending migrations:

```powershell
python manage.py makemigrations --check --dry-run
```

Run tests:

```powershell
python manage.py test --noinput
```

Run dependency checks:

```powershell
python -m pip check
```

## API Overview

### Users

- `POST /api/users/register/` - Register a buyer account
- `POST /api/users/login/` - Login and receive JWT tokens
- `POST /api/users/logout/` - Blacklist a refresh token
- `GET /api/users/profile/` - Retrieve authenticated user profile
- `PATCH /api/users/profile/` - Update authenticated user profile

Public registration always creates a `buyer` account. Seller/admin promotion should be handled separately by trusted admin functionality.

### Products

- `GET /api/products/` - List products
- `GET /api/products/<id>/` - Retrieve product detail
- `POST /api/products/create/` - Create product as seller/admin
- `PUT/PATCH /api/products/<id>/update/` - Update product as owner seller/admin
- `DELETE /api/products/<id>/delete/` - Delete product as owner seller/admin

### Cart

- `GET /api/cart/` - Retrieve authenticated user's cart
- `POST /api/cart/add/` - Add a product to cart
- `DELETE /api/cart/remove/` - Remove a product from cart
- `DELETE /api/cart/clear/` - Clear cart
- `DELETE /api/cart/cleanup/` - Delete carts older than 24 hours

Cart add accepts either `product` or `product_id` plus `quantity`.

### Orders

- `GET /api/orders/` - List authenticated user's orders
- `POST /api/orders/place/` - Place an order from the authenticated user's cart
- `GET /api/orders/<id>/` - Retrieve authenticated user's order detail

The same order endpoints are also available under `/api/cart/orders/` for backward compatibility.

### Payments

- `POST /api/payments/process/` - Process a dummy payment
- `GET /api/payments/history/` - List authenticated user's payment history
- `GET /api/payments/<id>/` - Retrieve authenticated user's payment detail

Dummy payment request example:

```json
{
  "order_id": 1,
  "amount": "20.00",
  "simulate_result": "completed"
}
```

`simulate_result` is optional and defaults to `completed`. Supported values:

- `completed` - Creates a completed payment and moves the order to `processing`
- `failed` - Creates a failed payment and returns HTTP 402

Completed payments cannot be duplicated for the same order.

### Shipping

- `GET /api/shipping/shipping/` - List authenticated user's shipping addresses
- `POST /api/shipping/shipping/add/` - Add a shipping address for an order
- `GET /api/shipping/tracking/<id>/` - Retrieve shipment tracking
- `PATCH /api/shipping/tracking/update/<id>/` - Update shipment tracking as admin or owning seller

### Admin Panel

- `GET /api/admin-panel/` - Admin-only dashboard summary

## Development Notes

- `db.sqlite3` is ignored and should be created locally with migrations.
- Static and media upload directories are ignored by Git.
- `python manage.py check --deploy` still reports expected production-hardening warnings for local settings, including `DEBUG=True`, empty `ALLOWED_HOSTS`, and hardcoded development `SECRET_KEY`.

Before deploying, move environment-specific settings such as `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, database credentials, and HTTPS cookie settings into environment variables.
