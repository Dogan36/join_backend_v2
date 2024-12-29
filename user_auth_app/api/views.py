from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from user_auth_app.api.serializers import CustomUserSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth import get_user_model



class RegistrationView(APIView):
    """
    Registrierung eines neuen Benutzers
    """

    def post(self, request, *args, **kwargs):
        # Der Serializer für die Benutzerdaten
        serializer = CustomUserSerializer(data=request.data)

        # Überprüfen, ob die Daten validiert sind
        if serializer.is_valid():
            user = serializer.save()  # Benutzer wird erstellt

            # Token für den Benutzer erstellen
            token, created = Token.objects.get_or_create(user=user)

            # Rückgabe der Benutzerdaten und des Tokens
            return Response({
                'user': serializer.data,
                'token': token.key  # Das Token als Teil der Antwort
            }, status=status.HTTP_201_CREATED)
        
        # Wenn die Validierung fehlschlägt, gebe die Fehler zurück
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
        reset_link = f"http://frontend-url/reset-password/{uid}/{token}/"

        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email="noreply@example.com",
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