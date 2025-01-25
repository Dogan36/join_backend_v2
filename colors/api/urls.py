from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ColorViewSet

router = DefaultRouter()
router.register(r'colors', ColorViewSet, basename='colors')

urlpatterns = [
    path('', include(router.urls)),
]