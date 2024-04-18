from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/audio/tts', consumers.AudioConsumer.as_asgi()),
    path('ws/audio/stt', consumers.SpeechToTextConsumer.as_asgi()),
]
