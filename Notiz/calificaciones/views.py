from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from usuarios.models import Usuario
from academico.models import Asignatura, CriterioEvaluacion, PeriodoAcademico, Estudiante
from .models import Calificacion, HistorialCambiosCalificacion, SolicitudCambioNota
from .forms import CalificacionForm, CalificacionMasivaForm, SolicitudCambioNotaForm, AprobacionSolicitudForm

# Función para verificar si el usuario es profesor
def es_profesor(user):
    return user.is_authenticated and user.rol == Usuario.PROFESOR

# Función para verificar si el usuario es administrador
def es_admin(user):
    return user.is_authenticated and user.rol == Usuario.ADMIN

@login_required
@user_passes_test(es_profesor)
def listar_asignaturas(request):
    """Muestra las asignaturas asignadas al profesor actual"""
    asignaturas = Asignatura.objects.filter(profesor=request.user)
    return render(request, 'calificaciones/listar_asignaturas.html', {'asignaturas': asignaturas})

@login_required
@user_passes_test(es_profesor)
def listar_estudiantes_asignatura(request, asignatura_id):
    """Muestra la lista de estudiantes para una asignatura específica"""
    asignatura = get_object_or_404(Asignatura, id=asignatura_id, profesor=request.user)
    estudiantes = Estudiante.objects.filter(curso=asignatura.curso)
    
    # Obtener el periodo académico activo
    periodo_activo = PeriodoAcademico.objects.filter(activo=True).first()
    
    # Obtener criterios de evaluación para esta asignatura
    criterios = CriterioEvaluacion.objects.filter(asignatura=asignatura)
    
    # Para cada estudiante, obtener sus calificaciones en esta asignatura
    estudiantes_con_calificaciones = []
    for estudiante in estudiantes:
        calificaciones = {}
        for criterio in criterios:
            try:
                calificacion = Calificacion.objects.get(
                    estudiante=estudiante,
                    asignatura=asignatura,
                    criterio=criterio,
                    periodo=periodo_activo
                )
                calificaciones[criterio.id] = calificacion
            except Calificacion.DoesNotExist:
                calificaciones[criterio.id] = None
        
        estudiantes_con_calificaciones.append({
            'estudiante': estudiante,
            'calificaciones': calificaciones
        })
    
    return render(request, 'calificaciones/listar_estudiantes.html', {
        'asignatura': asignatura,
        'estudiantes': estudiantes_con_calificaciones,
        'criterios': criterios,
        'periodo': periodo_activo
    })

@login_required
@user_passes_test(es_profesor)
def registrar_calificacion(request, estudiante_id, asignatura_id):
    """Permite al profesor registrar una calificación individual"""
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    asignatura = get_object_or_404(Asignatura, id=asignatura_id, profesor=request.user)
    periodo_activo = PeriodoAcademico.objects.filter(activo=True).first()
    
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.estudiante = estudiante
            calificacion.asignatura = asignatura
            calificacion.periodo = periodo_activo
            
            # Verificar si ya existe una calificación para este criterio
            criterio = form.cleaned_data['criterio']
            try:
                calificacion_existente = Calificacion.objects.get(
                    estudiante=estudiante,
                    asignatura=asignatura,
                    criterio=criterio,
                    periodo=periodo_activo
                )
                # Si existe, actualizar en lugar de crear
                calificacion_existente.valor = calificacion.valor
                calificacion_existente.observacion = calificacion.observacion
                calificacion_existente.save()
                messages.success(request, f'Calificación actualizada para {estudiante.usuario.get_full_name()}')
            except Calificacion.DoesNotExist:
                # Si no existe, crear nueva
                calificacion.save()
                messages.success(request, f'Calificación registrada para {estudiante.usuario.get_full_name()}')
                
            return redirect('listar_estudiantes_asignatura', asignatura_id=asignatura.id)
    else:
        form = CalificacionForm(initial={
            'estudiante': estudiante,
            'asignatura': asignatura,
            'periodo': periodo_activo
        })
        
    # Filtrar criterios por asignatura
    form.fields['criterio'].queryset = CriterioEvaluacion.objects.filter(asignatura=asignatura)
    
    return render(request, 'calificaciones/registrar_calificacion.html', {
        'form': form,
        'estudiante': estudiante,
        'asignatura': asignatura
    })

