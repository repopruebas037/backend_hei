
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hello.urls')),
    path('api/v1/', include('heii_apis.urls')),  
    path('chatbot/v1/', include('chatbot.urls')),
    
]
