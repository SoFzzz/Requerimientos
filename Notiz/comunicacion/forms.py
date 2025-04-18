from django import forms
from .models import Mensaje, AnuncioGeneral
from usuarios.models import Usuario  # Ajusta según tu modelo de usuario

class MensajeForm(forms.ModelForm):
    receptor = forms.ModelChoiceField(
        queryset=Usuario.objects.all(),
        label='Destinatario'
    )
    
    class Meta:
        model = Mensaje
        fields = ['receptor', 'asunto', 'contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 5}),
        }

class AnuncioForm(forms.ModelForm):
    class Meta:
        model = AnuncioGeneral
        fields = ['titulo', 'contenido', 'visible']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 5}),
        }