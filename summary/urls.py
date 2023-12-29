from django.urls import path
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register("board",BoardViewSet)

app_name = "summary"
urlpatterns = [
    path("",views.index, name="summary"),    
    path("real_estate/",views.real_estate,name="real_estate"),
    path("gold_rate/",views.gold_rate,name="gold_rate"),
    path("exchange_rate/",views.exchange_rate,name="exchange_rate"),
    path("coin/",views.coin,name="coin"),
    path("gold_chatbot/",views.gold_chatbot,name="gold_chatbot"),
]