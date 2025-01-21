from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, InvitePerEmailView


router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')



urlpatterns = [
    path('', include(router.urls)),
    path('invite/', InvitePerEmailView.as_view(), name='invite-per-email'),
]