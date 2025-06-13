from django.apps import AppConfig


class GigsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'GIGS'
    verbose_name = 'Gestión de Eventos Musicales'
    
    def ready(self):
        """Importar señales cuando la aplicación esté lista"""
        import GIGS.signals