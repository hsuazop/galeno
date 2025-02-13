from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
def index(request):
    return render(request, "dashboard/login.html", {})

def index(request):
    return render(request, "landing/index.html", {})