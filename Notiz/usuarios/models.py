# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Usuario(AbstractUser):
    ADMIN = 'admin'
    PROFESOR = 'profesor'
    ESTUDIANTE = 'estudiante'
    PADRE = 'padre'
    
    ROL_CHOICES = [
        (ADMIN, 'Administrador'),
        (PROFESOR, 'Profesor'),
        (ESTUDIANTE, 'Estudiante'),
        (PADRE, 'Padre/Madre'),
    ]
    
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ESTUDIANTE)
    correo_institucional = models.EmailField(unique=True)
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado = models.BooleanField(default=False)
    autenticacion_dos_pasos = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"

class Padre(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='padre')
    correo_contacto = models.EmailField()
    
    def __str__(self):
        return f"Padre/Madre: {self.usuario.username}"







