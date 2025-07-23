# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Acciones(models.Model):
    codfacultad = models.ForeignKey('Planmejora', models.DO_NOTHING, db_column='codfacultad')
    codcarrera = models.IntegerField()
    codevaluacion = models.IntegerField()
    codplanmejora = models.IntegerField()
    codaccion = models.BigAutoField(primary_key=True)
    descripcion = models.TextField()
    fechainicio = models.DateField()
    fechafin = models.DateField()
    fechacompromiso = models.DateField()
    codusuarioresponsable = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='codusuarioresponsable')
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    codestado = models.ForeignKey('Estados', models.DO_NOTHING, db_column='codestado', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'acciones'
        unique_together = (('codfacultad', 'codcarrera', 'codevaluacion', 'codplanmejora', 'codaccion'),)


class Archivos(models.Model):
    codusuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='codusuario')
    codarchivo = models.BigIntegerField(primary_key=True)
    coddconfiguracionelementofundamentalfuentedeinformaciondocument = models.ForeignKey('Configuracionelementofundamentalfuentedeinformaciondocumentos', models.DO_NOTHING, db_column='coddconfiguracionelementofundamentalfuentedeinformaciondocument', to_field='coddconfiguracionelementofundamentalfuentedeinformaciondocument')
    nombre = models.TextField()
    tipomime = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    fechacarga = models.DateTimeField(blank=True, null=True)
    codestado = models.ForeignKey('Estados', models.DO_NOTHING, db_column='codestado', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archivos'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Carreras(models.Model):
    codfacultad = models.OneToOneField('Facultades', models.DO_NOTHING, db_column='codfacultad', primary_key=True)  # The composite primary key (codfacultad, codcarrera) found, that is not supported. The first column is selected.
    codcarrera = models.IntegerField()
    codtipocarrera = models.ForeignKey('Tipocarrera', models.DO_NOTHING, db_column='codtipocarrera')
    nombre = models.CharField(max_length=100)
    codestadocarrera = models.ForeignKey('Estados', models.DO_NOTHING, db_column='codestadocarrera', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'carreras'
        unique_together = (('codfacultad', 'codcarrera'),)


class Criterios(models.Model):
    codmodelo = models.OneToOneField('Modelos', models.DO_NOTHING, db_column='codmodelo', primary_key=True)  # The composite primary key (codmodelo, codcriterio) found, that is not supported. The first column is selected.
    codcriterio = models.IntegerField()
    nombre = models.CharField(max_length=60)
    descripcion = models.TextField(blank=True, null=True)
    codestadocriterio = models.ForeignKey('Estados', models.DO_NOTHING, db_column='codestadocriterio', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'criterios'
        unique_together = (('codmodelo', 'codcriterio'), ('codmodelo', 'nombre'),)


class Detalleelementofundamentalfuentedeinformacion(models.Model):
    codmodelo = models.ForeignKey('Fuentedeinformacion', models.DO_NOTHING, db_column='codmodelo')
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()
    codelementofundamental = models.IntegerField()
    codfuentedeinformacion = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'detalleelementofundamentalfuentedeinformacion'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Elementofundamental(models.Model):
    codmodelo = models.OneToOneField('Indicadores', models.DO_NOTHING, db_column='codmodelo', primary_key=True)  # The composite primary key (codmodelo, codcriterio, codsubcriterio, codindicador, codelementofundamental) found, that is not supported. The first column is selected.
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()
    codelementofundamental = models.IntegerField()
    descripcion = models.TextField()
    codestadoelementofundamental = models.ForeignKey('Estados', models.DO_NOTHING, db_column='codestadoelementofundamental', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'elementofundamental'
        unique_together = (('codmodelo', 'codcriterio', 'codsubcriterio', 'codindicador', 'codelementofundamental'),)


class Escalavaloracion(models.Model):
    codmodelo = models.ForeignKey('Modelos', models.DO_NOTHING, db_column='codmodelo')
    codtipoescala = models.ForeignKey('Tipoescala', models.DO_NOTHING, db_column='codtipoescala')
    codescalavaloracion = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    codestado = models.ForeignKey('Estados', models.DO_NOTHING, db_column='codestado', blank=True, null=True)
    color_hex = models.TextField(blank=True, null=True)
    valor = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'escalavaloracion'


class Estados(models.Model):
    codestado = models.IntegerField(primary_key=True)
    tipo = models.TextField()  # This field type is a guess.
    descripcion = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'estados'


class Evaluaciones(models.Model):
    codfacultad = models.OneToOneField(Carreras, models.DO_NOTHING, db_column='codfacultad', primary_key=True)  # The composite primary key (codfacultad, codcarrera, codevaluacion) found, that is not supported. The first column is selected.
    codcarrera = models.IntegerField()
    codmodelo = models.ForeignKey('Modelos', models.DO_NOTHING, db_column='codmodelo')
    codtipoevaluacion = models.ForeignKey('Tipoevaluacion', models.DO_NOTHING, db_column='codtipoevaluacion')
    codevaluacion = models.IntegerField()
    descripcion = models.TextField(blank=True, null=True)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    codestado = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestado', blank=True, null=True)
    notaevaluacion = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evaluaciones'
        unique_together = (('codfacultad', 'codcarrera', 'codevaluacion'),)
        
        
        
class Evaluadorescriterio(models.Model):
    codevaluador = models.AutoField(primary_key=True)
    codusuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='codusuario')
    codfacultad = models.IntegerField()
    codcarrera = models.IntegerField()
    codmodelo = models.IntegerField()
    codcriterio = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'evaluadorescriterio'
        unique_together = (('codusuario', 'codfacultad', 'codcarrera', 'codmodelo', 'codcriterio'),)
        
        

class Evidencias(models.Model):
    codarchivo = models.ForeignKey(Archivos, models.DO_NOTHING, db_column='codarchivo')
    codevidencia = models.BigIntegerField(primary_key=True)
    titulo = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    codestado = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestado', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evidencias'


class Facultades(models.Model):
    codinstitucion = models.ForeignKey('Instituciones', models.DO_NOTHING, db_column='codinstitucion')
    codfacultad = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=10)
    codestadofacultad = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestadofacultad', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'facultades'


class Fuentedeinformacion(models.Model):
    codmodelo = models.OneToOneField('Indicadores', models.DO_NOTHING, db_column='codmodelo', primary_key=True)  # The composite primary key (codmodelo, codcriterio, codsubcriterio, codindicador, codfuentedeinformacion) found, that is not supported. The first column is selected.
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()
    codfuentedeinformacion = models.IntegerField()
    descripcion = models.TextField()
    codestadofuentedeinformacion = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestadofuentedeinformacion', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fuentedeinformacion'
        unique_together = (('codmodelo', 'codcriterio', 'codsubcriterio', 'codindicador', 'codfuentedeinformacion'),)


class Indicadores(models.Model):
    codmodelo = models.IntegerField(primary_key=True)
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()
    codtipoindicador = models.ForeignKey('Tipoindicador', models.DO_NOTHING, db_column='codtipoindicador')
    descripcion = models.TextField(blank=True, null=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    estandar = models.TextField(blank=True, null=True)
    umbralminimo = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    valor_maximo = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'indicadores'
        unique_together = (('codmodelo', 'codcriterio', 'codsubcriterio', 'nombre'),)

class Instituciones(models.Model):
    codinstitucion = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'instituciones'


class Lineamientovariable(models.Model):
    codmodelo = models.OneToOneField(Indicadores, models.DO_NOTHING, db_column='codmodelo', primary_key=True)  # The composite primary key (codmodelo, codcriterio, codsubcriterio, codindicador, codlineamientovariable) found, that is not supported. The first column is selected.
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()
    codlineamientovariable = models.IntegerField()
    descripcion = models.TextField()
    codestadolineamientovariable = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestadolineamientovariable', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lineamientovariable'
        unique_together = (('codmodelo', 'codcriterio', 'codsubcriterio', 'codindicador', 'codlineamientovariable'),)


class Medicionelementofundamental(models.Model):
    codfacultad = models.OneToOneField(Evaluaciones, models.DO_NOTHING, db_column='codfacultad')  # The composite primary key (codfacultad, codcarrera, codevaluacion, codmodelo, codcriterio, codsubcriterio, codindicador, codelementofundamental, codmedicionelementofundamental, codfuentedeinformacion) found, that is not supported. The first column is selected.
    codcarrera = models.IntegerField()
    codevaluacion = models.IntegerField()
    codmodelo = models.ForeignKey(Fuentedeinformacion, models.DO_NOTHING, db_column='codmodelo')
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()
    codelementofundamental = models.IntegerField()
    codfuentedeinformacion = models.IntegerField()
    codmedicionelementofundamental = models.BigAutoField(primary_key=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    valor = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    fechacorte = models.DateField(blank=True, null=True)
    codescalavaloracion = models.ForeignKey(Escalavaloracion, models.DO_NOTHING, db_column='codescalavaloracion')
    codusuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='codusuario', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'medicionelementofundamental'
        unique_together = (('codfacultad', 'codcarrera', 'codevaluacion', 'codmodelo', 'codcriterio', 'codsubcriterio', 'codindicador', 'codelementofundamental', 'codmedicionelementofundamental', 'codfuentedeinformacion'),)


class Medicionevidencia(models.Model):
    codfacultad = models.ForeignKey(Medicionelementofundamental, models.DO_NOTHING, db_column='codfacultad')
    codcarrera = models.IntegerField()
    codevaluacion = models.IntegerField()
    codmodelo = models.IntegerField()
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()
    codelementofundamental = models.IntegerField()
    codfuentedeinformacion = models.IntegerField()
    codmedicionelementofundamental = models.BigIntegerField(primary_key=True)  # The composite primary key (codmedicionelementofundamental, codevidencia) found, that is not supported. The first column is selected.
    codevidencia = models.ForeignKey(Evidencias, models.DO_NOTHING, db_column='codevidencia')

    class Meta:
        managed = False
        db_table = 'medicionevidencia'
        unique_together = (('codmedicionelementofundamental', 'codevidencia'),)


class Modelos(models.Model):
    codmodelo = models.IntegerField(primary_key=True)
    descripcion = models.CharField(unique=True, max_length=100)
    codestadomodelo = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestadomodelo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modelos'


class Observacionindicador(models.Model):
    codfacultad = models.ForeignKey('Puntajeindicador', models.DO_NOTHING, db_column='codfacultad')
    codcarrera = models.IntegerField()
    codevaluacion = models.IntegerField()
    codmodelo = models.IntegerField()
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()
    codpuntajeindicador = models.BigIntegerField()
    codobservacionindicador = models.BigAutoField(primary_key=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    codtiporecomendacion = models.ForeignKey('Tiporecomendacion', models.DO_NOTHING, db_column='codtiporecomendacion')
    descripcion = models.TextField(blank=True, null=True)
    fecharegistroevaluacion = models.DateTimeField(blank=True, null=True)
    codusuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='codusuario', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'observacionindicador'


class Periodoevaluacion(models.Model):
    codperiodoevaluacion = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'periodoevaluacion'


class Planmejora(models.Model):
    codfacultad = models.OneToOneField(Evaluaciones, models.DO_NOTHING, db_column='codfacultad', primary_key=True)  # The composite primary key (codfacultad, codcarrera, codevaluacion, codplanmejora) found, that is not supported. The first column is selected.
    codcarrera = models.IntegerField()
    codevaluacion = models.IntegerField()
    codplanmejora = models.IntegerField()
    fechaaprobacion = models.DateField()
    descripcion = models.TextField()
    fechainicio = models.DateField()
    fechafin = models.DateField()
    codestado = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestado', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'planmejora'
        unique_together = (('codfacultad', 'codcarrera', 'codevaluacion', 'codplanmejora'),)


class Puntajeindicador(models.Model):
    codfacultad = models.IntegerField()
    codcarrera = models.IntegerField()
    codevaluacion = models.IntegerField()

    codmodelo = models.IntegerField()
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()

    codpuntajeindicador = models.BigAutoField(primary_key=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    valor = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True)
    codescalavaloracion = models.ForeignKey('Escalavaloracion', models.DO_NOTHING, db_column='codescalavaloracion')
    metodo = models.TextField(blank=True, null=True)
    fechaevaluacion = models.DateTimeField(blank=True, null=True)
    codusuarioevaluador = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='codusuarioevaluador', blank=True, null=True)
    nota_ponderada = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'puntajeindicador'
        unique_together = (
            ('codfacultad', 'codcarrera', 'codevaluacion', 'codmodelo', 'codcriterio', 'codsubcriterio', 'codindicador', 'codpuntajeindicador'),
            ('codfacultad', 'codcarrera', 'codevaluacion', 'codmodelo', 'codcriterio', 'codsubcriterio', 'codindicador'),
        )

class Roles(models.Model):
    codrol = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'roles'


class Seguimientos(models.Model):
    codaccion = models.ForeignKey(Acciones, models.DO_NOTHING, db_column='codaccion')
    codcarrera = models.IntegerField()
    codevaluacion = models.IntegerField()
    codplanmejora = models.IntegerField()
    codaccion = models.IntegerField()
    codseguimiento = models.BigAutoField(primary_key=True)
    fecha = models.DateField()
    avance = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    codestado = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestado', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seguimientos'
        unique_together = (( 'codcarrera', 'codevaluacion', 'codplanmejora', 'codaccion', 'codseguimiento'),)


class Subcriterios(models.Model):
    codmodelo = models.OneToOneField(Criterios, models.DO_NOTHING, db_column='codmodelo', primary_key=True)  # The composite primary key (codmodelo, codcriterio, codsubcriterio) found, that is not supported. The first column is selected.
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    nombre = models.CharField(max_length=60)
    descripcion = models.TextField(blank=True, null=True)
    codestadosubcriterio = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestadosubcriterio', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcriterios'
        unique_together = (('codmodelo', 'codcriterio', 'codsubcriterio'), ('codmodelo', 'codcriterio', 'nombre'),)


class Tipocarrera(models.Model):
    codtipocarrera = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'tipocarrera'


class Tipoescala(models.Model):
    codtipoescala = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'tipoescala'


class Tipoevaluacion(models.Model):
    codtipoevaluacion = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'tipoevaluacion'


class Tipoindicador(models.Model):
    codtipoindicador = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'tipoindicador'


class Tiporecomendacion(models.Model):
    codtiporecomendacion = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'tiporecomendacion'


class Usuarios(models.Model):
    codrol = models.ForeignKey(Roles, models.DO_NOTHING, db_column='codrol')
    codusuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=40)
    correo = models.CharField(max_length=80)
    userid = models.TextField(unique=True)
    clave = models.TextField()
    codestadousuario = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestadousuario', blank=True, null=True)
    estadologin = models.IntegerField(blank=True, null=True)
    codfacultad = models.IntegerField(blank=True, null=True)
    codcarrera = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarios'


class Visitas(models.Model):
    codfacultad = models.OneToOneField(Evaluaciones, models.DO_NOTHING, db_column='codfacultad', primary_key=True)  # The composite primary key (codfacultad, codcarrera, codevaluacion, codvisita) found, that is not supported. The first column is selected.
    codcarrera = models.IntegerField()
    codevaluacion = models.IntegerField()
    codvisita = models.IntegerField()
    fechainicio = models.DateField()
    fechafin = models.DateField()
    codestado = models.ForeignKey(Estados, models.DO_NOTHING, db_column='codestado', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'visitas'
        unique_together = (('codfacultad', 'codcarrera', 'codevaluacion', 'codvisita'),)
        
# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

class Configuracionelementofundamentalfuentedeinformaciondocumentos(models.Model):
    # ---------- campos que identifican la configuración ----------
    codmodelo  = models.ForeignKey(
        'Detalleelementofundamentalfuentedeinformacion',
        models.DO_NOTHING,
        db_column='codmodelo'
    )
    codcriterio  = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador  = models.IntegerField()
    codelementofundamental = models.IntegerField()
    codfuentedeinformacion = models.IntegerField()
    coddetalleelementofundamentalfuentedeinformacion = models.BigIntegerField()

    # ---------- único campo autoincremental existente en la tabla ----------
    coddconfiguracionelementofundamentalfuentedeinformaciondocument = models.BigAutoField(
        primary_key=True,
        db_column='coddconfiguracionelementofundamentalfuentedeinformaciondocument'
    )

    # ---------- otros datos ----------
    aplicavariosperiodos = models.IntegerField(blank=True, null=True)
    descripcion = models.TextField()

    class Meta:
        managed = False          # <—  Django no tocará la tabla
        db_table = 'configuracionelementofundamentalfuentedeinformaciondocumentos'
        unique_together = (
            (
                'codmodelo', 'codcriterio', 'codsubcriterio', 'codindicador',
                'codelementofundamental', 'codfuentedeinformacion',
                'coddetalleelementofundamentalfuentedeinformacion'
            ),
        )
        
class Doc(models.Model):
    codigo = models.AutoField(primary_key=True)
    identificacion = models.TextField(blank=True, null=True)
    idnivel = models.IntegerField(blank=True, null=True)
    nombrecortofacultad = models.TextField(blank=True, null=True)
    nombrecarrera = models.TextField(blank=True, null=True)
    curso = models.TextField(blank=True, null=True)
    nombredocente = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    emailpersonal = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doc'
        
class Est(models.Model):
    codigo = models.AutoField(primary_key=True)
    identificacion = models.TextField(blank=True, null=True)
    idfacultad = models.IntegerField(blank=True, null=True)
    idnivel = models.IntegerField(blank=True, null=True)
    nombrecortofacultad = models.TextField(blank=True, null=True)
    nombrecarrera = models.TextField(blank=True, null=True)
    curso = models.TextField(blank=True, null=True)
    nombreestudiante = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    celular = models.TextField(blank=True, null=True)
    emailpersonal = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'est'
        
class Medidorelementofundamentalfuenteinformciondocumentos(models.Model):
    codmodelo = models.IntegerField()
    codcriterio = models.IntegerField()
    codsubcriterio = models.IntegerField()
    codindicador = models.IntegerField()
    codelementofundamental = models.IntegerField()
    codfuentedeinformacion = models.IntegerField()
    coddetalleelementofundamentalfuentedeinformacion = models.BigIntegerField()
    codmedidorelementofundamentaldocumentos = models.BigAutoField(primary_key=True)
    aplicavariosperiodos = models.IntegerField(blank=True, null=True)
    descripcion = models.TextField()

    class Meta:
        managed = False
        db_table = 'medidorelementofundamentalfuenteinformciondocumentos'
        unique_together = (('codmodelo', 'codcriterio', 'codsubcriterio', 'codindicador', 'codelementofundamental', 'codfuentedeinformacion'),)
        

class Responsablesindicador(models.Model):
    codresponsable = models.AutoField(primary_key=True)
    codusuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='codusuario')
    codfacultad = models.IntegerField(blank=True, null=True)
    codcarrera = models.IntegerField(blank=True, null=True)
    nombrecarrera = models.TextField(blank=True, null=True)
    codindicador = models.IntegerField(blank=True, null=True)
    nombreindicador = models.TextField(blank=True, null=True)
    responsable = models.TextField(blank=True, null=True)
    identificacion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'responsablesindicador'