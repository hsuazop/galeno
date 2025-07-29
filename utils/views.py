from django.contrib.auth.models import User
from core.models import Medico, Paciente, Cita, EvaluacionFisica, Diagnostico, Receta, RecetaMedicamento
from django.utils import timezone
from datetime import timedelta
import random
from django.http import HttpResponse

def crear_datos_demo_galeno(request):
    try:
        medico_user = User.objects.get(username='hectorsp25@gmial.com')
        medico = Medico.objects.get(user=medico_user)
    except User.DoesNotExist:
        return HttpResponse("❌ Usuario del médico no encontrado.")
    except Medico.DoesNotExist:
        return HttpResponse("❌ Médico relacionado no encontrado.")

    nombres = [
        ("Ana", "López", "F", "ana.lopez@gmail.com"),
        ("José", "Martínez", "M", "jose.martinez@yahoo.com"),
        ("María Fernanda", "Rivera", "F", "maria.fernanda@hotmail.com"),
        ("Carlos", "González", "M", "carlos.gonzalez@gmail.com"),
        ("Lucía", "Ramírez", "F", "lucia.ramirez@outlook.com"),
        ("Pedro", "Zelaya", "M", "pedro.zelaya@correo.hn"),
        ("Andrea", "Mejía", "F", "andrea.mejia@gmail.com"),
        ("Luis", "Mendoza", "M", "luis.mendoza@live.com"),
        ("Sofía", "Castro", "F", "sofia.castro@gmail.com"),
        ("Javier", "Ordoñez", "M", "javier.ordonez@hnmail.com"),
    ]

    base_datetime = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
    motivos = ["Chequeo general", "Dolor abdominal", "Revisión anual", "Control de diabetes", "Dolor de garganta"]

    for i, (nombre, apellido, genero, email) in enumerate(nombres):
        dni = f"08011990{i+1000}"
        telefono = f"9876-55{i:02d}"
        direccion = f"Colonia Ejemplo #{i+1}, Tegucigalpa"

        # Crear usuario si no existe
        user, _ = User.objects.get_or_create(
            username=dni,
            defaults={"first_name": nombre, "last_name": apellido}
        )

        # Crear paciente si no existe
        paciente, _ = Paciente.objects.get_or_create(
            user=user,
            defaults={
                "nombre": nombre,
                "apellido": apellido,
                "genero": genero,
                "fecha_nacimiento": "1990-01-01",
                "dni": dni,
                "telefono": telefono,
                "direccion": direccion,
                "email": email,
            }
        )

        # Crear entre 2 y 4 citas por paciente (mezclando pasadas y futuras)
        for _ in range(random.randint(2, 4)):
            dias_offset = random.randint(-30, 15)  # citas entre 30 días atrás y 15 días adelante
            fecha_cita = base_datetime + timedelta(days=dias_offset, hours=random.randint(0, 6))
            motivo = random.choice(motivos)

            cita = Cita.objects.create(
                paciente=paciente,
                medico=medico,
                fecha_hora=fecha_cita,
                motivo=motivo,
                estado="Completada" if dias_offset < 0 else "Pendiente"
            )

            # Evaluación Física
            EvaluacionFisica.objects.create(
                cita=cita,
                temperatura=f"{round(random.uniform(36.0, 37.5), 1)} °C",
                peso=f"{round(random.uniform(50, 90), 1)} kg",
                estatura=f"{round(random.uniform(1.50, 1.85), 2)} m",
                presion_arterial="120/80 mmHg",
                frecuencia_cardiaca=f"{random.randint(60, 100)} bpm"
            )

            # Diagnóstico (solo si la cita ya pasó)
            if dias_offset < 0:
                Diagnostico.objects.create(
                    cita=cita,
                    descripcion=random.choice([
                        "Resfriado común",
                        "Hipertensión controlada",
                        "Gastritis leve",
                        "Chequeo sin novedades"
                    ])
                )

                receta = Receta.objects.create(
                    cita=cita,
                    recomendaciones_generales="Reposo, hidratación y buena alimentación."
                )

                medicamentos = [
                    ("Paracetamol 500mg", "1 tableta cada 8 horas por 3 días"),
                    ("Ibuprofeno 400mg", "1 tableta cada 12 horas por 5 días"),
                    ("Amoxicilina 500mg", "1 cápsula cada 8 horas por 7 días")
                ]

                for med in random.sample(medicamentos, 2):
                    RecetaMedicamento.objects.create(
                        receta=receta,
                        medicamento=med[0],
                        dosis=med[1]
                    )

    return HttpResponse("✅ Datos de demo creados: pacientes con citas pasadas y futuras.")