@login_required
@user_passes_test(es_profesor)
def cargar_calificaciones_masivas(request):
    """Permite al profesor cargar calificaciones de forma masiva mediante un archivo Excel/CSV"""
    if request.method == 'POST':
        form = CalificacionMasivaForm(request.POST, request.FILES, profesor=request.user)
        if form.is_valid():
            archivo = request.FILES['archivo']
            asignatura = form.cleaned_data['asignatura']
            criterio = form.cleaned_data['criterio']
            periodo = form.cleaned_data['periodo']
            
            # Leer archivo según formato
            extension = archivo.name.split('.')[-1].lower()
            if extension == 'csv':
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
                
            # Procesar datos y registrar calificaciones
            with transaction.atomic():
                calificaciones_creadas = 0
                calificaciones_actualizadas = 0
                
                for _, fila in df.iterrows():
                    id_estudiante = str(fila['ID_Estudiante'])
                    valor = float(fila['Valor'])
                    observacion = fila.get('Observacion', None) if 'Observacion' in df.columns else None
                    
                    try:
                        estudiante = Estudiante.objects.get(numero_identificacion=id_estudiante)
                        
                        # Verificar si ya existe una calificación
                        try:
                            calificacion = Calificacion.objects.get(
                                estudiante=estudiante,
                                asignatura=asignatura,
                                criterio=criterio,
                                periodo=periodo
                            )
                            # Actualizar calificación existente
                            calificacion.valor = valor
                            if observacion:
                                calificacion.observacion = observacion
                            calificacion.save()
                            calificaciones_actualizadas += 1
                        except Calificacion.DoesNotExist:
                            # Crear nueva calificación
                            Calificacion.objects.create(
                                estudiante=estudiante,
                                asignatura=asignatura,
                                criterio=criterio,
                                periodo=periodo,
                                valor=valor,
                                observacion=observacion
                            )
                            calificaciones_creadas += 1
                    except Estudiante.DoesNotExist:
                        # Registrar error para este estudiante
                        pass
            
            messages.success(
                request, 
                f'Proceso completado: {calificaciones_creadas} calificaciones creadas, '
                f'{calificaciones_actualizadas} actualizadas.'
            )
            return redirect('listar_asignaturas')
    else:
        form = CalificacionMasivaForm(profesor=request.user)
    
    return render(request, 'calificaciones/cargar_calificaciones_masivas.html', {'form': form})

@login_required
@user_passes_test(es_profesor)
def publicar_calificaciones(request, asignatura_id, criterio_id):
    """Publica las calificaciones para que sean visibles por los estudiantes"""
    asignatura = get_object_or_404(Asignatura, id=asignatura_id, profesor=request.user)
    criterio = get_object_or_404(CriterioEvaluacion, id=criterio_id, asignatura=asignatura)
    periodo_activo = PeriodoAcademico.objects.filter(activo=True).first()
    
    # Marcar todas las calificaciones como publicadas
    calificaciones = Calificacion.objects.filter(
        asignatura=asignatura,
        criterio=criterio,
        periodo=periodo_activo,
        publicada=False
    )
    
    for calificacion in calificaciones:
        calificacion.publicada = True
        calificacion.fecha_publicacion = timezone.now()
        calificacion.save()
        
        # Enviar notificación al estudiante
        from comunicacion.models import Notificacion
        Notificacion.objects.create(
            usuario=calificacion.estudiante.usuario,
            titulo=f'Nueva calificación en {asignatura.nombre}',
            mensaje=f'Se ha publicado tu calificación para {criterio.nombre} en {asignatura.nombre}.',
            enlace='/estudiante/calificaciones/'
        )
    
    messages.success(request, f'Se han publicado {calificaciones.count()} calificaciones')
    return redirect('listar_estudiantes_asignatura', asignatura_id=asignatura.id)

@login_required
@user_passes_test(es_profesor)
def solicitar_cambio_nota(request, calificacion_id):
    """Permite al profesor solicitar un cambio de nota"""
    calificacion = get_object_or_404(Calificacion, id=calificacion_id, asignatura__profesor=request.user)
    
    if request.method == 'POST':
        form = SolicitudCambioNotaForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.calificacion = calificacion
            solicitud.profesor = request.user
            solicitud.save()
            
            messages.success(request, 'Solicitud de cambio de nota enviada correctamente.')
            return redirect('listar_estudiantes_asignatura', asignatura_id=calificacion.asignatura.id)
    else:
        form = SolicitudCambioNotaForm(initial={
            'calificacion': calificacion,
            'valor_propuesto': calificacion.valor
        })
        
    return render(request, 'calificaciones/solicitar_cambio_nota.html', {
        'form': form,
        'calificacion': calificacion
    })

@login_required
@user_passes_test(es_admin)
def listar_solicitudes_cambio(request):
    """Muestra al administrador todas las solicitudes de cambio de nota pendientes"""
    solicitudes = SolicitudCambioNota.objects.filter(estado=SolicitudCambioNota.PENDIENTE)
    return render(request, 'calificaciones/listar_solicitudes.html', {'solicitudes': solicitudes})

