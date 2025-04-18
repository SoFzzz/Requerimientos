# academico/forms.py
from django import forms
from .models import Institucion, PeriodoAcademico, Curso, Asignatura, CriterioEvaluacion, Estudiante

class InstitucionForm(forms.ModelForm):
    class Meta:
        model = Institucion
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'escala_minima': forms.NumberInput(attrs={'class': 'form-control'}),
            'escala_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'nota_aprobacion': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PeriodoAcademicoForm(forms.ModelForm):
    class Meta:
        model = PeriodoAcademico
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CriterioEvaluacionForm(forms.ModelForm):
    class Meta:
        model = CriterioEvaluacion
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ponderacion': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ('curso', 'numero_identificacion', 'fecha_nacimiento')
        widgets = {
            'numero_identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
