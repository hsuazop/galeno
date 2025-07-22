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
    # Total de pacientes registrados (con al menos una cita con este médico)
    total_pacientes = Paciente.objects.filter(cita__medico=request.user.medico).distinct().count()

    # Total de citas asignadas a este médico
    total_citas = Cita.objects.filter(medico=request.user.medico).count()


    return render(request, 'dashboard/medico_dashboard.html', { 'total_pacientes': total_pacientes,
        'total_citas': total_citas, 'pacientes': pacientes})

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
    medico = request.user.medico  # Asegúrate que Medico esté vinculado al user

    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()

        if not motivo:
            messages.error(request, "El motivo de la cita es obligatorio.")
            return redirect(request.path)

        with transaction.atomic():
            cita = Cita.objects.create(
                paciente=paciente,
                medico=medico,
                fecha_hora=timezone.now(),
                motivo=motivo,
                notas_medico=request.POST.get('notas_medico', '').strip(),
                estado='Completada'
            )

            # Evaluación física (solo si algún campo tiene valor)
            if any([
                request.POST.get('temperatura'),
                request.POST.get('peso'),
                request.POST.get('estatura'),
                request.POST.get('presion_arterial'),
                request.POST.get('frecuencia_cardiaca')
            ]):
                EvaluacionFisica.objects.create(
                    cita=cita,
                    temperatura=request.POST.get('temperatura', '').strip(),
                    peso=request.POST.get('peso', '').strip(),
                    estatura=request.POST.get('estatura', '').strip(),
                    presion_arterial=request.POST.get('presion_arterial', '').strip(),
                    frecuencia_cardiaca=request.POST.get('frecuencia_cardiaca', '').strip()
                )

            # Diagnóstico (opcional)
            descripcion = request.POST.get('diagnostico', '').strip()
            if descripcion:
                Diagnostico.objects.create(
                    cita=cita,
                    descripcion=descripcion
                )

            # Receta y medicamentos (opcional)
            medicamentos = request.POST.getlist('medicamento[]')
            dosis_list = request.POST.getlist('dosis[]')
            recomendaciones = request.POST.get('recomendaciones', '').strip()

            if any(m.strip() for m in medicamentos):
                receta = Receta.objects.create(
                    cita=cita,
                    recomendaciones_generales=recomendaciones
                )
                for nombre, dosis in zip(medicamentos, dosis_list):
                    nombre = nombre.strip()
                    dosis = dosis.strip()
                    if nombre:
                        RecetaMedicamento.objects.create(
                            receta=receta,
                            medicamento=nombre,  # CharField, ya no es FK
                            dosis=dosis
                        )

        messages.success(
            request,
            f"Cita registrada para {paciente.nombre} {paciente.apellido} el {cita.fecha_hora.strftime('%d/%m/%Y a las %I:%M %p')}."
        )
        return redirect('ver_historial_paciente', paciente_id=paciente.id)

    # Mostrar últimas citas
    # citas = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora')[:3]
    return render(request, 'dashboard/consulta_paciente.html', {'paciente': paciente})



def crear_cita_con_paciente(request):
    medico = request.user.medico  # Asegúrate que sea un médico autenticado

    if request.method == 'POST':
        dni = request.POST['dni'].strip()
        email = request.POST['email'].strip()

        with transaction.atomic():
            # Verificar si el paciente ya existe
            paciente = Paciente.objects.filter(dni=dni).first()
            if not paciente:
                # Crear usuario
                username = email if email else dni
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=request.POST['nombre'].strip(),
                    last_name=request.POST['apellido'].strip()
                )

                # Crear paciente
                paciente = Paciente.objects.create(
                    user=user,
                    nombre=request.POST['nombre'].strip(),
                    apellido=request.POST['apellido'].strip(),
                    fecha_nacimiento=request.POST.get('fecha_nacimiento'),
                    genero=request.POST.get('genero'),
                    dni=dni,
                    telefono=request.POST.get('telefono', '').strip(),
                    direccion=request.POST.get('direccion', '').strip(),
                    email=email
                )

            # Crear cita
            cita = Cita.objects.create(
                paciente=paciente,
                medico=medico,
                fecha_hora=timezone.now(),
                motivo=request.POST.get('motivo', '').strip(),
                notas_medico=request.POST.get('notas_medico', '').strip(),
                estado='Completada'
            )

            # Evaluación física (solo si se ingresó algo)
            if any([
                request.POST.get('temperatura'),
                request.POST.get('peso'),
                request.POST.get('estatura'),
                request.POST.get('presion_arterial'),
                request.POST.get('frecuencia_cardiaca')
            ]):
                EvaluacionFisica.objects.create(
                    cita=cita,
                    temperatura=request.POST.get('temperatura', '').strip(),
                    peso=request.POST.get('peso', '').strip(),
                    estatura=request.POST.get('estatura', '').strip(),
                    presion_arterial=request.POST.get('presion_arterial', '').strip(),
                    frecuencia_cardiaca=request.POST.get('frecuencia_cardiaca', '').strip()
                )

            # Diagnóstico (si se ingresó)
            diagnostico_texto = request.POST.get('diagnostico', '').strip()
            if diagnostico_texto:
                Diagnostico.objects.create(
                    cita=cita,
                    descripcion=diagnostico_texto
                )

            # Receta y medicamentos
            medicamentos = request.POST.getlist('medicamento')
            dosis_list = request.POST.getlist('dosis')
            recomendaciones = request.POST.get('recomendaciones', '').strip()

            if any(nombre.strip() for nombre in medicamentos):
                receta = Receta.objects.create(
                    cita=cita,
                    recomendaciones_generales=recomendaciones
                )
                for nombre, dosis in zip(medicamentos, dosis_list):
                    nombre = nombre.strip()
                    dosis = dosis.strip()
                    if nombre:
                        RecetaMedicamento.objects.create(
                            receta=receta,
                            medicamento=nombre,
                            dosis=dosis
                        )

        messages.success(
            request,
            f"Cita registrada para {paciente.nombre} {paciente.apellido} el {cita.fecha_hora.strftime('%d/%m/%Y a las %I:%M %p')}."
        )
        return redirect('ver_historial_paciente', paciente_id=paciente.id)

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

