# userAPI/apps.py
from django.apps import AppConfig


class UserapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userAPI'

    def ready(self):
        import userAPI.signals