@login_required
@user_passes_test(es_admin)
def resolver_solicitud_cambio(request, solicitud_id):
    """Permite al administrador aprobar o rechazar una solicitud de cambio de nota"""
    solicitud = get_object_or_404(SolicitudCambioNota, id=solicitud_id, estado=SolicitudCambioNota.PENDIENTE)
    
    if request.method == 'POST':
        form = AprobacionSolicitudForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            comentario = form.cleaned_data['comentario']
            
            if decision == 'aprobar':
                # Registrar en historial
                HistorialCambiosCalificacion.objects.create(
                    calificacion=solicitud.calificacion,
                    valor_anterior=solicitud.calificacion.valor,
                    valor_nuevo=solicitud.valor_propuesto,
                    usuario_cambio=request.user,
                    motivo=f"Solicitud aprobada: {solicitud.motivo}"
                )
                
                # Actualizar calificación
                solicitud.calificacion.valor = solicitud.valor_propuesto
                solicitud.calificacion.save()
                
                # Actualizar solicitud
                solicitud.estado = SolicitudCambioNota.APROBADA
                solicitud.fecha_resolucion = timezone.now()
                solicitud.admin_resolucion = request.user
                solicitud.save()
                
                messages.success(request, 'Solicitud aprobada correctamente.')
            else:
                # Rechazar solicitud
                solicitud.estado = SolicitudCambioNota.RECHAZADA
                solicitud.fecha_resolucion = timezone.now()
                solicitud.admin_resolucion = request.user
                solicitud.save()
                
                messages.info(request, 'Solicitud rechazada.')
                
            # Notificar al profesor
            from comunicacion.models import Notificacion
            Notificacion.objects.create(
                usuario=solicitud.profesor,
                titulo=f'Resolución de solicitud de cambio de nota',
                mensaje=f'Su solicitud de cambio de nota para {solicitud.calificacion.estudiante.usuario.get_full_name()} '
                        f'ha sido {"aprobada" if decision == "aprobar" else "rechazada"}. '
                        f'{comentario if comentario else ""}',
                enlace='/profesor/solicitudes/'
            )
                
            return redirect('listar_solicitudes_cambio')
    else:
        form = AprobacionSolicitudForm()
        
    return render(request, 'calificaciones/resolver_solicitud.html', {
        'form': form,
        'solicitud': solicitud
    })

# Vista para estudiantes
@login_required
def ver_calificaciones_estudiante(request):
    """Permite al estudiante ver sus calificaciones publicadas"""
    # Verificar que el usuario es un estudiante
    if request.user.rol != Usuario.ESTUDIANTE:
        messages.error(request, "No tiene permiso para acceder a esta página.")
        return redirect('dashboard')
        
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
    except Estudiante.DoesNotExist:
        messages.error(request, "No se encontró información de estudiante asociada a su cuenta.")
        return redirect('dashboard')
    
    # Obtener periodo académico activo
    periodo_activo = PeriodoAcademico.objects.filter(activo=True).first()
    
    # Obtener todas las asignaturas del curso del estudiante
    asignaturas = Asignatura.objects.filter(curso=estudiante.curso)
    
    # Obtener calificaciones publicadas del estudiante
    calificaciones_por_asignatura = {}
    for asignatura in asignaturas:
        criterios = CriterioEvaluacion.objects.filter(asignatura=asignatura)
        
        calificaciones = []
        total_ponderado = 0
        suma_ponderaciones = 0
        
        for criterio in criterios:
            try:
                calificacion = Calificacion.objects.get(
                    estudiante=estudiante,
                    asignatura=asignatura,
                    criterio=criterio,
                    periodo=periodo_activo,
                    publicada=True
                )
                calificaciones.append({
                    'criterio': criterio,
                    'valor': calificacion.valor,
                    'observacion': calificacion.observacion,
                    'fecha_publicacion': calificacion.fecha_publicacion
                })
                
                # Calcular valor ponderado
                total_ponderado += calificacion.valor * (criterio.ponderacion / 100)
                suma_ponderaciones += criterio.ponderacion
            except Calificacion.DoesNotExist:
                calificaciones.append({
                    'criterio': criterio,
                    'valor': None,
                    'observacion': None,
                    'fecha_publicacion': None
                })
        
        # Calcular promedio si hay calificaciones
        promedio = None
        if suma_ponderaciones > 0:
            promedio = total_ponderado / (suma_ponderaciones / 100)
        
        calificaciones_por_asignatura[asignatura] = {
            'calificaciones': calificaciones,
            'promedio': promedio
        }
    
    return render(request, 'calificaciones/ver_calificaciones_estudiante.html', {
        'estudiante': estudiante,
        'periodo': periodo_activo,
        'calificaciones_por_asignatura': calificaciones_por_asignatura
    })

@login_required
def descargar_boletin(request):
    """Permite al estudiante descargar un boletín de calificaciones en PDF"""
    # Verificar que el usuario es un estudiante
    if request.user.rol != Usuario.ESTUDIANTE:
        messages.error(request, "No tiene permiso para acceder a esta página.")
        return redirect('dashboard')
        
    try:
        estudiante = Estudiante.objects.get(usuario=request.user)
    except Estudiante.DoesNotExist:
        messages.error(request, "No se encontró información de estudiante asociada a su cuenta.")
        return redirect('dashboard')
    
    # Crear el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boletin_{estudiante.usuario.username}.pdf"'
    
    buffer = io.BytesIO()
        
