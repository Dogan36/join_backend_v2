from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from user_auth_app.api.serializers import CustomUserSerializer, ContactSerializer
from user_auth_app.models import Contact
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction


class CustomLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Überprüfe, ob ein Benutzer mit diesem Benutzernamen existiert.
        try:
            user_obj = User.objects.get(email=username)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Versuche, den Benutzer zu authentifizieren.
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'color': user.color.hex_value if hasattr(user, 'color') and user.color else None,
                    'avatar': user.avatar,
                    'phone': user.phone
                },
                'token': token.key
            }, status=status.HTTP_200_OK)

        # Falls die Authentifizierung fehlschlägt, liegt das Passwort falsch.
        return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
    
class RegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():  # Stellt sicher, dass alle Datenbankoperationen atomar ablaufen
                user = serializer.save()  # Benutzer wird erstellt

                # Token für den neuen User erstellen
                token, created = Token.objects.get_or_create(user=user)

                # Rückgabe der Benutzerdaten und des Tokens
                return Response({
                    'user': serializer.data,
                    'token': token.key
                }, status=status.HTTP_201_CREATED)
        
        # Bei fehlerhafter Validierung die Fehler zurückgeben
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"https:/localhost:5173/reset-password/{uid}/{token}/"

        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email="noreply@join.dogan-celik.com",
            recipient_list=[email],
        )
        return Response({"message": "Password reset link has been sent to your email"}, status=status.HTTP_200_OK)
    
    
class PasswordResetView(APIView):
    def post(self, request, uidb64, token):
        new_password = request.data.get('password')
        if not new_password:
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError):
            return Response({"error": "Invalid UID"}, status=status.HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user  # Annahme: der Benutzer ist authentifiziert (z.B. über TokenAuthentication)
        old_password = request.data.get('oldPassword')
        new_password = request.data.get('newPassword')

        if not old_password or not new_password:
            return Response({"error": "Both old and new passwords are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Überprüfe, ob das alte Passwort korrekt ist
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        # Setze das neue Passwort
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Hole die Felder aus den Request-Daten
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')

        existing_user = User.objects.filter(email=email).exclude(pk=user.pk).first()
        if existing_user:
            return Response(
                {"error": "email_taken"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not name or not email:
            return Response(
                {"error": "Name and email are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Aktualisiere die Felder
        user.name = name
        user.email = email
        user.phone = phone 
        
        user.save()

        return Response(
            {
                "message": "Profile updated successfully.",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "color": user.color.hex_value if hasattr(user, 'color') and user.color else None,
                    "avatar": user.avatar
                }
            },
            status=status.HTTP_200_OK
        )
   
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Contact.objects.filter(user=user)
    
   