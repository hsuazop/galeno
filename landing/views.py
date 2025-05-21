from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request, "landing/index.html", {})

def registrar(request):
    return render(request, "landing/registrar.html", {})

def ingresar(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if hasattr(user, 'paciente'):
                return redirect('dashboard_paciente')  # nombre de la URL para pacientes
            elif hasattr(user, 'medico'):
                return redirect('dashboard_medico')    # nombre de la URL para médicos
            elif hasattr(user, 'asistente'):
                return redirect('dashboard_asistente') # nombre de la URL para asistentes
            else:
                messages.error(request, "El usuario no tiene un rol asignado.")
                return redirect('login')
        else:
            messages.error(request, "Credenciales incorrectas.")
            return redirect('login')
    return render(request, "landing/ingresar.html", {})

def cita(request):
    return render(request, "landing/cita.html", {})