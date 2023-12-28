from django.urls import path
from rest_framework import routers
from . import views
from . import consumers

app_name = "simulation"
urlpatterns = [
    path('',views.index,name='index'),
    path('myreport/',views.my_report,name="myreport"),
    
    
]