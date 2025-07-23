from django.contrib.auth.backends import BaseBackend
from appPis.models import Usuarios

class UsuarioAutenticado:
    def __init__(self, usuario):
        self.id = usuario.codusuario
        self.username = usuario.userid
        self.email = usuario.correo
        self._usuario = usuario

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self._usuario.estadologin == 1  # o simplemente True

    def __str__(self):
        return self.username

class UsuarioBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            usuario = Usuarios.objects.get(userid=username)
            if usuario.clave == password:  # sin cifrado
                return UsuarioAutenticado(usuario)
        except Usuarios.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            usuario = Usuarios.objects.get(pk=user_id)
            return UsuarioAutenticado(usuario)
        except Usuarios.DoesNotExist:
            return None
