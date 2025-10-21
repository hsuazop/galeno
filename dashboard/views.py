import json
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
from core.forms import OdontogramaForm


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

    pacientes_relaciones = MedicoPaciente.objects.filter(medico=medico)

    # Total de pacientes asignados
    total_pacientes = pacientes_relaciones.count()

    # Total de citas asignadas a este médico
    total_citas = Cita.objects.filter(medico=request.user.medico).count()

    return render(request, 'dashboard/medico_dashboard.html', {'total_pacientes': total_pacientes,
                                                               'total_citas': total_citas, 'pacientes': pacientes_relaciones})


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


# def crear_cita_paciente(request, paciente_id):
#     paciente = get_object_or_404(Paciente, id=paciente_id)
#     medico = request.user.medico  # Asegúrate que Medico esté vinculado al user
#
#     if request.method == 'POST':
#         cita = Cita.objects.create(
#             paciente=paciente,
#             medico=medico,
#             estado='Borrador'
#         )
#
#         # 🔹 Mantengo EXACTO tu bloque de redirect por especialidad
#         especialidad_nombre = (medico.especialidad.nombre if medico.especialidad else '').strip().lower()
#
#         if especialidad_nombre == 'medico':
#             return redirect('dashboard:editar_cita_medico', paciente_id=paciente.id, cita_id=cita.id)
#         elif especialidad_nombre == 'odontologo':
#             return redirect('dashboard:editar_cita_odontologo', paciente_id=paciente.id, cita_id=cita.id)
#         elif especialidad_nombre == 'psicologo':
#             return redirect('dashboard:editar_cita_psicologo', paciente_id=paciente.id, cita_id=cita.id)
#         elif especialidad_nombre == 'nutricionista':
#             return redirect('dashboard:editar_cita_nutricionista', paciente_id=paciente.id, cita_id=cita.id)
#         else:
#             return redirect('dashboard:editar_cita', paciente_id=paciente.id, cita_id=cita.id)


# def crear_cita_con_paciente(request):
#     medico = request.user.medico  # Asegúrate que sea un médico autenticado
#
#     if request.method == 'POST':
#         dni = request.POST['dni'].strip()
#         email = request.POST['email'].strip()
#
#         with transaction.atomic():
#             # Verificar si el paciente ya existe
#             paciente = Paciente.objects.filter(dni=dni).first()
#             if not paciente:
#                 # Crear usuario
#                 username = email if email else dni
#                 user = User.objects.create_user(
#                     username=username,
#                     email=email,
#                     first_name=request.POST['nombre'].strip(),
#                     last_name=request.POST['apellido'].strip()
#                 )
#
#                 # Crear paciente
#                 paciente = Paciente.objects.create(
#                     user=user,
#                     nombre=request.POST['nombre'].strip(),
#                     apellido=request.POST['apellido'].strip(),
#                     fecha_nacimiento=request.POST.get('fecha_nacimiento'),
#                     genero=request.POST.get('genero'),
#                     dni=dni,
#                     telefono=request.POST.get('telefono', '').strip(),
#                     direccion=request.POST.get('direccion', '').strip(),
#                     email=email
#                 )
#
#             # Crear cita
#             cita = Cita.objects.create(
#                 paciente=paciente,
#                 medico=medico,
#                 fecha_hora=timezone.now(),
#                 motivo=request.POST.get('motivo', '').strip(),
#                 notas_medico=request.POST.get('notas_medico', '').strip(),
#                 estado='Completada'
#             )
#
#             # Evaluación física (solo si se ingresó algo)
#             if any([
#                 request.POST.get('temperatura'),
#                 request.POST.get('peso'),
#                 request.POST.get('estatura'),
#                 request.POST.get('presion_arterial'),
#                 request.POST.get('frecuencia_cardiaca')
#             ]):
#                 EvaluacionFisica.objects.create(
#                     cita=cita,
#                     temperatura=request.POST.get('temperatura', '').strip(),
#                     peso=request.POST.get('peso', '').strip(),
#                     estatura=request.POST.get('estatura', '').strip(),
#                     presion_arterial=request.POST.get('presion_arterial', '').strip(),
#                     frecuencia_cardiaca=request.POST.get('frecuencia_cardiaca', '').strip()
#                 )
#
#             # Diagnóstico (si se ingresó)
#             diagnostico_texto = request.POST.get('diagnostico', '').strip()
#             if diagnostico_texto:
#                 Diagnostico.objects.create(
#                     cita=cita,
#                     descripcion=diagnostico_texto
#                 )
#
#             # Receta y medicamentos
#             medicamentos = request.POST.getlist('medicamento')
#             dosis_list = request.POST.getlist('dosis')
#             recomendaciones = request.POST.get('recomendaciones', '').strip()
#
#             if any(nombre.strip() for nombre in medicamentos):
#                 receta = Receta.objects.create(
#                     cita=cita,
#                     recomendaciones_generales=recomendaciones
#                 )
#                 for nombre, dosis in zip(medicamentos, dosis_list):
#                     nombre = nombre.strip()
#                     dosis = dosis.strip()
#                     if nombre:
#                         RecetaMedicamento.objects.create(
#                             receta=receta,
#                             medicamento=nombre,
#                             dosis=dosis
#                         )
#
#         messages.success(
#             request,
#             f"Cita registrada para {paciente.nombre} {paciente.apellido} el {cita.fecha_hora.strftime('%d/%m/%Y a las %I:%M %p')}."
#         )
#         return redirect('ver_historial_paciente', paciente_id=paciente.id)
#
#     return render(request, 'dashboard/crear_cita_con_paciente.html')


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
from django.db import transaction, IntegrityError


@login_required
@transaction.atomic
def crear_paciente(request):
    medico = request.user.medico  # médico logueado

    if request.method == 'POST':
        form = PacienteCreateForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni'].strip()
            email = (form.cleaned_data.get('email') or '').lower()

            paciente = Paciente.objects.filter(dni=dni).first()
            created_user = False
            temp_password = None

            if paciente:
                # Si ya existe el paciente, solo aseguro la relación con el médico
                try:
                    _, rel_creada = MedicoPaciente.objects.get_or_create(
                        medico=medico, paciente=paciente
                    )
                    if rel_creada:
                        messages.success(request, f'Paciente existente asignado al médico.')
                    else:
                        messages.info(request, f'El paciente (DNI {dni}) ya estaba asignado a este médico.')
                except IntegrityError:
                    # Carrera: relación ya creada por otra transacción
                    pass

            else:
                # Crear User si no existe
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

                # Crear Paciente
                paciente = form.save(commit=False)
                paciente.user = user
                paciente.save()

                # Crear relación MedicoPaciente (idempotente)
                try:
                    MedicoPaciente.objects.get_or_create(medico=medico, paciente=paciente)
                except IntegrityError:
                    pass

                if created_user:
                    messages.success(
                        request,
                        f'Paciente creado. Usuario/DNI: {dni} | Contraseña temporal: {temp_password}'
                    )
                else:
                    messages.info(request, f'Paciente creado usando usuario existente (DNI {dni}).')

            # Crear SIEMPRE una cita en borrador
            cita = Cita.objects.create(
                paciente=paciente,
                medico=medico,
                estado='Borrador'
            )

            # 🔹 Mantengo EXACTO tu bloque de redirect por especialidad
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
    cita = get_object_or_404(Cita, id=cita_id, paciente=paciente)
    medico = getattr(request.user, 'medico', None)
    
    docs_paciente = Documentos.objects.filter(cita__paciente=paciente)

    diagnostico = getattr(cita, 'diagnostico', None)
    if not diagnostico:
        diagnostico = Diagnostico.objects.create(cita=cita, descripcion="")

    receta = getattr(cita, 'receta', None)
    if not receta:
        receta = Receta.objects.create(cita=cita, recomendaciones_generales="")

    medicamentos = medicamentos = receta.medicamentos.all()

    # Para la lista que ya mostrabas
    citas = Cita.objects.filter(paciente=paciente, medico=medico).order_by('-fecha_hora')


    instance = Odontograma.objects.filter(paciente=paciente, cita=cita).order_by('-id').first()

    # buscar el de la cita anterior
    if not instance:
        # Buscar la cita anterior completada (excluir la actual y borradores)
        cita_anterior = (Cita.objects.filter(paciente=paciente, medico=medico).exclude(id=cita.id).order_by('-fecha_hora').first())
        
        if cita_anterior:
            # Buscar odontograma de la cita anterior
            instance = Odontograma.objects.filter(paciente=paciente, cita=cita_anterior).order_by('-id').first()
            if instance:
                print(f"✅ Cargando odontograma de cita anterior ID: {cita_anterior.id}")
            else:
                print(f"⚠️ Cita anterior ID {cita_anterior.id} encontrada, pero sin odontograma")
        else:
            print("ℹ️ No hay citas anteriores para este paciente")
    else:
        print(f"✅ Usando odontograma existente de la cita actual ID: {cita.id}")



    if request.method == 'POST':
        docs = request.FILES.getlist("documentos")
        nombre_doc = request.POST.get("nombre_documento", "").strip()

        # form documentos
        if docs:
            for file in docs:
                Documentos.objects.create(
                    cita=cita,
                    nombre=nombre_doc if nombre_doc else file.name,
                    archivo=file
                )
            messages.success(request, f"✅ {len(docs)} documento(s) guardado(s) correctamente.")
            return redirect('dashboard:editar_cita_odontologo', paciente_id=paciente.id, cita_id=cita.id)

        # Si no hay documentos, procesar el form principal
        post_data = request.POST.copy()
        post_data['datos'] = request.POST.get('odontograma_json', '[]')
        form = OdontogramaForm(request.POST, instance=instance)

        if form.is_valid():
            od = form.save(commit=False)
            od.paciente = paciente
            od.medico = medico
            od.cita = cita

            # Si llega como string (por Textarea) normalizamos a lista
            if isinstance(od.datos, str):
                try:
                    od.datos = json.loads(od.datos)
                except Exception:
                    od.datos = []

            od.save()

            # Guardar motivo de la cita si viene en POST
            motivo = request.POST.get("motivo", "").strip()
            if motivo:
                cita.motivo = motivo
                cita.notas_medico = request.POST.get("notas_medico", "").strip()
                cita.estado = 'Programada'
                cita.save()
            
            #Guardar diagnóstico si viene en POST
            diagnostico_desc = request.POST.get("diagnostico", "").strip()
            if diagnostico_desc:
                diagnostico.descripcion = diagnostico_desc
                diagnostico.save()

            #Guardar recomendaciones en receta si viene en POST
            recomendaciones = request.POST.get("recomendaciones", "").strip()
            if recomendaciones:
                receta.recomendaciones_generales = recomendaciones
                receta.save()

            #guardar medicamentos en receta si vienen en POST
            medicamentos_nombres = request.POST.getlist("medicamento[]")
            medicamentos_dosis = request.POST.getlist("dosis[]")

            #Obtener medicametos actuales en la receta
            Lista_Meds = set(
                (m.medicamento.strip().lower(), m.dosis.strip().lower())
                for m in receta.medicamentos.all()
            )

            for nombre, dosis in zip(medicamentos_nombres, medicamentos_dosis):
                nombre_limpio = nombre.strip()
                dosis_limpia = dosis.strip()
                if not nombre_limpio:
                    continue
                clave = (nombre_limpio.lower(), dosis_limpia.lower())
                if clave not in Lista_Meds:
                    RecetaMedicamento.objects.create(
                        receta=receta,
                        medicamento=nombre_limpio,
                        dosis=dosis_limpia
                    )

            messages.success(request, "✅ Odontograma guardado correctamente.")
            return redirect('dashboard:editar_cita_odontologo', paciente_id=paciente.id, cita_id=cita.id)
        else:
            messages.error(request, "❌ Revisa el formulario.")
    else:
        
        form = OdontogramaForm(instance=instance)

    # JSON existente para precargar en el engine (array literal en JS)
    initial_data = instance.datos if instance else []
    odontograma_json_str = json.dumps(initial_data)
    
    # Debug final: mostrar qué se está enviando al template
    print(f"\n{'='*60}")
    print(f"🔍 DEBUG FINAL - Cita ID: {cita.id}")
    print(f"📊 JSON enviado al frontend: {odontograma_json_str}")
    print(f"📝 Total de dientes en odontograma: {len(initial_data)}")
    if instance:
        print(f"✅ Odontograma ID: {instance.id} (de Cita ID: {instance.cita.id})")
    else:
        print("⚠️ No hay odontograma (se enviará array vacío)")
    print(f"{'='*60}\n")

    #-- render para solo usar pantalla del odontograma original

    # return render(
    #     request,
    #     'dashboard/consulta_paciente_odontologo.html',
    #     {
    #         'paciente': paciente,
    #         'citas': citas,
    #         'form': form,
    #         'odontograma_json_str': odontograma_json_str,
    #         'cita': cita,
    #         'medicamentos': medicamentos,
    #     }
    # )

    #render para usar usar url del odontograma2
    template_name = 'dashboard/consulta_paciente_odontologo.html'
    if request.resolver_match.url_name == 'editar_cita_odontologo2':
        template_name = 'dashboard/consulta_paciente_odontologo2.html'

    return render(
        request,
        template_name,
        {
            'paciente': paciente,
            'citas': citas,
            'form': form,
            'odontograma_json_str': odontograma_json_str,
            'cita': cita,
            'medicamentos': medicamentos,
            'docs_paciente':docs_paciente,
        }
    )


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


@login_required
def crear_cita_borrador(request, paciente_id):
    if request.method != 'POST':
        return redirect('dashboard_medico')

    medico = request.user.medico
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Crea una cita mínima como borrador
    cita = Cita.objects.create(
        medico=medico,
        paciente=paciente,
        fecha_hora=timezone.now(),  # puedes poner None si tu modelo lo permite
        motivo='(Borrador)',
        # Variante A (si tienes choices de estado):
        estado='BORRADOR',
        # Variante B (si usas un booleano):
        # es_borrador=True,
    )

    messages.success(request, 'Borrador de cita creado. Completa los datos para guardarla definitivamente.')

    # Redirección al editor según la especialidad del médico
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
        return redirect('dashboard:editar_cita', paciente_id=paciente.id, cita_id=cita.id)

    # Fallback
    return redirect('editar_cita_medico', paciente_id=paciente.id, cita_id=cita.id)
