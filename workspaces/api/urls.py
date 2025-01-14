from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet
from .views import JoinWorkspace

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'join-workspaces', JoinWorkspace , basename='workspace')

urlpatterns = [
    path('', include(router.urls)),
]