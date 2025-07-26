# AUTH/apps.py
from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AUTH'

    def ready(self):
        import AUTH.signals