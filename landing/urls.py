from django.urls import path

from landing.views import *

urlpatterns = [
    path("", index, name="index"),
    path("ingresar", ingresar, name="ingresar"),
    path("registrar", registrar, name="registrar"),
    path("cita", cita, name="cita"),
    path('activar/<uidb64>/<token>/', activar_cuenta, name='activar_cuenta'),
    # path('activar/<uidb64>/<token>/', activar_cuenta, name='activar_cuenta'),
    path('probar-correo/', enviar_correo_prueba, name='probar_correo'),

]
