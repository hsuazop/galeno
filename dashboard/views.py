from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from core.models import *
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from datetime import date

def calcular_edad(fecha_nacimiento):
    if not fecha_nacimiento:
        return None
    today = date.today()
    return today.year - fecha_nacimiento.year - (
        (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )

# Create your views here.
def login(request):
    return render(request, "dashboard/login.html", {})

@login_required
def dashboard_paciente(request):
    return render(request, 'paciente_dashboard.html')

@login_required
def dashboard_medico(request):
    medico = request.user.medico  # gracias al related_name='medico'
    pacientes = Paciente.objects.filter(cita__medico=request.user.medico).distinct()
    return render(request, 'dashboard/medico_dashboard.html', {'pacientes': pacientes})

@login_required
def dashboard_asistente(request):
    return render(request, 'asistente_dashboard.html')

def ver_historial_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    citas = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora')
    edad = calcular_edad(paciente.fecha_nacimiento)

    return render(request, 'dashboard/historial_paciente.html', {
        'paciente': paciente,
        'citas': citas,
        'edad': edad,
    })


def crear_cita_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    medico = request.user.medico

    if request.method == 'POST':

        with transaction.atomic():
            cita = Cita.objects.create(
                paciente=paciente,
                medico=medico,
                fecha_hora=timezone.now(),
                motivo=request.POST.get('motivo', ''),
                notas_medico=request.POST.get('notas_medico', ''),
                estado='Completada'
            )

            EvaluacionFisica.objects.create(
                cita=cita,
                temperatura=request.POST.get('temperatura'),
                peso=request.POST.get('peso'),
                estatura=request.POST.get('estatura'),
                presion_arterial=request.POST.get('presion_arterial'),
                frecuencia_cardiaca=request.POST.get('frecuencia_cardiaca')
            )

            Diagnostico.objects.create(
                cita=cita,
                descripcion=request.POST.get('diagnostico', '')
            )

            receta = Receta.objects.create(
                cita=cita,
                recomendaciones_generales=request.POST.get('recomendaciones', '')
            )

            for nombre, dosis in zip(request.POST.getlist('medicamento'), request.POST.getlist('dosis')):
                if nombre.strip():
                    medicamento, _ = Medicamento.objects.get_or_create(nombre=nombre.strip())
                    RecetaMedicamento.objects.create(
                        receta=receta,
                        medicamento=medicamento,
                        dosis=dosis.strip()
                    )


        # Agrega el mensaje
        messages.success(
            request,
            f"Cita registrada para {paciente.nombre} {paciente.apellido} el {cita.fecha_hora.strftime('%d/%m/%Y a las %I:%M %p')}."
        )
        try:
            return redirect('ver_historial_paciente', paciente_id=paciente.id)
        except Exception as e:
            return HttpResponse(f"Error en redirección: {e}")


    citas = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora')[:3]
    return render(request, 'dashboard/consulta_paciente.html', {'paciente': paciente, 'citas': citas})


def crear_cita_con_paciente(request):
    medico = request.user.medico  # Asegúrate que sea un médico autenticado

    if request.method == 'POST':
        dni = request.POST['dni']
        email = request.POST['email']

        with transaction.atomic():
            # Verificar si el paciente ya existe
            paciente = Paciente.objects.filter(dni=dni).first()
            if not paciente:
                # Crear usuario básico
                user = User.objects.create(
                    username=dni,
                    first_name=request.POST['nombre'],
                    last_name=request.POST['apellido']
                )
                # Crear paciente
                paciente = Paciente.objects.create(
                    user=user,
                    nombre=request.POST['nombre'],
                    apellido=request.POST['apellido'],
                    fecha_nacimiento=request.POST['fecha_nacimiento'],
                    genero=request.POST['genero'],
                    dni=dni,
                    telefono=request.POST['telefono'],
                    direccion=request.POST['direccion'],
                    email=email
                )

            # Crear cita
            cita = Cita.objects.create(
                paciente=paciente,
                medico=medico,
                fecha_hora=timezone.now(),
                motivo=request.POST.get('motivo', ''),
                notas_medico=request.POST.get('notas_medico', ''),
                estado='Completada'
            )

            # Evaluación física
            EvaluacionFisica.objects.create(
                cita=cita,
                temperatura=request.POST.get('temperatura'),
                peso=request.POST.get('peso'),
                estatura=request.POST.get('estatura'),
                presion_arterial=request.POST.get('presion_arterial'),
                frecuencia_cardiaca=request.POST.get('frecuencia_cardiaca')
            )

            # Diagnóstico
            Diagnostico.objects.create(
                cita=cita,
                descripcion=request.POST.get('diagnostico', '')
            )

            # Receta
            receta = Receta.objects.create(
                cita=cita,
                recomendaciones_generales=request.POST.get('recomendaciones', '')
            )

            # Medicamentos
            nombres = request.POST.getlist('medicamento')
            dosis_list = request.POST.getlist('dosis')

            for nombre, dosis in zip(nombres, dosis_list):
                if nombre.strip():
                    medicamento, _ = Medicamento.objects.get_or_create(nombre=nombre.strip())
                    RecetaMedicamento.objects.create(
                        receta=receta,
                        medicamento=medicamento,
                        dosis=dosis.strip()
                    )

        # Mensaje personalizado
        messages.success(
            request,
            f"Cita registrada para {paciente.nombre} {paciente.apellido} el {cita.fecha_hora.strftime('%d/%m/%Y a las %I:%M %p')}."
        )
        return redirect('ver_historial_paciente', paciente_id=paciente.id)
        # return HttpResponseRedirect(url)

    return render(request, 'dashboard/crear_cita_con_paciente.html')


@login_required
def ver_citas_medico(request):
    medico = request.user.medico

    # Todas las citas de este médico
    citas = Cita.objects.filter(medico=medico).order_by('-fecha_hora')

    # Estadísticas
    total_citas = citas.count()
    total_pacientes = citas.values('paciente').distinct().count()
    completadas = citas.filter(estado='Completada').count()
    pendientes = citas.filter(estado='Pendiente').count()
    canceladas = citas.filter(estado='Cancelada').count()

    context = {
        'citas': citas,
        'total_citas': total_citas,
        'total_pacientes': total_pacientes,
        'completadas': completadas,
        'pendientes': pendientes,
        'canceladas': canceladas,
    }

    return render(request, 'dashboard/citas_medico.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')  # o cambia 'login' por la URL que desees redirigir

