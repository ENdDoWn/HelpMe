import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ticket.routing  # 👈 make sure this works

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatproject.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ticket.routing.websocket_urlpatterns
        )
    ),
})
