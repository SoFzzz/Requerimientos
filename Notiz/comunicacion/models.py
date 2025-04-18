# Create your models here.
from django.db import models
from usuarios.models import Usuario

class Mensaje(models.Model):
    remitente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    asunto = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    
    def __str__(self):
        return f"De {self.remitente.username} para {self.destinatario.username}: {self.asunto}"

class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    enlace = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.titulo} para {self.usuario.username}"

class AnuncioGeneral(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    autor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    importante = models.BooleanField(default=False)
    
    def __str__(self):
        return self.titulo