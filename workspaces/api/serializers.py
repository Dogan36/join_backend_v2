from rest_framework import serializers
from workspaces.models import Workspace, Category, Task, Subtask
from django.contrib.auth import get_user_model
from user_auth_app.api.serializers import CustomUserSerializer
from colors.api.serializers import ColorSerializer
from colors.models import Color
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
    class Meta:
        model = Subtask
        fields = ['id', 'name', 'is_completed']
        read_only_fields = ['id']

class TaskSerializer(serializers.ModelSerializer):
    workspace = serializers.PrimaryKeyRelatedField(read_only=True)  # Setzen in der View
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=True # Nur für Schreiboperationen
    )
    subtasks = SubtaskSerializer(many=True, required=False)
  
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'due_date', 'category', 'selected_contacts', 'status', 'workspace', 'subtasks', 'prio']
    
    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        task = Task.objects.create(**validated_data)
        for subtask_data in subtasks_data:
            Subtask.objects.create(task=task, **subtask_data)
        return task

    def update(self, instance, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
    # Aktualisiere die Task-Instanz
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    # Aktuelle Subtasks sammeln
        current_subtasks = {subtask.id: subtask for subtask in instance.subtasks.all()}

        for subtask_data in subtasks_data:
            subtask_id = subtask_data.get('id', None)
            if subtask_id:
            # Aktualisiere vorhandene Subtasks
                subtask = current_subtasks.pop(subtask_id, None)
                if subtask:
                    subtask.name = subtask_data.get('name', subtask.name)
                    subtask.is_completed = subtask_data.get('is_completed', subtask.is_completed)
                    subtask.save()
            else:
            # Erstelle neue Subtasks
                Subtask.objects.create(task=instance, **subtask_data)

    # Lösche Subtasks, die nicht im Update-Request enthalten sind
        for subtask in current_subtasks.values():
            subtask.delete()

        return instance

    
class CategorySerializer(serializers.ModelSerializer):
    workspace = serializers.PrimaryKeyRelatedField(read_only=True)
    color = ColorSerializer()
    class Meta:
        model = Category
        fields = ['id', 'name', 'workspace', 'color']
    
    def create(self, validated_data):
        color_data = validated_data.pop('color')
        color, created = Color.objects.get_or_create(**color_data)
        category = Category.objects.create(color=color, **validated_data)
        return category
        



