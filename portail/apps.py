import sys

import config
import log
cfg = config.init("config.json")
if cfg.is_default:
    cfg.write("config.json")
log.init(log.Log.INFO)



from django.apps import AppConfig


class PortailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portail'

    def ready(self, *args, **kwargs):
        if 'runserver' in sys.argv:
            from portail.views import serv
            serv.init()
