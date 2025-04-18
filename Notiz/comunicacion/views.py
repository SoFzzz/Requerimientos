# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Mensaje, Notificacion, AnuncioGeneral
from .forms import MensajeForm, AnuncioForm
from usuarios.models import Usuario  # Ajusta según tu modelo de usuario real

@login_required
def bandeja_entrada(request):
    mensajes_recibidos = Mensaje.objects.filter(receptor=request.user)
    return render(request, 'comunicacion/bandeja_entrada.html', {
        'mensajes': mensajes_recibidos
    })

@login_required
def mensajes_enviados(request):
    mensajes_enviados = Mensaje.objects.filter(emisor=request.user)
    return render(request, 'comunicacion/mensajes_enviados.html', {
        'mensajes': mensajes_enviados
    })

@login_required
def nuevo_mensaje(request):
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.emisor = request.user
            mensaje.save()
            
            # Crear notificación para el receptor
            Notificacion.objects.create(
                usuario=mensaje.receptor,
                tipo='mensaje',
                titulo=f'Nuevo mensaje de {request.user.get_full_name() or request.user.username}',
                mensaje=f'Has recibido un nuevo mensaje: {mensaje.asunto}',
                enlace=f'/comunicacion/mensaje/{mensaje.id}/'
            )
            
            messages.success(request, 'Mensaje enviado correctamente')
            return redirect('bandeja_entrada')
    else:
        form = MensajeForm()
        
    # Filtrar usuarios según el rol del usuario actual
    usuarios_disponibles = None
    if request.user.is_staff:  # Administrador
        usuarios_disponibles = Usuario.objects.all()
    elif hasattr(request.user, 'es_profesor') and request.user.es_profesor:
        # Estudiantes de los cursos del profesor + todos los administradores
        # (Esta lógica dependerá de cómo están definidas tus relaciones)
        estudiantes = Usuario.objects.filter(es_estudiante=True)  # Ajusta según tu modelo
        admins = Usuario.objects.filter(is_staff=True)
        usuarios_disponibles = (estudiantes | admins).distinct()
    else:  # Estudiante
        # Profesores de sus cursos + administradores
        profesores = Usuario.objects.filter(es_profesor=True)  # Ajusta según tu modelo
        admins = Usuario.objects.filter(is_staff=True)
        usuarios_disponibles = (profesores | admins).distinct()
    
    return render(request, 'comunicacion/nuevo_mensaje.html', {
        'form': form,
        'usuarios': usuarios_disponibles
    })

@login_required
def ver_mensaje(request, mensaje_id):
    mensaje = get_object_or_404(Mensaje, id=mensaje_id)
    
    # Verificar que el usuario pueda ver este mensaje
    if request.user != mensaje.emisor and request.user != mensaje.receptor:
        messages.error(request, 'No tienes permiso para ver este mensaje')
        return redirect('bandeja_entrada')
    
    # Marcar como leído si es el receptor
    if request.user == mensaje.receptor and not mensaje.leido:
        mensaje.leido = True
        mensaje.save()
        
        # Marcar notificación relacionada como leída
        Notificacion.objects.filter(
            usuario=request.user,
            tipo='mensaje',
            enlace__contains=f'mensaje/{mensaje.id}/'
        ).update(leida=True)
    
    return render(request, 'comunicacion/ver_mensaje.html', {'mensaje': mensaje})

@login_required
def mis_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    return render(request, 'comunicacion/notificaciones.html', {
        'notificaciones': notificaciones
    })

@login_required
def marcar_notificacion_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.leida = True
    notificacion.save()
    return redirect('mis_notificaciones')

# Para administradores
@login_required
def anuncios_generales(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('home')
    
    anuncios = AnuncioGeneral.objects.all()
    
    if request.method == 'POST':
        form = AnuncioForm(request.POST)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.autor = request.user
            anuncio.save()
            
            # Notificar a todos los usuarios
            usuarios = Usuario.objects.all()
            for usuario in usuarios:
                Notificacion.objects.create(
                    usuario=usuario,
                    tipo='sistema',
                    titulo='Nuevo anuncio institucional',
                    mensaje=f'Se ha publicado un nuevo anuncio: {anuncio.titulo}',
                    enlace='/comunicacion/anuncios/'
                )
            
            messages.success(request, 'Anuncio publicado correctamente')
            return redirect('anuncios_generales')
    else:
        form = AnuncioForm()
    
    return render(request, 'comunicacion/anuncios.html', {
        'anuncios': anuncios,
        'form': form
    })