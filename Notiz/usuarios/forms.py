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


