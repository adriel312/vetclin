"""
ASGI config — ponto de entrada para servidores assíncronos (ex: Uvicorn).
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application()
