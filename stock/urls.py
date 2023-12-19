from django.urls import path
from rest_framework import routers
from . import views

app_name = "stock"
urlpatterns = [
    path('',views.StockRetrieveAPI,name='stock-retrieve'),
]