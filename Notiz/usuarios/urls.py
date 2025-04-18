from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.index, name='index'),  # Página de inicio
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
]