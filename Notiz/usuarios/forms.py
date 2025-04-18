# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Usuario', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegistroForm(UserCreationForm):
    correo_institucional = forms.EmailField(max_length=254, required=True, help_text='Requerido. Ingrese un correo institucional válido.')
    
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'correo_institucional', 'password1', 'password2', 'rol')
        
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email')
        
class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(label='Contraseña actual', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_nuevo = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirmacion = forms.CharField(label='Confirmar nueva contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        password_nuevo = cleaned_data.get('password_nuevo')
        password_confirmacion = cleaned_data.get('password_confirmacion')
        
        if password_nuevo and password_confirmacion:
            if password_nuevo != password_confirmacion:
                raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data

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

# calificaciones/forms.py
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

# reportes/forms.py
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

# comunicacion/forms.py
from django import forms
from .models import Mensaje, AnuncioGeneral
from usuarios.models import Usuario

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['destinatario', 'asunto', 'contenido']
        widgets = {
            'asunto': forms.TextInput(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        usuario_actual = kwargs.pop('usuario_actual', None)
        super().__init__(*args, **kwargs)
        
        # Limitar destinatarios según el rol del usuario actual
        if usuario_actual:
            if usuario_actual.rol == Usuario.ESTUDIANTE:
                # Estudiantes solo pueden enviar mensajes a sus profesores
                self.fields['destinatario'].queryset = Usuario.objects.filter(
                    rol=Usuario.PROFESOR
                )
            elif usuario_actual.rol == Usuario.PROFESOR:
                # Profesores pueden enviar a estudiantes y administradores
                self.fields['destinatario'].queryset = Usuario.objects.filter(
                    rol__in=[Usuario.ESTUDIANTE, Usuario.ADMIN]
                )
            elif usuario_actual.rol == Usuario.ADMIN:
                # Administradores pueden enviar a cualquiera
                self.fields['destinatario'].queryset = Usuario.objects.exclude(id=usuario_actual.id)

class AnuncioGeneralForm(forms.ModelForm):
    class Meta:
        model = AnuncioGeneral
        fields = ['titulo', 'contenido', 'importante']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }