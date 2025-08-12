from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from landing.forms import RegistroMedicoForm
from core.models import Especialidad, Medico

# Create your views here.
def index(request):
    return render(request, "landing/index.html", {})

def registrar(request):
    especialidades = Especialidad.objects.all()

    if request.method == 'POST':
        data = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'password_confirm': request.POST.get('password_confirm'),
            'nombre': request.POST.get('nombre'),
            'apellido': request.POST.get('apellido'),
            'telefono': request.POST.get('telefono'),
            'especialidad_id': request.POST.get('especialidad_id'),
            'acepta_terminos': request.POST.get('acepta_terminos'),
        }

        form = RegistroMedicoForm(data)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            telefono = form.cleaned_data['telefono']
            especialidad_id = form.cleaned_data['especialidad_id']


            # Crear usuario (inactivo hasta verificar)
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_active=False
            )

            # Crear perfil médico
            Medico.objects.create(
                user=user,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                email=email,
                especialidad_id=especialidad_id if especialidad_id else None,
            )

            # Enviar correo de activación
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = f"http://{current_site.domain}/activar/{uid}/{token}/"
            mensaje = f"Hola {user.username},\n\nActiva tu cuenta en Galeno haciendo clic en el siguiente enlace:\n{link}"

            send_mail(
                'Activa tu cuenta en Galeno',
                mensaje,
                None,
                [email]
            )

            messages.success(request, "Registro exitoso. Revisa tu correo para activar tu cuenta.")
            return redirect('registrar')
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)

    return render(request, 'landing/registrar.html', {
        'especialidades': especialidades
    })


def activar_cuenta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            send_mail(
                'Tu cuenta en Galeno ha sido activada',
                f"Hola {user.username}, tu cuenta ha sido activada con éxito. Ya puedes iniciar sesión en el sistema Galeno.",
                None,
                [user.email]
            )
            messages.success(request, "Tu cuenta ha sido activada correctamente. Ahora puedes iniciar sesión.")
        else:
            messages.info(request, "Tu cuenta ya está activada.")
        return redirect('ingresar')  # Cambia 'login' al nombre de tu vista de inicio de sesión
    else:
        messages.error(request, "El enlace de activación no es válido o ha expirado.")
        return redirect('registrar')  # Redirige a donde prefieras si falla


def ingresar(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        print(username)
        print(password)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if hasattr(user, 'paciente'):
                return redirect('dashboard:dashboard_paciente')  # nombre de la URL para pacientes
            elif hasattr(user, 'medico'):
                return redirect('dashboard:dashboard_medico')    # nombre de la URL para médicos
            elif hasattr(user, 'asistente'):
                return redirect('dashboard:dashboard_asistente') # nombre de la URL para asistentes
            else:
                messages.error(request, "El usuario no tiene un rol asignado.")
                return redirect('ingresar')
        else:
            messages.error(request, "Credenciales incorrectas.")
            return redirect('ingresar')
    return render(request, "landing/ingresar.html", {})

def cita(request):
    return render(request, "landing/cita.html", {})


def enviar_correo_prueba(request):
    try:
        send_mail(
            subject='Correo de prueba desde Galeno',
            message='Este es un mensaje de prueba enviado desde Django usando Opalstack.',
            from_email=None,  # usa DEFAULT_FROM_EMAIL de settings.py
            recipient_list=['hectorsp25@gmail.com'],  # 👈 cambia esto por tu correo real
            fail_silently=False,
        )
        return HttpResponse("✅ Correo enviado correctamente.")
    except Exception as e:
        return HttpResponse(f"❌ Error al enviar el correo: {e}", status=500)