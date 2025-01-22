from django.urls import path
from .views import RegistrationView, PasswordResetRequestView, PasswordResetView, CustomLoginView


urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', PasswordResetView.as_view(), name='password_reset'),
]