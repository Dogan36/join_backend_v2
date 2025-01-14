from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from .serializers import WorkspaceSerializer
from workspaces.models import Workspace
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

class WorkspaceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
class JoinWorkspaceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        join_code = request.data.get('join_code')
        workspace = get_object_or_404(Workspace, join_code=join_code)
        workspace.members.add(request.user)
        return Response({'message': 'You have successfully joined the workspace'}, status=status.HTTP_200_OK)