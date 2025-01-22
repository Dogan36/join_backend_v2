from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, InvitePerEmailView, CategoryViewSet, ColorViewSet, TaskViewSet, SubtaskViewSet


router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'colors', ColorViewSet, basename='color')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'subtasks', SubtaskViewSet, basename='subtask')



urlpatterns = [
    path('', include(router.urls)),
    path('invite/', InvitePerEmailView.as_view(), name='invite-per-email'),
]