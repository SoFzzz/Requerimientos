# ya pondre algo aqui
from django import forms
from .models import Calificacion, SolicitudCambioNota
from academico.models import Asignatura, CriterioEvaluacion, PeriodoAcademico

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['estudiante', 'asignatura', 'criterio', 'periodo', 'valor', 'observacion']
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CalificacionMasivaForm(forms.Form):
    archivo = forms.FileField(
        label="Archivo Excel/CSV de calificaciones",
        help_text="El archivo debe tener las columnas: ID_Estudiante, Valor, Observacion (opcional)"
    )
    asignatura = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    criterio = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    periodo = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        profesor = kwargs.pop('profesor', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar asignaturas por profesor si se proporciona
        if profesor:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(profesor=profesor)
        else:
            self.fields['asignatura'].queryset = Asignatura.objects.all()
            
        # Inicialmente el criterio está vacío, se llenará con JavaScript cuando se seleccione una asignatura
        self.fields['criterio'].queryset = CriterioEvaluacion.objects.none()
        
        # Mostrar solo periodos activos
        self.fields['periodo'].queryset = PeriodoAcademico.objects.filter(activo=True)
    
    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        extension = archivo.name.split('.')[-1].lower()
        
        if extension not in ['xls', 'xlsx', 'csv']:
            raise forms.ValidationError("Formato de archivo no soportado. Use Excel (.xls, .xlsx) o CSV.")
        
        # La validación detallada del contenido del archivo se hará en la vista
        # para evitar problemas con la carga de pandas
        return archivo

class SolicitudCambioNotaForm(forms.ModelForm):
    class Meta:
        model = SolicitudCambioNota
        fields = ['calificacion', 'valor_propuesto', 'motivo']
        widgets = {
            'valor_propuesto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class AprobacionSolicitudForm(forms.Form):
    decision = forms.ChoiceField(
        choices=[('aprobar', 'Aprobar Solicitud'), ('rechazar', 'Rechazar Solicitud')],
        widget=forms.RadioSelect
    )
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )