from django.apps import AppConfig


class EcommerceSyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ecommerce_sync'
    verbose_name = 'Sincronización e-commerce (PrestaShop)'

    def ready(self):
        from . import signals
        signals.connect_signals()
