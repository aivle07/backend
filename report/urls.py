from django.urls import path
from rest_framework import routers
from . import views


app_name = "report"
urlpatterns = [
    path("", views.report, name="report"),
]