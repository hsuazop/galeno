from django.urls import path

from dashboard.views import *

urlpatterns = [

    path('paciente/', dashboard_paciente, name='dashboard_paciente'),
    path('medico/', dashboard_medico, name='dashboard_medico'),
    path('asistente/', dashboard_asistente, name='dashboard_asistente'),

]