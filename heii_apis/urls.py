from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register_restaurant),
    path('login', views.login_restaurant),
    path('orders',views.create_order) ,
    path('products',views.create_product)
]
