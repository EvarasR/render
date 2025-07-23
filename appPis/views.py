from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from appPis import models
from . import forms
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from functools import wraps
from django.urls import reverse_lazy
from django.forms import modelform_factory
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Max, Sum
from datetime import datetime
from django.db import connection





 
 
def logout_view(request):
    request.session.flush()
    return redirect('/')  # redirige a tu URL de login real


from django.core.files.storage import default_storage

def requiere_sesion_y_rol(roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if 'usuario_id' not in request.session or request.session.get('usuario_rol') not in roles_permitidos:
                return redirect('/')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def registro(request):
    error = None

    if request.method == 'POST':
        form = forms.RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            try:
                usuario.save()
                return redirect('/')
            except Exception as e:
                print("Error al guardar:", e)
                error = f"No se pudo guardar el usuario: {e}"
        else:
            print("Errores de formulario:", form.errors)
    else:
        form = forms.RegistroForm()

    return render(request, 'login.html', {'form': form, 'error': error})


def login_view(request):
    error = None

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            userid = form.cleaned_data['userid'].strip()
            clave  = form.cleaned_data['clave'].strip()

            try:
                usuario = models.Usuarios.objects.get(userid=userid)

                if clave == usuario.clave:
                    # ─── guardar en sesión ─────────────────────────────
                    request.session['usuario_id']   = usuario.codusuario
                    request.session['codusuario']   = usuario.codusuario
                    request.session['usuario_nombre'] = usuario.nombre
                    request.session['usuario_rol']  = usuario.codrol_id

                    # Si es coordinador de facultad, guardar la facultad
                    if usuario.codrol_id == 9:
                        request.session['codfacultad'] = usuario.codfacultad
                        # Si quieres el nombre de la facultad (opcional):
                        try:
                            facultad = models.Facultades.objects.get(codfacultad=usuario.codfacultad)
                            request.session['nombre_facultad'] = facultad.nombre
                        except:
                            request.session['nombre_facultad'] = ''

                        return redirect('crear_autoevaluacion')  # Cambia la url a la vista de inicio del coordinador

                    # ─── redirección según rol ───────────────────────
                    rol = usuario.codrol_id

                    if rol == 7:                     # Docente
                        return redirect('docente_panel')

                    elif rol == 3:                   # Coordinador de carrera
                        return redirect('lista_indicadores')

                    elif rol in (4, 5):              # Evaluador interno / externo
                        return redirect('e_listado')

                    elif rol == 1:                   # Administrador
                        return redirect('admin_dashboard')

                    elif rol == 2:                   # Autoridades
                        return redirect('a_calificaciones')

                    elif rol == 6:                   # Auditor
                        return redirect('auditor_dashboard')

                    # Rol desconocido → vista genérica
                    return redirect('home')

                else:
                    error = "Contraseña incorrecta"

            except models.Usuarios.DoesNotExist:
                error = "Usuario no encontrado"
    else:
        form = forms.LoginForm()

    return render(request, 'login.html', {'form': form, 'error': error})



def docente_panel(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('/')

    docente = models.Usuarios.objects.get(pk=usuario_id)
    asignaciones = models.Responsablesindicador.objects.filter(codusuario=docente)

    # Diccionario: {codindicador: nombre}
    indicadores_dict = {
        i.codindicador: i.nombre for i in models.Indicadores.objects.all()
    }

    return render(request, 'paneles/docente_panel.html', {
        'docente': docente,
        'asignaciones': asignaciones,
        'indicadores_dict': indicadores_dict
    })

def home(request):
    usuario_nombre = request.session.get('usuario_nombre')
    if not usuario_nombre:
        return redirect('/')
    return render(request, 'home.html', {'usuario_nombre': usuario_nombre})

class IndicadoresListView(generic.ListView):
    model = models.Indicadores
    template_name = 'indicadores/list.html'
    context_object_name = 'indicadores'
    paginate_by = 30

class IndicadoresDetailView(generic.DetailView):
    model = models.Indicadores
    template_name = 'indicadores/detail.html'
    pk_url_kwarg = 'codindicador'  # o según tu pk real
    context_object_name = 'indicador'

# Create your views here.

#SUBIR EVIDENCIAS-------------------------------------------------------
def subir_evidencia(request, doc_pk):
    """
    Subida de evidencia para UN documento específico
    (tabla Configuracionelementofundamentalfuentedeinformaciondocumentos).
    """

    # ─── 1. Usuario autenticado ──────────────────────────────────────
    uid = request.session.get('usuario_id')
    if not uid:
        return redirect('/')

    docente = get_object_or_404(models.Usuarios, pk=uid)

    # ─── 2. Validar si tiene evaluación activa en su carrera ──────────
    evaluacion_activa = models.Evaluaciones.objects.filter(
        codfacultad=docente.codfacultad,
        codcarrera=docente.codcarrera,
        codestado__in=[3, 4],  # 3 = En proceso, 4 = Terminada
        fechainicio__lte=timezone.now().date(),
        fechafin__gte=timezone.now().date()
    ).first()

    if not evaluacion_activa:
        return HttpResponse("No hay una evaluación activa para tu carrera. No puedes subir evidencia.")

    # ─── 3. Documento de configuración ────────────────────────────────
    doc = get_object_or_404(
        models.Configuracionelementofundamentalfuentedeinformaciondocumentos,
        pk=doc_pk
    )

    # ─── 4. Indicador relacionado ─────────────────────────────────────
    indicador = get_object_or_404(
        models.Indicadores,
        codindicador=doc.codindicador
    )

    # ─── 5. ¿Aplica a varios períodos? ────────────────────────────────
    aplica_periodos = bool(doc.aplicavariosperiodos)
    periodos = (
        models.Periodoevaluacion.objects.order_by('-codperiodoevaluacion')[:5]
        if aplica_periodos else []
    )

    # ─── 6. Nombre base del archivo ───────────────────────────────────
    nombre_doc_base = doc.descripcion or f"Documento indicador {indicador.codindicador}"

    # ─── 7. Procesar subida ───────────────────────────────────────────
    if request.method == 'POST' and 'archivo' in request.FILES:
        archivo_subido = request.FILES['archivo']
        periodo_id = request.POST.get('periodo')
        periodo_obj = (
            models.Periodoevaluacion.objects.filter(pk=periodo_id).first()
            if periodo_id else None
        )

        titulo = (
            f"{nombre_doc_base} – {periodo_obj.descripcion}"
            if periodo_obj else nombre_doc_base
        )
        descripcion = request.POST.get('descripcion', '')

        try:
            # ─── Guardar archivo en disco ─────────────────────────────
            ruta_guardada = default_storage.save(
                f"evidencias/{archivo_subido.name}",
                archivo_subido
            )

            # ─── Generar IDs manuales ────────────────────────────────
            nuevo_codarchivo = (
                (models.Archivos.objects
                 .order_by('-codarchivo')
                 .values_list('codarchivo', flat=True)
                 .first() or 0) + 1
            )
            nuevo_codevidencia = (
                (models.Evidencias.objects
                 .order_by('-codevidencia')
                 .values_list('codevidencia', flat=True)
                 .first() or 0) + 1
            )
            estado = models.Estados.objects.first()

            # ─── Guardar en tabla Archivos ───────────────────────────
            archivo = models.Archivos.objects.create(
                codarchivo=nuevo_codarchivo,
                codusuario=docente,
                coddconfiguracionelementofundamentalfuentedeinformaciondocument=doc,
                nombre=archivo_subido.name,
                tipomime=archivo_subido.content_type,
                url=ruta_guardada,
                fechacarga=timezone.now(),
                codestado=estado
            )

            # ─── Guardar en tabla Evidencias ─────────────────────────
            if periodo_obj:
                descripcion = f"Período: {periodo_obj.descripcion}\n{descripcion}"

            models.Evidencias.objects.create(
                codevidencia=nuevo_codevidencia,
                codarchivo=archivo,
                titulo=titulo,
                descripcion=descripcion,
                codestado=estado
            )

            return redirect('evidencias_docente')

        except Exception as e:
            return HttpResponse(f"Error al guardar: {e}")

    # ─── 8. GET: mostrar formulario ──────────────────────────────────
    context = {
        'indicador'      : indicador,
        'doc'            : doc,
        'aplica_periodos': aplica_periodos,
        'periodos'       : periodos,
    }
    return render(request, 'paneles/subir_evidencia.html', context)

#VER LAS EVIDENCIAS SUBIDAS    
    
def evidencias_docente(request):
    """
    Lista las evidencias que el docente (usuario logueado) ya ha subido.
    """
    uid = request.session.get('usuario_id')
    if not uid:
        return redirect('/')

    evidencias = (
        models.Evidencias.objects
        .filter(codarchivo__codusuario_id=uid)
        .select_related('codarchivo')
        .order_by('-codarchivo__fechacarga')
    )

    return render(
        request,
        'paneles/evidencias_docente.html',
        {'evidencias': evidencias},
    )
    
    
#DOCUMENTOS POR INDICADOR
def documentos_por_indicador(request, indicador_id):
    """
    Muestra todos los documentos configurados para un indicador
    (tabla Configuracionelementofundamentalfuentedeinformaciondocumentos).

    • Se ordenan por la PK: 'coddconfiguracionelementofundamentalfuentedeinformaciondocument'.
    • Solo usuarios autenticados (sesión personalizada).
    """
    # ─── Autenticación ────────────────────────────────────────────────
    uid = request.session.get('usuario_id')
    if not uid:
        return redirect('/')

    # ─── Objeto Indicador (para mostrar nombre) ──────────────────────
    indicador = get_object_or_404(models.Indicadores, codindicador=indicador_id)

    # ─── Query de documentos del indicador ───────────────────────────
    documentos = (
        models.Configuracionelementofundamentalfuentedeinformaciondocumentos.objects
        .filter(codindicador=indicador_id)
        .order_by('coddconfiguracionelementofundamentalfuentedeinformaciondocument')
    )

    # ─── Render ──────────────────────────────────────────────────────
    return render(
        request,
        'paneles/documentos_indicador.html',
        {
            'indicador': indicador,
            'documentos': documentos,
        }
    )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# ───────────────────────────────────────────────────────────
def _es_coordinador(request):
    uid = request.session.get('usuario_id')
    if not uid:
        return False
    try:
        usuario = models.Usuarios.objects.get(pk=uid)
        return usuario.codrol_id == 3
    except models.Usuarios.DoesNotExist:
        return False

def _facultad_usuario(request):
    uid = request.session.get('usuario_id')
    if not uid:
        return None
    try:
        usuario = models.Usuarios.objects.get(pk=uid)
        return usuario.codfacultad
    except models.Usuarios.DoesNotExist:
        return None

def _carrera_usuario(request):
    uid = request.session.get('usuario_id')
    if not uid:
        return None
    try:
        usuario = models.Usuarios.objects.get(pk=uid)
        return usuario.codcarrera
    except models.Usuarios.DoesNotExist:
        return None

def _nombre_carrera(codcarrera):
    from .models import Carreras
    carrera = Carreras.objects.filter(codcarrera=codcarrera).first()
    return carrera.nombre if carrera else ""
    
    

# ─────── LISTA DE INDICADORES (por facultad del coordinador) ─────────────

def lista_indicadores(request):
    if not _es_coordinador(request):
        return redirect('/')

    facultad_id = _facultad_usuario(request)

    # Traer todos los indicadores
    indicadores = list(models.Indicadores.objects.all().order_by('codindicador'))

    # IDs de los que tienen responsable
    cods_con_responsable = set(
        models.Responsablesindicador.objects.filter(
            codfacultad=facultad_id
        ).values_list('codindicador', flat=True)
    )

    # Marca el estado (atributo dinámico, no va en la base)
    for ind in indicadores:
        ind.tienen_responsable = ind.codindicador in cods_con_responsable

    return render(request, 'coordinador/lista_indicadores.html', {
        'indicadores': indicadores
    })

# ─────── GESTIÓN DE RESPONSABLES ────────────────────────────

def gestion_responsables(request, indicador_id):
    if not _es_coordinador(request):
        return redirect('/')

    facultad = _facultad_usuario(request)
    carrera = _carrera_usuario(request)
    if facultad is None or carrera is None:
        messages.error(request, "No se pudo determinar la facultad o carrera del coordinador.")
        return redirect('/')

    indicador = get_object_or_404(models.Indicadores, codindicador=indicador_id)

    # Responsables actuales
    actuales = (
        models.Responsablesindicador.objects
        .filter(codindicador=indicador_id, codfacultad=facultad, codcarrera=carrera)
        .select_related('codusuario')
    )

    # Mostrar ambos tipos de docentes: responsables y no responsables
    docentes_disponibles = (
        models.Usuarios.objects
        .filter(
            codrol_id__in=[7, 10],
            codfacultad=facultad,
            codcarrera=carrera
        )
        .exclude(codusuario__in=actuales.values('codusuario_id'))
        .order_by('nombre')
    )

    if request.method == 'POST':
        if 'add_docente' in request.POST:
            docente_id = request.POST.get('docente')
            docente = get_object_or_404(models.Usuarios, pk=docente_id)

            if not docente.codfacultad or not docente.codcarrera:
                messages.error(request, "Este docente no tiene facultad o carrera asignada.")
                return redirect('gestion_responsables', indicador_id=indicador_id)

            # Cambia el rol si es necesario
            if docente.codrol_id == 10:
                docente.codrol_id = 7
                docente.save(update_fields=["codrol"])

            models.Responsablesindicador.objects.create(
                codusuario=docente,
                codfacultad=facultad,
                codcarrera=carrera,
                nombrecarrera=_nombre_carrera(carrera),
                codindicador=indicador.codindicador,
                nombreindicador=indicador.nombre,
                responsable=docente.nombre,
                identificacion=docente.userid,
            )
            messages.success(request, f'{docente.nombre} asignado como responsable.')
            return redirect('gestion_responsables', indicador_id=indicador_id)

        if 'remove_resp' in request.POST:
            resp_id = request.POST.get('resp_id')
            responsable = models.Responsablesindicador.objects.filter(pk=resp_id, codfacultad=facultad, codcarrera=carrera).first()
            docente = responsable.codusuario if responsable else None

            # Elimina al responsable
            models.Responsablesindicador.objects.filter(pk=resp_id, codfacultad=facultad, codcarrera=carrera).delete()

            # Si el docente ya NO tiene indicadores asignados en esa facultad/carrera, vuelve a ser rol 10
            if docente:
                sigue_siendo_responsable = models.Responsablesindicador.objects.filter(
                    codusuario=docente, codfacultad=facultad, codcarrera=carrera
                ).exists()
                if not sigue_siendo_responsable and docente.codrol_id == 7:
                    docente.codrol_id = 10
                    docente.save(update_fields=["codrol"])

            messages.info(request, 'Responsable eliminado.')
            return redirect('gestion_responsables', indicador_id=indicador_id)

    return render(
        request,
        'coordinador/gestion_responsables.html',
        {
            'indicador': indicador,
            'responsables_actual': actuales,
            'docentes_disponibles': docentes_disponibles,
        }
    )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# util rápido
def _es_evaluador(request):
    uid = request.session.get('usuario_id')
    if not uid:
        return False
    try:
        return models.Usuarios.objects.get(pk=uid).codrol_id in (4, 5)
    except models.Usuarios.DoesNotExist:
        return False


# 4-A  listado de indicadores

def e_listado(request):
    uid = request.session.get('usuario_id')
    if not uid:
        return redirect('/')

    hoy = timezone.now().date()

    evaluaciones = models.Evaluaciones.objects.filter(
        fechainicio__lte=hoy,
        fechafin__gte=hoy,
        codestado=3
    )

    if not evaluaciones.exists():
        return render(request, 'evaluador/listado.html', {'indicadores': []})

    for evaluacion in evaluaciones:
        criterios_asignados = (
            models.Evaluadorescriterio.objects
            .filter(
                codusuario=uid,
                codfacultad=evaluacion.codfacultad_id,
                codcarrera=evaluacion.codcarrera,
                codmodelo=evaluacion.codmodelo_id
            )
            .values_list('codcriterio', flat=True)
        )

        if criterios_asignados:
            indicadores = (
                models.Indicadores.objects
                .filter(
                    codmodelo=evaluacion.codmodelo_id,
                    codcriterio__in=criterios_asignados
                )
                .order_by('codindicador')
            )
            return render(request, 'evaluador/listado.html', {
                'indicadores': indicadores,
                'evaluacion': evaluacion
            })

    return render(request, 'evaluador/listado.html', {'indicadores': []})

def evidencias_por_indicador(request, codindicador):
    uid = request.session.get('usuario_id')
    hoy = timezone.now().date()

    indicador = get_object_or_404(models.Indicadores, codindicador=codindicador)

    evaluacion = models.Evaluaciones.objects.filter(
        codmodelo=indicador.codmodelo,
        fechainicio__lte=hoy,
        fechafin__gte=hoy,
        codestado=3
    ).first()

    if not evaluacion:
        return HttpResponse("No hay evaluación activa.")

    documentos = models.Configuracionelementofundamentalfuentedeinformaciondocumentos.objects.filter(
        codmodelo=indicador.codmodelo,
        codcriterio=indicador.codcriterio,
        codsubcriterio=indicador.codsubcriterio,
        codindicador=indicador.codindicador
    )

    data = []
    for documento in documentos:
        archivos = models.Archivos.objects.filter(
            coddconfiguracionelementofundamentalfuentedeinformaciondocument=documento.coddconfiguracionelementofundamentalfuentedeinformaciondocument
        )
        evidencias = models.Evidencias.objects.filter(
            codarchivo__in=archivos
        ).select_related('codarchivo')

        data.append({
            'documento': documento,
            'evidencias': evidencias,
        })

    return render(request, 'evaluador/evidencias.html', {
        'indicador': indicador,
        'data': data,
        'evaluacion': evaluacion,
        'codfacultad': evaluacion.codfacultad_id,
        'codcarrera': evaluacion.codcarrera,
        'codevaluacion': evaluacion.codevaluacion,
        'codmodelo': evaluacion.codmodelo_id,
        'codcriterio': indicador.codcriterio,
        'codsubcriterio': indicador.codsubcriterio,
    })

def obtener_codescalavaloracion(promedio):
    if promedio >= 0.90:
        return 1  # Satisfactorio
    elif promedio >= 0.70:
        return 2  # Cuasi satisfactorio
    elif promedio >= 0.50:
        return 3  # Poco satisfactorio
    elif promedio > 0:
        return 4  # Deficiente
    else:
        return 0  # No evaluado

ESTADOS_EVALUACION_ABIERTOS = {3}

@require_POST
def guardar_puntaje(request, codindicador):
    required_fields = [
        'codfacultad', 'codcarrera', 'codevaluacion',
        'codmodelo', 'codcriterio', 'codsubcriterio', 'codindicador'
    ]
    datos = {}
    for campo in required_fields:
        datos[campo] = request.POST.get(campo)
        if not datos[campo]:
            return HttpResponseBadRequest(f"Falta el campo: {campo}")

    try:
        codfacultad = int(datos['codfacultad'])
        codcarrera = int(datos['codcarrera'])
        codevaluacion = int(datos['codevaluacion'])
        codmodelo = int(datos['codmodelo'])
        codcriterio = int(datos['codcriterio'])
        codsubcriterio = int(datos['codsubcriterio'])
        codindicador = int(datos['codindicador'])
    except Exception as e:
        return HttpResponseBadRequest(f"Error en los datos numéricos: {e}")

    valores = []
    for key, value in request.POST.items():
        if key.startswith('valor_'):
            try:
                valores.append(float(value))
            except:
                pass

    if not valores or all(v == 0 for v in valores):
        return HttpResponse("Debe calificar al menos una evidencia.")

    total_documentos = len([k for k in request.POST.keys() if k.startswith('valor_')])
    promedio = sum(valores) / total_documentos if total_documentos > 0 else 0

    codescala = obtener_codescalavaloracion(promedio)
    codescalavaloracion = models.Escalavaloracion.objects.filter(
        codmodelo=codmodelo,
        codescalavaloracion=codescala
    ).first()

    if not codescalavaloracion:
        return HttpResponseBadRequest("No existe escala de valoración para este valor.")

    metodo = 'Evaluación directa (promedio de evidencias)'
    codusuarioevaluador = int(request.session.get('codusuario', 0))

    # NUEVO: Calcula y guarda la nota ponderada del indicador
    indicador = models.Indicadores.objects.get(
        codmodelo=codmodelo, codcriterio=codcriterio, codsubcriterio=codsubcriterio, codindicador=codindicador
    )
    valor_maximo = float(indicador.valor_maximo) if indicador.valor_maximo else 1
    nota_ponderada = promedio * valor_maximo

    puntaje, creado = models.Puntajeindicador.objects.update_or_create(
        codfacultad=codfacultad,
        codcarrera=codcarrera,
        codevaluacion=codevaluacion,
        codmodelo=codmodelo,
        codcriterio=codcriterio,
        codsubcriterio=codsubcriterio,
        codindicador=codindicador,
        defaults={
            'fecharegistro': timezone.now(),
            'valor': promedio,
            'nota_ponderada': nota_ponderada,
            'codescalavaloracion': codescalavaloracion,
            'metodo': metodo,
            'fechaevaluacion': timezone.now(),
            'codusuarioevaluador_id': codusuarioevaluador
        }
    )

    # OPCIONAL: recalcula la nota total de la evaluación después de cada guardado
    calcular_y_guardar_nota_evaluacion(
        codfacultad, codcarrera, codevaluacion, codmodelo
    )

    return redirect('e_listado')

# --------- FUNCIONES UTILITARIAS ---------------

def calcular_nota_criterio(codfacultad, codcarrera, codevaluacion, codmodelo, codcriterio):
    suma = models.Puntajeindicador.objects.filter(
        codfacultad=codfacultad,
        codcarrera=codcarrera,
        codevaluacion=codevaluacion,
        codmodelo=codmodelo,
        codcriterio=codcriterio
    ).aggregate(total=Sum('nota_ponderada'))['total']
    return float(suma) if suma else 0

def calcular_y_guardar_nota_evaluacion(codfacultad, codcarrera, codevaluacion, codmodelo):
    criterios = models.Criterios.objects.filter(
        codmodelo=codmodelo
    ).values_list('codcriterio', flat=True)

    nota_total = 0
    for codcriterio in criterios:
        nota_criterio = calcular_nota_criterio(
            codfacultad, codcarrera, codevaluacion, codmodelo, codcriterio
        )
        nota_total += nota_criterio

    # Guarda en Evaluaciones
    models.Evaluaciones.objects.filter(
        codfacultad=codfacultad,
        codcarrera=codcarrera,
        codevaluacion=codevaluacion,
        codmodelo=codmodelo
    ).update(notaevaluacion=nota_total)
    return nota_total

def cerrar_evaluaciones_por_fecha():
    hoy = timezone.now().date()
    models.Evaluaciones.objects.filter(
        fechafin__lt=hoy,
        codestado=3
    ).update(codestado=4)









        


from django.db.models import Q
def a_calificaciones(request):
    if request.session.get('usuario_rol') != 2:
        return redirect('/')

    filtro_estado = request.GET.get('estado', 'todas')
    filtro_facultad = request.GET.get('facultad')
    filtro_carrera = request.GET.get('carrera')
    filtro_evaluacion = request.GET.get('evaluacion')

    facultades = models.Facultades.objects.all().order_by('nombre')
    carreras = models.Carreras.objects.none()
    evaluaciones = models.Evaluaciones.objects.none()

    if filtro_facultad:
        carreras = models.Carreras.objects.filter(codfacultad=int(filtro_facultad)).order_by('nombre')
    if filtro_facultad and filtro_carrera:
        evaluaciones = models.Evaluaciones.objects.filter(
            codfacultad_id=int(filtro_facultad),
            codcarrera=int(filtro_carrera)
        ).order_by('-fechainicio')

    # Filtrar evaluaciones válidas por estado
    eval_qs = models.Evaluaciones.objects.all()
    if filtro_facultad:
        eval_qs = eval_qs.filter(codfacultad_id=int(filtro_facultad))
    if filtro_carrera:
        eval_qs = eval_qs.filter(codcarrera=int(filtro_carrera))
    if filtro_evaluacion:
        eval_qs = eval_qs.filter(codevaluacion=int(filtro_evaluacion))
    if filtro_estado == 'proceso':
        eval_qs = eval_qs.filter(codestado=3)
    elif filtro_estado == 'terminadas':
        eval_qs = eval_qs.filter(codestado=4)
    else:
        eval_qs = eval_qs.filter(codestado__in=[3, 4])

    # IDs de las evaluaciones válidas
    ids_evaluaciones = eval_qs.values_list('codevaluacion', flat=True)

    # Filtrar Puntajeindicador solo por las evaluaciones válidas
    puntajes = models.Puntajeindicador.objects.filter(
        codevaluacion__in=ids_evaluaciones
    )
    if filtro_facultad:
        puntajes = puntajes.filter(codfacultad=int(filtro_facultad))
    if filtro_carrera:
        puntajes = puntajes.filter(codcarrera=int(filtro_carrera))
    if filtro_evaluacion:
        puntajes = puntajes.filter(codevaluacion=int(filtro_evaluacion))

    puntajes = puntajes.select_related('codescalavaloracion')

    indicadores_dict = {i.codindicador: i for i in models.Indicadores.objects.all()}
    facultad_dict = {f.codfacultad: f.nombre for f in facultades}
    carrera_dict = {(c.codfacultad_id, c.codcarrera): c.nombre for c in models.Carreras.objects.all()}

    agrupado = {}
    for cal in puntajes:
        indicador = indicadores_dict.get(cal.codindicador)
        if not indicador:
            continue
        agrupado[indicador.codindicador] = {
            'nombre': indicador.nombre,
            'valor': cal.valor,
            'escala': cal.codescalavaloracion.nombre if cal.codescalavaloracion else '',
            'color': cal.codescalavaloracion.color_hex if cal.codescalavaloracion and cal.codescalavaloracion.color_hex else '#ddd',
            'nombre_facultad': facultad_dict.get(cal.codfacultad, ''),
            'nombre_carrera': carrera_dict.get((cal.codfacultad, cal.codcarrera), ''),
            'codevaluacion': cal.codevaluacion,
        }

    return render(request, 'autoridad/calificaciones.html', {
        'facultades': facultades,
        'carreras': carreras,
        'evaluaciones': evaluaciones,
        'agrupado': agrupado,
        'filtro_estado': filtro_estado,
        'filtro_facultad': filtro_facultad,
        'filtro_carrera': filtro_carrera,
        'filtro_evaluacion': filtro_evaluacion,
    })

    
def a_calificaciones_por_carrera(request, codfacultad, codcarrera, codevaluacion):
    if request.session.get('usuario_rol') != 2:
        return redirect('/')

    calificaciones = models.Puntajeindicador.objects.filter(
        codfacultad=codfacultad,
        codcarrera=codcarrera,
        codevaluacion=codevaluacion
    ).select_related('codescalavaloracion')

    agrupado = {}
    for cal in calificaciones:
        indicador = models.Indicadores.objects.get(codindicador=cal.codindicador)
        agrupado[indicador.codindicador] = {
            'nombre': indicador.nombre,
            'valor': cal.valor,
            'escala': cal.codescalavaloracion.nombre if cal.codescalavaloracion else '',
        }

    return render(request, 'autoridad/calificaciones_carrera.html', {
        'agrupado': agrupado,
        'codfacultad': codfacultad,
        'codcarrera': codcarrera,
        'codevaluacion': codevaluacion,
    })
    
def a_calificaciones_por_indicador(request, codindicador):
    if request.session.get('usuario_rol') != 2:
        return redirect('/')

    calificaciones = models.Puntajeindicador.objects.filter(
        codindicador=codindicador
    ).select_related('codescalavaloracion')

    indicador = models.Indicadores.objects.get(codindicador=codindicador)

    lista = []
    for cal in calificaciones:
        lista.append({
            'evaluacion': cal.codevaluacion,
            'facultad': cal.codfacultad,
            'carrera': cal.codcarrera,
            'valor': cal.valor,
            'escala': cal.codescalavaloracion.nombre if cal.codescalavaloracion else '',
            'fecha': cal.fecharegistro,
        })

    return render(request, 'autoridad/calificaciones_indicador.html', {
        'indicador': indicador,
        'calificaciones': lista,
    })
    

def listar_evaluaciones(request):
    codfacultad = request.session.get('codfacultad')  # Si quieres filtrar por facultad

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                e.codfacultad,
                f.nombre AS facultad,
                e.codcarrera,
                c.nombre AS carrera,
                e.codevaluacion,
                m.descripcion AS modelo,
                t.descripcion AS tipo,
                e.descripcion,
                e.fechainicio,
                e.fechafin,
                s.descripcion AS estado
            FROM evaluaciones e
            JOIN carreras c ON c.codfacultad = e.codfacultad AND c.codcarrera = e.codcarrera
            JOIN facultades f ON f.codfacultad = e.codfacultad
            JOIN modelos m ON m.codmodelo = e.codmodelo
            JOIN tipoevaluacion t ON t.codtipoevaluacion = e.codtipoevaluacion
            JOIN estados s ON s.codestado = e.codestado
            WHERE e.codfacultad = %s
            ORDER BY e.codcarrera, e.codevaluacion
        """, [codfacultad])
        evaluaciones = [
            dict(
                codfacultad=row[0],
                facultad=row[1],
                codcarrera=row[2],
                carrera=row[3],
                codevaluacion=row[4],
                modelo=row[5],
                tipo=row[6],
                descripcion=row[7],
                fechainicio=row[8],
                fechafin=row[9],
                estado=row[10],
            )
            for row in cursor.fetchall()
        ]

    return render(request, 'coordinador_facultad/listar_evaluaciones.html', {'evaluaciones': evaluaciones})


def crear_autoevaluacion(request):
    if not (request.session.get('usuario_rol') == 9):
        return redirect('login')
    codfacultad = request.session.get('codfacultad')
    carreras = models.Carreras.objects.filter(codfacultad=codfacultad)
    modelos = models.Modelos.objects.all()
    error = None
    if request.method == "POST":
        codcarrera = request.POST.get('codcarrera')
        codmodelo = request.POST.get('codmodelo')
        descripcion = request.POST.get('descripcion')
        fechainicio = request.POST.get('fechainicio')
        fechafin = request.POST.get('fechafin')
        try:
            fi = datetime.strptime(fechainicio, "%Y-%m-%d").date()
            ff = datetime.strptime(fechafin, "%Y-%m-%d").date()
            if ff <= fi:
                error = "La fecha fin debe ser mayor a la fecha inicio."
            else:
                # Verifica si ya existe una autoevaluación para esa carrera, periodo y tipo
                existe = False
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT 1 FROM evaluaciones WHERE codfacultad=%s AND codcarrera=%s AND codtipoevaluacion=1
                    """, [codfacultad, codcarrera])
                    existe = cursor.fetchone()
                if existe:
                    error = "Ya existe una autoevaluación para esta carrera en ese periodo."
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT MAX(codevaluacion) FROM evaluaciones
                            WHERE codfacultad=%s AND codcarrera=%s
                        """, [codfacultad, codcarrera])
                        max_eval = cursor.fetchone()[0] or 0
                        codevaluacion = max_eval + 1
                        codtipoevaluacion = 1  # Autoevaluación
                        codestado = 3         # Estado por defecto
                        cursor.execute("""
                            INSERT INTO evaluaciones (
                                codfacultad, codcarrera, codevaluacion, codmodelo, codtipoevaluacion,
                                descripcion, fechainicio, fechafin, codestado
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, [
                            codfacultad, codcarrera, codevaluacion, codmodelo, codtipoevaluacion,
                            descripcion, fi, ff, codestado
                        ])
                    return redirect('listar_evaluaciones')
        except Exception as ex:
            error = "Verifique los datos ingresados. " + str(ex)
    return render(request, 'coordinador_facultad/crear_autoevaluacion.html', {
        'carreras': carreras, 'modelos': modelos, 'error': error
    })
    
def editar_autoevaluacion(request, codfacultad, codcarrera, codevaluacion):
    if not (request.session.get('usuario_rol') == 9):
        return redirect('login')
    modelos = models.Modelos.objects.all()
    error = None
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT codmodelo, descripcion, fechainicio, fechafin, codestado
            FROM evaluaciones
            WHERE codfacultad=%s AND codcarrera=%s AND codevaluacion=%s
        """, [codfacultad, codcarrera, codevaluacion])
        row = cursor.fetchone()
    if not row:
        return render(request, 'coordinador_facultad/mensaje.html', {'mensaje': 'Evaluación no encontrada'})
    if request.method == "POST":
        codmodelo = request.POST.get('codmodelo')
        descripcion = request.POST.get('descripcion')
        fechainicio = request.POST.get('fechainicio')
        fechafin = request.POST.get('fechafin')
        codestado = request.POST.get('codestado')
        try:
            fi = datetime.strptime(fechainicio, "%Y-%m-%d").date()
            ff = datetime.strptime(fechafin, "%Y-%m-%d").date()
            if ff <= fi:
                error = "La fecha fin debe ser mayor a la fecha inicio."
            else:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE evaluaciones SET codmodelo=%s, descripcion=%s, fechainicio=%s, fechafin=%s, codestado=%s
                        WHERE codfacultad=%s AND codcarrera=%s AND codevaluacion=%s
                    """, [
                        codmodelo, descripcion, fechainicio, fechafin, codestado,
                        codfacultad, codcarrera, codevaluacion
                    ])
                return redirect('listar_evaluaciones')
        except Exception as ex:
            error = "Verifique los datos ingresados. " + str(ex)
    return render(request, 'coordinador_facultad/editar_autoevaluacion.html', {
        'modelos': modelos,
        'evaluacion': {
            'codmodelo': row[0], 'descripcion': row[1],
            'fechainicio': row[2], 'fechafin': row[3], 'codestado': row[4]
        },
        'codfacultad': codfacultad,
        'codcarrera': codcarrera,
        'codevaluacion': codevaluacion,
        'error': error
    })
    

def eliminar_autoevaluacion(request, codfacultad, codcarrera, codevaluacion):
    if not (request.session.get('usuario_rol') == 9):
        return redirect('login')
    error = None
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM evaluaciones WHERE codfacultad=%s AND codcarrera=%s AND codevaluacion=%s
                """, [codfacultad, codcarrera, codevaluacion])
            return redirect('listar_evaluaciones')
        except Exception as ex:
            error = "No se pudo eliminar la evaluación: " + str(ex)
    return render(request, 'coordinador_facultad/confirmar_eliminar.html', {
        'codfacultad': codfacultad, 'codcarrera': codcarrera, 'codevaluacion': codevaluacion, 'error': error
    })