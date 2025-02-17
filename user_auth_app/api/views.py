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
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

class CustomLoginView(APIView):
    @extend_schema(
        request={
            'username': OpenApiParameter("username", str, description="Username", required=True),
            'password': OpenApiParameter("password", str, description="Password", required=True),
        },
        responses={
            200: OpenApiResponse(
                description="Login successful",
                response=CustomUserSerializer  # Direkt auf den Serializer verweisen
            ),
            400: OpenApiResponse(description="Incorrect password"),
            404: OpenApiResponse(description="User does not exist"),
        }
    )
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user_obj = User.objects.get(email=username)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            send_mail(
            subject="Login Notification",
            message=f"Login successful",
            from_email="noreply@join.dogan-celik.com",
            recipient_list=["mail@dogan-celik.com"],
            )
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
        return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
    
    
class RegistrationView(APIView):
    authentication_classes = []
    @extend_schema(
        request=CustomUserSerializer,
        responses={
            201: OpenApiResponse(
                description="User successfully registered",
                response=CustomUserSerializer
            ),
            400: OpenApiResponse(description="Invalid user data")
        }
    )
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
    @extend_schema(
        request=OpenApiParameter("email", str, description="User's email address", required=True),
        responses={
            200: OpenApiResponse(description="Password reset link sent successfully"),
            400: OpenApiResponse(description="Email is required"),
            404: OpenApiResponse(description="User with this email does not exist")
        }
    )
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
        reset_link = f"https:/join.dogan-celik.com/reset-password/{uid}/{token}/"
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email="noreply@join.dogan-celik.com",
            recipient_list=[email],
        )
        return Response({"message": "Password reset link has been sent to your email"}, status=status.HTTP_200_OK)
    
    
class PasswordResetView(APIView):
    @extend_schema(
       parameters=[
            OpenApiParameter('uidb64', str, description='User ID encoded in base64', required=True),
            OpenApiParameter('token', str, description='Password reset token', required=True),
        ],
        responses={
            200: OpenApiResponse(description="Password reset successfully"),
            400: OpenApiResponse(description="Invalid UID or expired token")
        }
    )
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
    @extend_schema(
         request={
             
            'oldPassword': OpenApiParameter("oldPassword", str, description="Old password", required=True),
            'newPassword': OpenApiParameter("newPassword", str, description="New password", required=True)
        },
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Incorrect old password or missing new password")
        }
    )
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
    @extend_schema(
        request={
            "name": OpenApiParameter("name", str, description="User's name", required=True),
            "email": OpenApiParameter("email", str, description="User's email", required=True),
            "phone": OpenApiParameter("phone", str, description="User's phone number", required=False)
        },
        responses={
            200: OpenApiResponse(
                description="Profile updated successfully",
                response=CustomUserSerializer
            ),
            400: OpenApiResponse(description="Name and email are required"),
            404: OpenApiResponse(description="User not found"),
            400: OpenApiResponse(description="Email is already taken")
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
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
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="List of contacts",
                response=ContactSerializer(many=True)
            )
        }
    )
    def get_queryset(self):
        user = self.request.user
        return Contact.objects.filter(user=user)
    
   