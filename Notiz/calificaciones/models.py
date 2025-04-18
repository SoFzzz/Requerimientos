# Create your models here.
from django.db import models
from usuarios.models import Usuario
from academico.models import Asignatura, Estudiante, CriterioEvaluacion, PeriodoAcademico

class Calificacion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='calificaciones')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    criterio = models.ForeignKey(CriterioEvaluacion, on_delete=models.CASCADE)
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE)
    valor = models.FloatField()
    observacion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    publicada = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.estudiante.usuario.username} - {self.asignatura.nombre} - {self.valor}"

class HistorialCambiosCalificacion(models.Model):
    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE, related_name='historial')
    valor_anterior = models.FloatField()
    valor_nuevo = models.FloatField()
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario_cambio = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    motivo = models.TextField()
    
    def __str__(self):
        return f"Cambio en {self.calificacion}: {self.valor_anterior} -> {self.valor_nuevo}"

class SolicitudCambioNota(models.Model):
    PENDIENTE = 'pendiente'
    APROBADA = 'aprobada'
    RECHAZADA = 'rechazada'
    
    ESTADO_CHOICES = [
        (PENDIENTE, 'Pendiente'),
        (APROBADA, 'Aprobada'),
        (RECHAZADA, 'Rechazada'),
    ]
    
    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_cambio')
    valor_propuesto = models.FloatField()
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=PENDIENTE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    admin_resolucion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='resoluciones_solicitudes')
    
    def __str__(self):
        return f"Solicitud de cambio para {self.calificacion}: {self.calificacion.valor} -> {self.valor_propuesto}"