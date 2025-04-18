# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import user_passes_test
from .models import Usuario
from .forms import LoginForm, RegistroForm, PerfilForm, CambiarPasswordForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.bloqueado:
                    messages.error(request, 'Su cuenta está bloqueada. Contacte al administrador.')
                    return render(request, 'usuarios/login.html', {'form': form})
                
                # Verificación de dos pasos
                if user.autenticacion_dos_pasos:
                    # Generar código y enviarlo por correo
                    codigo = get_random_string(length=6, allowed_chars='0123456789')
                    request.session['codigo_verificacion'] = codigo
                    request.session['user_id_temp'] = user.id
                    
                    send_mail(
                        'Código de verificación',
                        f'Su código de verificación es: {codigo}',
                        'no-reply@sistema-notas.com',
                        [user.email],
                        fail_silently=False,
                    )
                    
                    return redirect('verificar_codigo')
                else:
                    # Sin verificación de dos pasos, acceso directo
                    login(request, user)
                    user.intentos_fallidos = 0
                    user.save()
                    return redirect('dashboard')
            else:
                # Buscar usuario por nombre para incrementar intentos fallidos
                try:
                    user = Usuario.objects.get(username=username)
                    user.intentos_fallidos += 1
                    if user.intentos_fallidos >= 5:
                        user.bloqueado = True
                        messages.error(request, 'Su cuenta ha sido bloqueada después de múltiples intentos fallidos.')
                    user.save()
                except Usuario.DoesNotExist:
                    pass
                    
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def verificar_codigo(request):
    if 'codigo_verificacion' not in request.session or 'user_id_temp' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        if codigo_ingresado == request.session['codigo_verificacion']:
            # Código correcto
            user_id = request.session['user_id_temp']
            user = Usuario.objects.get(id=user_id)
            login(request, user)
            
            # Limpiar sesión
            del request.session['codigo_verificacion']
            del request.session['user_id_temp']
            
            user.intentos_fallidos = 0
            user.save()
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Código incorrecto. Intente nuevamente.')
            
    return render(request, 'usuarios/verificar_codigo.html')

def recuperar_password(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        try:
            user = Usuario.objects.get(email=correo)
            # Generar token para reseteo
            token = get_random_string(length=32)
            user.password_reset_token = token
            user.save()
            
            # Enviar correo con link para resetear
            reset_url = f"{request.scheme}://{request.get_host()}/usuarios/reset-password/{token}/"
            send_mail(
                'Recuperación de contraseña',
                f'Para restablecer su contraseña, haga clic en el siguiente enlace: {reset_url}',
                'no-reply@sistema-notas.com',
                [correo],
                fail_silently=False,
            )
            
            messages.success(request, 'Se ha enviado un correo con instrucciones para recuperar su contraseña.')
            return redirect('login')
        except Usuario.DoesNotExist:
            messages.error(request, 'No existe un usuario con ese correo electrónico.')
    
    return render(request, 'usuarios/recuperar_password.html')

def reset_password(request, token):
    try:
        user = Usuario.objects.get(password_reset_token=token)
    except Usuario.DoesNotExist:
        messages.error(request, 'Token inválido o expirado.')
        return redirect('login')
        
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
        else:
            user.set_password(password)
            user.password_reset_token = None
            user.save()
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('login')
    
    return render(request, 'usuarios/reset_password.html')

@login_required
def cambiar_password(request):
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            password_actual = form.cleaned_data.get('password_actual')
            password_nuevo = form.cleaned_data.get('password_nuevo')
            
            if not request.user.check_password(password_actual):
                messages.error(request, 'La contraseña actual es incorrecta.')
            else:
                request.user.set_password(password_nuevo)
                request.user.save()
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('perfil')
    else:
        form = CambiarPasswordForm()
        
    return render(request, 'usuarios/cambiar_password.html', {'form': form})

@login_required
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=request.user)
        
    return render(request, 'usuarios/perfil.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.rol == Usuario.ESTUDIANTE:
        return redirect('dashboard_estudiante')
    elif request.user.rol == Usuario.PROFESOR:
        return redirect('dashboard_profesor')
    elif request.user.rol == Usuario.ADMIN:
        return redirect('dashboard_admin')
    else:
        return redirect('dashboard_padre')

# Función para verificar si el usuario es administrador
def es_admin(user):
    return user.is_authenticated and user.rol == Usuario.ADMIN

# Función para verificar si el usuario es profesor
def es_profesor(user):
    return user.is_authenticated and user.rol == Usuario.PROFESOR

# Función para verificar si el usuario es estudiante
def es_estudiante(user):
    return user.is_authenticated and user.rol == Usuario.ESTUDIANTE

@login_required
@user_passes_test(es_estudiante)
def dashboard_estudiante(request):
    # Lógica para el dashboard del estudiante
    return render(request, 'usuarios/dashboard_estudiante.html')

@login_required
@user_passes_test(es_profesor)
def dashboard_profesor(request):
    # Lógica para el dashboard del profesor
    return render(request, 'usuarios/dashboard_profesor.html')

@login_required
@user_passes_test(es_admin)
def dashboard_admin(request):
    # Lógica para el dashboard del administrador
    return render(request, 'usuarios/dashboard_admin.html')