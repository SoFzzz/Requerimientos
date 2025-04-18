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