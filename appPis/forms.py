from django import forms
from . import models
from .models import Usuarios


class SubirEvidenciaForm(forms.Form):
    archivo = forms.FileField(label='Selecciona un archivo', required=True)
    titulo = forms.CharField(max_length=255, required=True)
    descripcion = forms.CharField(widget=forms.Textarea, required=False)

class RegistroForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ['codrol', 'nombre', 'correo', 'userid', 'clave']
        
class LoginForm(forms.Form):
    userid = forms.CharField(label="Usuario")
    clave = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    
class PuntajeForm(forms.ModelForm):
    class Meta:
        model = models.Puntajeindicador
        fields = ['codescalavaloracion']  # solo este campo
        widgets = {
            'codescalavaloracion': forms.Select(attrs={'class': 'form-select'})
        }


class AutoevaluacionForm(forms.ModelForm):
    class Meta:
        model = models.Evaluaciones
        fields = ['codcarrera', 'codmodelo', 'descripcion', 'fechainicio', 'fechafin']

    def __init__(self, *args, **kwargs):
        carreras = kwargs.pop('carreras')
        super().__init__(*args, **kwargs)
        self.fields['codcarrera'].queryset = carreras
        self.fields['codcarrera'].label = "Carrera"
        self.fields['codmodelo'].label = "Modelo"
        self.fields['descripcion'].widget = forms.Textarea(attrs={'rows': 2})
        self.fields['fechainicio'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['fechafin'].widget = forms.DateInput(attrs={'type': 'date'})
