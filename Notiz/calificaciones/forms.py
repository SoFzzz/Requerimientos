from django import forms
from .models import Calificacion, SolicitudCambioNota
import pandas as pd

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
    asignatura = forms.ModelChoiceField(queryset=None)
    criterio = forms.ModelChoiceField(queryset=None)
    periodo = forms.ModelChoiceField(queryset=None)
    
    def __init__(self, *args, **kwargs):
        profesor = kwargs.pop('profesor', None)
        super().__init__(*args, **kwargs)
        
        from academico.models import Asignatura, CriterioEvaluacion, PeriodoAcademico
        
        # Filtrar asignaturas por profesor si se proporciona
        if profesor:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(profesor=profesor)
        else:
            self.fields['asignatura'].queryset = Asignatura.objects.all()
            
        self.fields['criterio'].queryset = CriterioEvaluacion.objects.none()
        self.fields['periodo'].queryset = PeriodoAcademico.objects.filter(activo=True)
    
    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        extension = archivo.name.split('.')[-1].lower()
        
        if extension not in ['xls', 'xlsx', 'csv']:
            raise forms.ValidationError("Formato de archivo no soportado. Use Excel (.xls, .xlsx) o CSV.")
        
        try:
            # Leer el archivo según su formato
            if extension == 'csv':
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            # Verificar las columnas necesarias
            if 'ID_Estudiante' not in df.columns or 'Valor' not in df.columns:
                raise forms.ValidationError("El archivo debe contener las columnas 'ID_Estudiante' y 'Valor'.")
            
            # Verificar que los valores sean numéricos
            if not pd.to_numeric(df['Valor'], errors='coerce').notnull().all():
                raise forms.ValidationError("La columna 'Valor' debe contener solo valores numéricos.")
                
            return archivo
            
        except Exception as e:
            raise forms.ValidationError(f"Error al procesar el archivo: {str(e)}")

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