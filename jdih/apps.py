from django.apps import AppConfig


class JdihConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jdih"

    def ready(self):
        from . import signals
