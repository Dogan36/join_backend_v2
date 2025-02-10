from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrationView, PasswordResetRequestView, PasswordResetView, CustomLoginView, ContactViewSet, ChangePasswordView, UpdateProfileView

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contact')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', PasswordResetView.as_view(), name='password_reset'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),
]

