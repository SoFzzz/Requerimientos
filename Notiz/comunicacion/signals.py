# comunicacion/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from calificaciones.models import Calificacion  # Ajusta según tus modelos
from .models import Notificacion

@receiver(post_save, sender=Calificacion)
def notificar_nueva_calificacion(sender, instance, created, **kwargs):
    """Envía notificación al estudiante cuando se registra una nueva calificación"""
    if created:
        estudiante = instance.estudiante  # Ajusta según tus modelos
        Notificacion.objects.create(
            usuario=estudiante,
            tipo='calificacion',
            titulo=f'Nueva calificación registrada',
            mensaje=f'Se ha registrado una nueva calificación en {instance.curso}',
            enlace=f'/calificaciones/mis-calificaciones/'
        )
        
        # Si el estudiante tiene padres vinculados
        if hasattr(estudiante, 'padres'):
            for padre in estudiante.padres.all():  # Ajusta según tus modelos
                Notificacion.objects.create(
                    usuario=padre,
                    tipo='calificacion',
                    titulo=f'Nueva calificación para {estudiante.get_full_name()}',
                    mensaje=f'Se ha registrado una nueva calificación para {estudiante.get_full_name()} en {instance.curso}',
                    enlace=f'/calificaciones/estudiante/{estudiante.id}/'
                )