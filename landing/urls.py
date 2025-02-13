from django.urls import path

from landing.views import *

urlpatterns = [
    path("", index, name="index"),

]