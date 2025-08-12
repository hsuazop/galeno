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
from core.forms import PacienteCreateForm

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
    return redirect('ingresar')  # o cambia 'login' por la URL que desees redirigir


from django.db.models import Count
def estadisticas_galeno(request):
    # Totales
    total_pacientes = Paciente.objects.count()
    total_citas = Cita.objects.count()
    citas_pendientes = Cita.objects.filter(estado="Pendiente").count()
    citas_completadas = Cita.objects.filter(estado="Completada").count()

    # Citas por paciente (los 10 primeros)
    citas_por_paciente = (
        Cita.objects.values("paciente__nombre", "paciente__apellido")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    # Datos para Google Charts
    data_citas_paciente = [
        ["Paciente", "Citas"]
    ]
    for item in citas_por_paciente:
        nombre = f"{item['paciente__nombre']} {item['paciente__apellido']}"
        data_citas_paciente.append([nombre, item["total"]])

    data_estado_citas = [
        ["Estado", "Cantidad"],
        ["Pendientes", citas_pendientes],
        ["Completadas", citas_completadas],
    ]

    context = {
        "total_pacientes": total_pacientes,
        "total_citas": total_citas,
        "citas_pendientes": citas_pendientes,
        "citas_completadas": citas_completadas,
        "data_citas_paciente": data_citas_paciente,
        "data_estado_citas": data_estado_citas,
    }
    return render(request, "dashboard/estadistica.html", context)


from django.urls import reverse

@login_required
@transaction.atomic
def crear_paciente(request):
    medico = request.user.medico  # médico logueado

    if request.method == 'POST':
        form = PacienteCreateForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni'].strip()
            email = (form.cleaned_data.get('email') or '').lower() or ''

            # 1) Reutilizar paciente por DNI dentro del médico logueado
            paciente = Paciente.objects.filter(dni=dni).first()
            created_user = False
            temp_password = None

            if not paciente:
                # 2) Reutilizar o crear User con username = DNI
                user = User.objects.filter(username=dni).first()
                if not user:
                    temp_password = User.objects.make_random_password()
                    user = User.objects.create_user(
                        username=dni,
                        password=temp_password,
                        first_name=form.cleaned_data['nombre'],
                        last_name=form.cleaned_data['apellido'],
                        email=email
                    )
                    created_user = True

                # 3) Crear Paciente ligado al médico logueado
                paciente = form.save(commit=False)
                paciente.user = user
                paciente.medico = medico
                paciente.save()

                if created_user:
                    messages.success(
                        request,
                        f'Paciente creado. Usuario/DNI: {dni} | Contraseña temporal: {temp_password}'
                    )
                else:
                    messages.info(request, f'Paciente creado usando usuario existente (DNI {dni}).')
            else:
                messages.info(request, f'Paciente existente reutilizado (DNI {dni}).')

            # 4) Crear SIEMPRE una Cita en estado Borrador
            cita = Cita.objects.create(
                paciente=paciente,
                medico=medico,
                estado='Borrador'
            )

            # # 5) Redirección según especialidad (incluye paciente y cita en la URL)
            # especialidad_nombre = (medico.especialidad.nombre if medico.especialidad else '').strip().lower()
            # route_by_spec = {
            #     'medico': 'editar_cita_medico',
            #     'odontologo': 'editar_cita_odontologo',
            #     'psicologo': 'editar_cita_psicologo',
            #     'nutricionista': 'editar_cita_nutricionista',
            # }
            # url_name = route_by_spec.get(especialidad_nombre, 'editar_cita')  # fallback
            #
            # return redirect(url_name, paciente_id=paciente.id, cita_id=cita.id)

            # 5) Redirección por especialidad (usando kwargs en el path)
            especialidad_nombre = (medico.especialidad.nombre if medico.especialidad else '').strip().lower()

            if especialidad_nombre == 'medico':
                return redirect('dashboard:editar_cita_medico', paciente_id=paciente.id, cita_id=cita.id)
            elif especialidad_nombre == 'odontologo':
                return redirect('dashboard:editar_cita_odontologo', paciente_id=paciente.id, cita_id=cita.id)
            elif especialidad_nombre == 'psicologo':
                return redirect('dashboard:editar_cita_psicologo', paciente_id=paciente.id, cita_id=cita.id)
            elif especialidad_nombre == 'nutricionista':
                return redirect('dashboard:editar_cita_nutricionista', paciente_id=paciente.id, cita_id=cita.id)
            else:
                # Fallback genérico
                return redirect('dashboard:editar_cita', paciente_id=paciente.id, cita_id=cita.id)

    else:
        form = PacienteCreateForm()

    return render(request, 'dashboard/crear_paciente.html', {'form': form})


def editar_cita_medico(request, paciente_id, cita_id):
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


def editar_cita_odontologo(request, paciente_id, cita_id):
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


def editar_cita_psicologo(request, paciente_id, cita_id):
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


def editar_cita_nutricionista(request, paciente_id, cita_id):
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
