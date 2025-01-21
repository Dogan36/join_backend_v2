from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from .serializers import WorkspaceSerializer
from workspaces.models import Workspace
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.core.mail import send_mail

class WorkspaceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.filter(members=self.request.user)

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

    