from django.apps import AppConfig

class ComunicacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comunicacion'
    
    def ready(self):
        import comunicacion.signals  # Importa las señales