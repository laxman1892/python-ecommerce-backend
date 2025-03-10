from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView, UserProfileView

urlpatterns = [
    # path('', views.UserView.as_view(), name='index'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]