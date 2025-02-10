

from rest_framework import serializers
from colors.api.serializers import ColorSerializer
from colors.models import Color
from colors.api.serializers import ColorSerializer
from user_auth_app.models import CustomUser, Contact


class CustomUserSerializer(serializers.ModelSerializer):
    # Passwortfeld, um das Passwort korrekt zu validieren und zu verschlüsseln
    password = serializers.CharField(write_only=True)
    color = ColorSerializer(required=False)
    avatar = serializers.CharField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'password', 'color', 'avatar', 'phone']

    # Überschreibe die create-Methode, um das Passwort zu hashen
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Passwort wird gehasht
        user.save()
        return user
    
class ContactSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    color = ColorSerializer(required=False)
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'user', 'phone', 'avatar', 'color']
        
    