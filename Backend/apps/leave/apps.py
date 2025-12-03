from django.apps import AppConfig


class LeaveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.leave'

    def ready(self):
        import apps.leave.signals  # Import signals
