
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
def home_view(request):
    return JsonResponse({"message": "Welcome to Join Backend API"})

urlpatterns = [
    path('', home_view),  # Füge eine Root-Route hinzu
    path('admin/', admin.site.urls),
    path('api/v1/user/', include('user_auth_app.api.urls')),
    path('api/v1/workspaces/', include('workspaces.api.urls')),
    path('api/v1/colors/', include('colors.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

]
