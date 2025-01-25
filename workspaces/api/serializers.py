from rest_framework import serializers
from workspaces.models import Workspace, Category, Task, Subtask
from django.contrib.auth import get_user_model
from user_auth_app.api.serializers import CustomUserSerializer
User = get_user_model()

class WorkspaceSerializer(serializers.ModelSerializer):
    members = CustomUserSerializer(many=True, read_only=True)
    owner = CustomUserSerializer(read_only=True)
    join_code = serializers.CharField(read_only=True)
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'members', 'owner', 'join_code']

    def create(self, validated_data):
        # Der User, der den Request sendet, wird als Owner gesetzt
        owner = self.context['request'].user
        validated_data['owner'] = owner
        
        # Workspace erstellen
        workspace = Workspace.objects.create(**validated_data)
        
        # Stelle sicher, dass der Owner auch zu den Mitgliedern hinzugefügt wird
        workspace.members.add(owner)
        
        return workspace

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if members is not None:
            instance.members.set(members)

        return instance

class SubtaskSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    class Meta:
        model = Subtask
        fields = ['id', 'name', 'done', 'task']

class TaskSerializer(serializers.ModelSerializer):
    workspace = serializers.PrimaryKeyRelatedField(
        queryset=Workspace.objects.all(),
        many=False
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,  # Erlaubt Null-Werte, falls keine Kategorie zugeordnet ist
        required=False    # Optional, je nachdem, ob das Feld erforderlich ist
    )
    subtasks = SubtaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'due_date', 'category', 'status', 'workspace', 'subtasks']

    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'workspace']


