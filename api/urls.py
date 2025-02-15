
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('example.urls')),
    path('api/v1/', include('heii_apis.urls')),  # Incluir las rutas de la API
    path('chatbot/v1/', include('chatbot.urls')),
]
