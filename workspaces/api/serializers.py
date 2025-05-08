from rest_framework import serializers
from ..models import Workspace, Category, Task, Subtask
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
    selected_contacts = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )
    subtasks = SubtaskSerializer(many=True, required=False)
  
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'due_date', 'category', 'selected_contacts', 'status', 'workspace', 'subtasks', 'prio']
    
    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        selected_contacts = validated_data.pop('selected_contacts', None)
        
        task = Task.objects.create(**validated_data)
        for subtask_data in subtasks_data:
            Subtask.objects.create(task=task, **subtask_data)
        if selected_contacts:
            task.selected_contacts.set(selected_contacts)
        return task

    def update(self, instance, validated_data):
    subtasks_data = validated_data.pop('subtasks', None)
    selected_contacts = validated_data.pop('selected_contacts', None)

    # Aktualisiere alle anderen Felder des Tasks
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()

    # Aktualisiere die Many-to-Many-Beziehung
    if selected_contacts is not None:
        instance.selected_contacts.set(selected_contacts)

    if subtasks_data is not None:
        # Bestehende Subtasks in einem Dictionary sammeln (Key: subtask.id)
        current_subtasks = {subtask.id: subtask for subtask in instance.subtasks.all()}
        incoming_ids = []

        for subtask_data in subtasks_data:
            subtask_id = subtask_data.get('id')
            if subtask_id and subtask_id in current_subtasks:
                # Bestehendes Subtask updaten
                subtask = current_subtasks[subtask_id]
                for attr, value in subtask_data.items():
                    setattr(subtask, attr, value)
                subtask.save()
                incoming_ids.append(subtask_id)
            else:
                # Neues Subtask anlegen
                Subtask.objects.create(task=instance, **subtask_data)

        # Lösche Subtasks, die nicht mehr in den neuen Daten vorkommen
        for subtask_id, subtask in current_subtasks.items():
            if subtask_id not in incoming_ids:
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
        
        
class InviteEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    join_code = serializers.CharField(required=True)



