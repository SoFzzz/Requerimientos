# academico/models.py
from django.db import models
from usuarios.models import Usuario

class Institucion(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    escala_minima = models.FloatField(default=0.0)
    escala_maxima = models.FloatField(default=5.0)
    nota_aprobacion = models.FloatField(default=3.0)
    
    def __str__(self):
        return self.nombre

class PeriodoAcademico(models.Model):
    TRIMESTRE = 'trimestre'
    SEMESTRE = 'semestre'
    ANUAL = 'anual'
    
    TIPO_CHOICES = [
        (TRIMESTRE, 'Trimestre'),
        (SEMESTRE, 'Semestre'),
        (ANUAL, 'Anual'),
    ]
    
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()}) - {self.institucion.nombre}"

class Curso(models.Model):
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class Asignatura(models.Model):
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='asignaturas')
    profesor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'profesor'})
    
    def __str__(self):
        return f"{self.nombre} - {self.curso.nombre}"

class CriterioEvaluacion(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='criterios')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    ponderacion = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def __str__(self):
        return f"{self.nombre} - {self.asignatura.nombre} ({self.ponderacion}%)"

class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='estudiante')
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True, related_name='estudiantes')
    numero_identificacion = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    padres = models.ManyToManyField('usuarios.Padre', related_name='hijos', blank=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.curso.nombre if self.curso else 'Sin curso'}"

