from django.apps import AppConfig


class PlaceAzeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'place_aze'

    def ready(self):
        import place_aze.signals