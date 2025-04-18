from django.apps import AppConfig


class MarketingConfig(AppConfig):
    name = 'marketing'
    
    def ready(self) -> None:
        import marketing.signals
