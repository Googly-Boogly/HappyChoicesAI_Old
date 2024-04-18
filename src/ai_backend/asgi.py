import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ai_backend.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_backend.settings')

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  # Define WebSocket protocol routing
  "websocket": AuthMiddlewareStack(
        URLRouter(
            ai_backend.routing.websocket_urlpatterns
        )
    ),
})
