"""Entrada ASGI (no la usamos ahora, va por si añadimos websockets en el futuro)."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
