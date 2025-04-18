from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),  # Usaremos usuarios como app para la página principal
    path('academico/', include('academico.urls')),
    path('calificaciones/', include('calificaciones.urls')),
    path('comunicacion/', include('comunicacion.urls')),
    path('reportes/', include('reportes.urls')),
]