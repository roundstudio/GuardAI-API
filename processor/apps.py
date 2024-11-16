from django.apps import AppConfig


class ProcessorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'processor'

    def ready(self):
        from processor.scheduler import start
        start()
