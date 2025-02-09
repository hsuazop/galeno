from django.db import models


class Paciente(models.Model):
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


class Medico(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    especialidad = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"Dr. {self.nombre} {self.apellido} - {self.especialidad}"


class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    motivo = models.TextField()
    notas_medico = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=[('Pendiente', 'Pendiente'), ('Completada', 'Completada'), ('Cancelada', 'Cancelada')], default='Pendiente')

    def __str__(self):
        return f"Cita de {self.paciente} con {self.medico} el {self.fecha_hora}"


class EvaluacionFisica(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, help_text="Temperatura en °C")
    peso = models.DecimalField(max_digits=5, decimal_places=2, help_text="Peso en kg")
    estatura = models.DecimalField(max_digits=4, decimal_places=2, help_text="Estatura en metros")
    presion_arterial = models.CharField(max_length=15, help_text="Ejemplo: 120/80 mmHg")
    frecuencia_cardiaca = models.IntegerField(help_text="Frecuencia cardiaca en bpm")

    def __str__(self):
        return f"Evaluación física de {self.cita.paciente}"


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
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    dosis = models.CharField(max_length=255, help_text="Ejemplo: 1 tableta cada 8 horas por 7 días")

    def __str__(self):
        return f"{self.medicamento} - {self.dosis}"
