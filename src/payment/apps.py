from django.apps import AppConfig


class PaymentConfig(AppConfig):
    name = 'payment'

    def ready(self) -> None:
        from . import signals