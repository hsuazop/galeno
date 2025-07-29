from django.urls import path

from utils.views import *

urlpatterns = [

    path('crear_datos_demo_galeno/', crear_datos_demo_galeno, name='crear_datos_demo_galeno'),


]