from django.urls import path

from . import views

urlpatterns = [
    path('chat', views.chatbot),    
    path("chatwapp", views.verify_whatsapp),
]
