import os

from django.apps import AppConfig

class PrisesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prises'

    def ready(self):
        from .tache_horaire import start_scheduler
        start_scheduler()
        import threading
        from . import mqtt_listener

        thread = threading.Thread(target=mqtt_listener.start_listener, daemon=True)
        thread.start()
        print("[MQTT] mqtt_listener démarré depuis ready()")
