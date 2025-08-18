# AUTH/apps.py
from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AUTH'
    verbose_name = 'Autenticación'
    
    def ready(self):
        pass