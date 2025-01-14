from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet
from .views import JoinWorkspaceViewSet

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'join-workspace', JoinWorkspaceViewSet, basename='join-workspace')

urlpatterns = [
    path('', include(router.urls)),
]