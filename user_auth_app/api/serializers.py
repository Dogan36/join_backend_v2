from rest_framework import serializers
from user_auth_app.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    # Passwortfeld, um das Passwort korrekt zu validieren und zu verschlüsseln
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'password']

    # Überschreibe die create-Methode, um das Passwort zu hashen
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Passwort wird gehasht
        user.save()
        return user
    
