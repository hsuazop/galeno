from django.urls import path

from landing.views import *

urlpatterns = [
    path("", index, name="index"),
    path("ingresar", ingresar, name="ingresar"),
    path("registrar", registrar, name="registrar"),
    path("cita", cita, name="cita"),

]