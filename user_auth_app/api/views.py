from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from user_auth_app.api.serializers import CustomUserSerializer

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