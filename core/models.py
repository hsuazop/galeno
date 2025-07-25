from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='paciente')
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    dni = models.CharField(max_length=50, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    email = models.EmailField(unique=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def edad(self):
        if self.fecha_nacimiento:
            hoy = date.today()
            return hoy.year - self.fecha_nacimiento.year - (
                    (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Hospital(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medico')
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"Dr. {self.nombre} {self.apellido} - {self.especialidad}"


class Asistente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='asistente')
    medico = models.ManyToManyField(Medico, related_name='asistentes')
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"Asistente {self.nombre} {self.apellido} de {self.medico}"


class AgendaMedica(models.Model):
    medico = models.ForeignKey('Medico', on_delete=models.CASCADE, related_name='agendas')
    fecha = models.DateField()  # Día específico
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    disponible = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        unique_together = ('medico', 'fecha', 'hora_inicio')  # No duplicar horarios en el mismo día

    def __str__(self):
        return f"Agenda de {self.medico} - {self.fecha} ({self.hora_inicio} - {self.hora_fin})"


class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()
    notas_medico = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=[('Pendiente', 'Pendiente'), ('Completada', 'Completada'), ('Cancelada', 'Cancelada')],
                              default='Completada')

    def __str__(self):
        return f"Cita de {self.paciente} con {self.medico} el {self.fecha_hora}"


class EvaluacionFisica(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)

    temperatura = models.CharField(
        max_length=1000,
        help_text="Temperatura en °C (ej. 36.8)",
        blank=True,
        null=True
    )
    peso = models.CharField(
        max_length=1000,
        help_text="Peso en kg (ej. 72.5)",
        blank=True,
        null=True
    )
    estatura = models.CharField(
        max_length=1000,
        help_text="Estatura en metros (ej. 1.75)",
        blank=True,
        null=True
    )
    presion_arterial = models.CharField(
        max_length=1500,
        help_text="Ejemplo: 120/80 mmHg",
        blank=True,
        null=True
    )
    frecuencia_cardiaca = models.CharField(
        max_length=1000,
        help_text="Frecuencia cardiaca en bpm",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Evaluación física para la cita del {self.cita.fecha_hora}"


class Diagnostico(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"Diagnóstico para {self.cita.paciente}"


class Medicamento(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Receta(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    recomendaciones_generales = models.TextField(blank=True)

    def __str__(self):
        return f"Receta de {self.cita.paciente} - {self.fecha_emision}"


class RecetaMedicamento(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="medicamentos")

    # Ya no es ForeignKey, ahora es texto libre
    medicamento = models.CharField(
        max_length=1055,
        help_text="Nombre del medicamento (ej. Amoxicilina 500mg)"
    )

    dosis = models.CharField(
        max_length=1055,
        help_text="Ejemplo: 1 tableta cada 8 horas por 7 días"
    )

    def __str__(self):
        return f"{self.medicamento} - {self.dosis}"
