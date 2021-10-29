import json
import os
import signal

from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt

import config
from portail.views import BaseHandler
from portail.views.base import need_auth_api
from subsonic.subsonic import Subsonic


class ServerHandler(BaseHandler):

    def __init__(self, queue_handler, sub_handler):
        self.queue_handler = queue_handler
        self.sub_handler = sub_handler



    @need_auth_api
    @csrf_exempt
    def api_ping(self, req: HttpRequest):
        # req.headers("Access-Control-Allow-Origin", "*")
        return self.serv_json_ok("pong")

    @need_auth_api
    @csrf_exempt
    def api_exit(self, req: HttpRequest, dump=False):
        pass
        """self.dl.stop(dump)
        if self.parent_pid:
            os.kill(self.parent_pid, signal.SIGUSR2)
        else:
            os.kill(os.getpid(), signal.SIGTERM)
        return self.serv_json_ok()"""

    @need_auth_api
    @csrf_exempt
    def api_restart(self, req: HttpRequest):
        pass
        '''self.dl.stop(False)
        if self.parent_pid:
            os.kill(self.parent_pid, signal.SIGUSR1)
        else:
            os.kill(os.getpid(), signal.SIGTERM)
        return self.serv_json_ok()'''


    @csrf_exempt
    @need_auth_api
    def config(self, req):
        if req.method=="GET":
            return self.api_get_config(req)
        return self.api_set_config(req)

    def api_get_config(self, req: HttpRequest):
        return self.serv_json_ok(config.cfg.config)

    def api_set_config(self, req: HttpRequest):
        body = json.loads(req.body)
        config.cfg.set_complete(body)
        config.cfg.write()
        if (config.cfg["subsonic.enable"]):
            self.sub_handler.subsonic = Subsonic(config.cfg["subsonic"])
        else:
            self.subsonic = None
        return self.serv_json_ok(config.cfg.config)


ServerHandler.instanciate()