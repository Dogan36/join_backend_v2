from rest_framework.permissions import BasePermission
from .models import Workspace

class IsWorkspaceMember(BasePermission):
    """
    Erlaubt den Zugriff nur Benutzern, die Mitglied des Workspaces sind.
    """

    def has_permission(self, request, view):
        workspace_id = view.kwargs.get('workspace_id')
        if not workspace_id:
            return False
        return Workspace.objects.filter(id=workspace_id, members=request.user).exists()