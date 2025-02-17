from rest_framework import viewsets
from colors.models import Color
from .serializers import ColorSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="List of colors",
                response= ColorSerializer(many=True)  # Array of colors returned
            ),
            400: OpenApiResponse(description="Bad Request")
        }
    )
    def list(self, request, *args, **kwargs):
        """
        List all colors available in the system.
        """
        return super().list(request, *args, **kwargs)