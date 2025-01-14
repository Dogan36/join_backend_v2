from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from .serializers import WorkspaceSerializer
from workspaces.models import Workspace
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

class WorkspaceViewSet(viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        # Optionale Filterung, um nur die Workspaces anzuzeigen, zu denen der User gehört
        user = self.request.user
        return Workspace.objects.filter(members=user)
    
class JoinWorkspace(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        join_code = request.data.get('join_code')
        workspace = get_object_or_404(Workspace, join_code=join_code)
        workspace.members.add(request.user)
        return Response({'message': 'You have successfully joined the workspace'}, status=status.HTTP_200_OK)