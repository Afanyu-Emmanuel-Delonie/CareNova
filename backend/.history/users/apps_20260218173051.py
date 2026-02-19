from django.apps import AppConfig


class ProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles' # Or 'users' if everything is in one app

    def ready(self):
        # Use the full dotted path to your signals file
