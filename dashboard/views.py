from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


# Create your views here.
def login(request):
    return render(request, "dashboard/login.html", {})

@login_required
def dashboard_paciente(request):
    return render(request, 'paciente_dashboard.html')

@login_required
def dashboard_medico(request):
    return render(request, 'dashboard/medico_dashboard.html')

@login_required
def dashboard_asistente(request):
    return render(request, 'asistente_dashboard.html')



