from django import forms
from academico.models import Curso, Asignatura, PeriodoAcademico, Estudiante

class ReporteIndividualForm(forms.Form):
    estudiante = forms.ModelChoiceField(
        queryset=Estudiante.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    periodo = forms.ModelChoiceField(
        queryset=PeriodoAcademico.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ReporteGrupalForm(forms.Form):
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    periodo = forms.ModelChoiceField(
        queryset=PeriodoAcademico.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )