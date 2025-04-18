from django.urls import path
from . import views

urlpatterns = [
    path('mensajes/', views.bandeja_entrada, name='bandeja_entrada'),
    path('mensajes/enviados/', views.mensajes_enviados, name='mensajes_enviados'),
    path('mensaje/nuevo/', views.nuevo_mensaje, name='nuevo_mensaje'),
    path('mensaje/<int:mensaje_id>/', views.ver_mensaje, name='ver_mensaje'),
    path('notificaciones/', views.mis_notificaciones, name='mis_notificaciones'),
    path('notificacion/leer/<int:notificacion_id>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('anuncios/', views.anuncios_generales, name='anuncios_generales'),
]