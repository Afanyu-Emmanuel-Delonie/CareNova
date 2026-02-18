from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

class ProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles'

    def ready(self):
        import signals