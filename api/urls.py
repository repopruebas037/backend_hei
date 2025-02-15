
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('example.urls')),
    path('chatbot/v1/', include('chatbot.urls')),
]
