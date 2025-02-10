from django.urls import path
from .views import ProcessPaymentView, PaymentHistoryView, PaymentDetailView

urlpatterns = [
     path('process/', ProcessPaymentView.as_view(), name='process-payment'),
     path('history/', PaymentHistoryView.as_view(), name='payment-history'),
     path('<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
]