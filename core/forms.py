# core/forms.py
from django import forms
from .models import Paciente
from django.core.exceptions import ValidationError

class PacienteCreateForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nombre', 'apellido', 'fecha_nacimiento', 'genero', 'dni',
            'telefono', 'direccion', 'email', 'ciudad'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'genero': forms.Select(choices=[('M', 'Masculino'), ('F', 'Femenino')], attrs={'class': 'form-select'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        v = (self.cleaned_data.get('nombre') or '').strip()
        if not v:
            raise ValidationError('El nombre es obligatorio.')
        return v

    def clean_apellido(self):
        v = (self.cleaned_data.get('apellido') or '').strip()
        if not v:
            raise ValidationError('El apellido es obligatorio.')
        return v

    def clean_dni(self):
        v = (self.cleaned_data.get('dni') or '').strip()
        if not v:
            raise ValidationError('El DNI es obligatorio.')
        return v

    def clean_email(self):
        v = (self.cleaned_data.get('email') or '').strip()
        # El email es opcional; si viene, Django valida formato por EmailField
        return v or None
