from django.urls import path

from dashboard.views import *

urlpatterns = [

    path('paciente/', dashboard_paciente, name='dashboard_paciente'),
    path('medico/', dashboard_medico, name='dashboard_medico'),
    path('asistente/', dashboard_asistente, name='dashboard_asistente'),
    path('paciente/<int:paciente_id>/historial/', ver_historial_paciente, name='ver_historial_paciente'),
    path('paciente/<int:paciente_id>/crear/', crear_cita_paciente, name='crear_cita'),
    path('medico/crear-cita/', crear_cita_con_paciente, name='crear_cita_con_paciente'),
    path('medico/citas/', ver_citas_medico, name='ver_citas_medico'),
    path('logout/', logout_view, name='logout'),

]