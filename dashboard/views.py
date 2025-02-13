from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
def login(request):
    return render(request, "dashboard/login.html", {})


def dashboard(request):
    return render(request, "dashboard/dashboard.html", {})