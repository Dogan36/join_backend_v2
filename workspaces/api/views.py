from venv import logger
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated

from workspaces import models
from workspaces.permissions import IsWorkspaceMember
from .serializers import WorkspaceSerializer, CategorySerializer, TaskSerializer, ColorSerializer, SubtaskSerializer
from workspaces.models import Workspace, Category, Task, Subtask
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)
class WorkspaceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.filter(members=self.request.user)

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def first_member_workspace(self, request):
        
        workspace = self.get_queryset().first()
        if workspace:
            serializer = self.get_serializer(workspace)
            return Response(serializer.data)
        else:
           return Response(None, status=200)
    
    @action(methods=['post'], detail=False, url_path='join-by-code')
    def join_by_code(self, request):
        join_code = request.data.get('join_code')
        workspace = get_object_or_404(Workspace, join_code=join_code)
        
        # Check if the user is already a member
        if request.user in workspace.members.all():
            return Response({'message': 'You are already a member of this workspace'}, status=status.HTTP_400_BAD_REQUEST)
        
        workspace.members.add(request.user)
        workspace.save()
        return Response({'message': 'You have successfully joined the workspace'}, status=status.HTTP_200_OK)    

    @action(methods=['post'], detail=False, url_path='leave')
    def leave_workspace(self, request):
        workspace_id = request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        if request.user not in workspace.members.all():
            return Response({'message': 'You are not a member of this workspace'}, status=status.HTTP_400_BAD_REQUEST)

        workspace.members.remove(request.user)
        workspace.save()
        return Response({'message': 'You have successfully left the workspace'}, status=status.HTTP_200_OK)
    
    @action(methods=['delete'], detail=False, url_path='delete-workspace')
    def delete_workspace(self, request):
        workspace_id = request.data.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        
        # Optional: Überprüfe, ob der angemeldete Benutzer berechtigt ist, diesen Workspace zu löschen
        if request.user.id != workspace.owner.id:
            return Response({'message': 'You do not have permission to delete this workspace'}, status=status.HTTP_403_FORBIDDEN)

        workspace.delete()
        return Response({'message': 'Workspace deleted successfully'}, status=status.HTTP_200_OK)
    
class InvitePerEmailView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('join_code')
        user = request.user   
        link = f"http://localhost:5173/"
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            send_mail(
                subject="Invitation to join workspace",
                message=f"{user.name} has invited you to join a workspace. Click the link to login to your account or create one: {link} and enter the code: {code}",
                html_message=f"{user.name} has invited you to join a workspace. <br> Click the link to login to your join account or create one: {link} <br> and enter the code: {code}",
                from_email="noreply@join.dogan-celik.com",
                recipient_list=[email],
            )
            return Response({"message": "Invitation has been sent"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to send invitation: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]
    serializer_class = TaskSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        context['workspace'] = workspace
        return context
    
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        if workspace_id:
            return Task.objects.filter(workspace_id=workspace_id).select_related('category', 'workspace').prefetch_related('subtasks')
        return Task.objects.none()
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        # Aufgabe wird mit dem Arbeitsbereich gespeichert
        task = serializer.save(workspace=workspace)

        # Hier fügst du die ausgewählten Kontakte hinzu, wenn sie im POST-Request enthalten sind
        selected_contact_ids = self.request.data.get('selected_contacts', [])
        if selected_contact_ids:
            users = User.objects.filter(id__in=selected_contact_ids)
            task.selected_contacts.set(users)  # Setzt die Kontakte für diese Aufgabe

        return Response(serializer.data, status=201)
    
class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        if workspace_id:
            return Category.objects.filter(workspace_id=workspace_id)
        return Category.objects.none()  # Keine Kategorien zurückgeben, wenn keine workspace_id vorhanden ist

    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, id=workspace_id)
        serializer.validated_data['workspace'] = workspace
        serializer.save()

    
