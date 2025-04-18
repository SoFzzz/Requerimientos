# Create your models here
from django.db import models
from usuarios.models import Usuario
from academico.models import Curso, Asignatura, PeriodoAcademico, Estudiante

class Reporte(models.Model):
    INDIVIDUAL = 'individual'
    GRUPAL = 'grupal'
    
    TIPO_CHOICES = [
        (INDIVIDUAL, 'Individual'),
        (GRUPAL, 'Grupal'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    generado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    archivo_pdf = models.FileField(upload_to='reportes/', null=True, blank=True)
    
    # Filtros
    estudiante = models.ForeignKey(Estudiante, on_delete=models.SET_NULL, null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True, blank=True)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.SET_NULL, null=True, blank=True)
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        if self.tipo == self.INDIVIDUAL:
            return f"Reporte individual: {self.estudiante.usuario.username} - {self.periodo.nombre}"
        return f"Reporte grupal: {self.curso.nombre} - {self.periodo.nombre}"

