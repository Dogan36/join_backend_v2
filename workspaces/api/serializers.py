from rest_framework import serializers
from workspaces.models import Workspace
from django.contrib.auth import get_user_model
from user_auth_app.api.serializers import CustomUserSerializer
User = get_user_model()

class WorkspaceSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    owner = CustomUserSerializer(read_only=True)
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