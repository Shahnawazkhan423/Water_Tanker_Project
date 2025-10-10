from django.apps import AppConfig


class SupplierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Supplier'
    def ready(self):
        import Supplier.receivers 