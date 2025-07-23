from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.login_view, name='login' ),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.registro, name='registro'),
    path('home/', views.home, name='home'),
    path('docente/', views.docente_panel, name='docente_panel'),
    path('indicadores/', views.IndicadoresListView.as_view(), name='indicador-list'),
    path('indicadores/<int:codmodelo>/', views.IndicadoresDetailView.as_view(), name='indicador-detail'),
    path('docente/subir/<int:doc_pk>/', views.subir_evidencia, name='subir_evidencia'),
    path('docente/evidencias/', views.evidencias_docente, name='evidencias_docente'),
    path('docente/indicador/<int:indicador_id>/documentos/',views.documentos_por_indicador,name='documentos_indicador'),
    path('coordinador/indicadores/',views.lista_indicadores,name='lista_indicadores'),
    path('coordinador/indicador/<int:indicador_id>/responsables/',views.gestion_responsables,name='gestion_responsables'),
    path('evaluador/indicadores/', views.e_listado,      name='e_listado'),
    path('evaluador/indicador/<int:codindicador>/', views.evidencias_por_indicador, name='evidencias_por_indicador'),
    path('evaluador/calificar/<int:codindicador>/guardar/', views.guardar_puntaje, name='guardar_puntaje'),
    # path('evaluador/calificar/<int:codevaluacion>/', views.PuntajeCreateView.as_view(), name='e_calificar'),
    path('autoridad/calificaciones/', views.a_calificaciones, name='a_calificaciones'),
    path('autoridad/calificaciones/<int:codfacultad>/<int:codcarrera>/<int:codevaluacion>/', views.a_calificaciones_por_carrera, name='a_calificaciones_por_carrera'),
    path('autoridad/calificaciones/indicador/<int:codindicador>/', views.a_calificaciones_por_indicador, name='a_calificaciones_por_indicador'),
    path('evaluaciones/', views.listar_evaluaciones, name='listar_evaluaciones'),
    path('evaluaciones/nueva/', views.crear_autoevaluacion, name='crear_autoevaluacion'),
    path('evaluaciones/<int:codfacultad>/<int:codcarrera>/<int:codevaluacion>/editar/', views.editar_autoevaluacion, name='editar_autoevaluacion'),
    path('evaluaciones/<int:codfacultad>/<int:codcarrera>/<int:codevaluacion>/eliminar/', views.eliminar_autoevaluacion, name='eliminar_autoevaluacion'),

]

