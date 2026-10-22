from django.apps import AppConfig


class Currierconfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'currier'

    def ready(self) -> None:
        import currier.signals
