from django.contrib import admin
from core.models import *

# ------------ Paciente ------------
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'email', 'dni')
    list_filter = ('genero', 'fecha_registro')
    ordering = ('apellido',)

# ------------ Especialidad ------------
@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

# ------------ Hospital ------------
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email')
    search_fields = ('nombre',)

# ------------ Asistente Inline para Medico ------------
# class AsistenteInline(admin.TabularInline):
#     model = Asistente.medicos.through
#     extra = 1

# ------------ Medico ------------
@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'especialidad', 'hospital', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'email')
    list_filter = ('especialidad', 'hospital')
    # inlines = [AsistenteInline]

# ------------ Asistente ------------
@admin.register(Asistente)
class AsistenteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'email')
    # filter_horizontal = ('medicos',)

# ------------ AgendaMedica ------------
@admin.register(AgendaMedica)
class AgendaMedicaAdmin(admin.ModelAdmin):
    list_display = ('medico', 'fecha', 'hora_inicio', 'hora_fin', 'disponible')
    search_fields = ('medico__nombre', 'medico__apellido')
    list_filter = ('fecha', 'disponible')
    ordering = ('fecha', 'hora_inicio')

# ------------ Cita ------------
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'fecha_hora', 'estado')
    search_fields = ('paciente__nombre', 'medico__nombre', 'fecha_hora')
    list_filter = ('estado',)
    ordering = ('fecha_hora',)

# ------------ EvaluacionFisica ------------
@admin.register(EvaluacionFisica)
class EvaluacionFisicaAdmin(admin.ModelAdmin):
    list_display = ('cita', 'peso', 'estatura', 'presion_arterial', 'frecuencia_cardiaca')
    search_fields = ('cita__paciente__nombre', 'cita__medico__nombre')

# ------------ Diagnostico ------------
@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ('cita',)
    search_fields = ('cita__paciente__nombre', 'cita__medico__nombre')

# ------------ Medicamento ------------
@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

# ------------ RecetaMedicamento Inline para Receta ------------
class RecetaMedicamentoInline(admin.TabularInline):
    model = RecetaMedicamento
    extra = 1

# ------------ Receta ------------
@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('cita', 'fecha_emision')
    inlines = [RecetaMedicamentoInline]

# ------------ RecetaMedicamento ------------
@admin.register(RecetaMedicamento)
class RecetaMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('receta', 'medicamento', 'dosis')
    search_fields = ('medicamento__nombre', 'receta__cita__paciente__nombre')


@admin.register(MedicoPaciente)
class MedicoPacienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'medico', 'paciente', 'fecha_emision')
    list_filter = ('medico', 'fecha_emision')
    search_fields = (
        'paciente__nombre', 'paciente__apellido', 'paciente__dni',
        'medico__nombre', 'medico__apellido', 'medico__email'
    )


@admin.register(Odontograma)
class OdontogramaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'paciente',
        'medico',
        'cita',
        'creado_en',
        'actualizado_en',
    )
    list_filter = ('medico', 'creado_en', 'actualizado_en')
    search_fields = (
        'paciente__nombre',
        'paciente__apellido',
        'paciente__dni',
        'medico__user__first_name',
        'medico__user__last_name',
        'cita__id',
    )
    ordering = ('-creado_en',)
    readonly_fields = ('creado_en', 'actualizado_en')

