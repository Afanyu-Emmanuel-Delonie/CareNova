from django.apps import AppConfig


class ProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles' 

    def ready(self):
        # Using a relative import often fixes the 'could not be resolved' error
        from . import signals