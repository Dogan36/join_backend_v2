from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, InvitePerEmailView, CategoryViewSet, TaskViewSet, SubtaskViewSet

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')


urlpatterns = [
    path('', include(router.urls)),
]

# Registriere Sub-Router für tasks und categories innerhalb des Workspace-Routers
workspace_router = DefaultRouter()
workspace_router.register(r'tasks', TaskViewSet, basename='workspace-task')
workspace_router.register(r'categories', CategoryViewSet, basename='workspace-category')
workspace_router.register(r'subtasks', SubtaskViewSet, basename='workspace-subtask')


# Inkludiere Sub-Router in der Haupt-URL-Konfiguration
urlpatterns += [
    path('workspaces/<int:workspace_id>/', include(workspace_router.urls)),
    path('invite/', InvitePerEmailView.as_view(), name='invite-per-email'),
]