from django.urls import path

from dashboard.views import *

urlpatterns = [
    path("login", login, name="login"),
    path("dashboard", dashboard, name="dashboard"),

]