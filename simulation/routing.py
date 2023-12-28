# routing.py

from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/graph/', consumers.GraphConsumer.as_asgi()),
]
