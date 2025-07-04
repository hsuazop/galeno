from django import forms
from django.contrib.auth.models import User
from core.models import Medico

class RegistroMedicoForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        error_messages={'required': 'Correo es obligatorio.'}
    )
    password = forms.CharField(
        label="Contraseña",
        min_length=6,
        widget=forms.PasswordInput,
        error_messages={'required': 'Contraseña es obligatoria.'}
    )
    password_confirm = forms.CharField(
        label="Confirmar contraseña",
        min_length=6,
        widget=forms.PasswordInput,
        error_messages={'required': 'Confirmar contraseña es obligatoria.'}
    )
    nombre = forms.CharField(
        label="Nombre",
        error_messages={'required': 'Nombre es obligatorio.'}
    )
    apellido = forms.CharField(
        label="Apellido",
        error_messages={'required': 'Apellido es obligatorio.'}
    )
    telefono = forms.CharField(
        label="Teléfono",
        required=False
    )
    especialidad_id = forms.IntegerField(
        label="Especialidad",
        required=False
    )
    acepta_terminos = forms.BooleanField(
        label="Términos y condiciones",
        required=True,
        error_messages={'required': 'Debes aceptar los términos y condiciones.'}
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        if Medico.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo ya está registrado como médico.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')

        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")