from django.urls import path

from . import views

urlpatterns = [
    path('chat', views.chatbot),
    path('saveprompt', views.save_prompt),    
    path("chatwapp", views.verify_whatsapp),
]
