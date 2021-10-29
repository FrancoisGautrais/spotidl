import json

from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt

from config import cfg
from portail.views import BaseHandler
from portail.views.base import need_auth_api
from subsonic.subsonic import Subsonic, SubsonicResponse


class SubsonicHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.subsonic=None

    def on_init(self):
        if cfg["subsonic.enable"]:
            self.subsonic = Subsonic(cfg["subsonic"])


    @csrf_exempt
    @need_auth_api
    def api_subsonic_test(self, req: HttpRequest):
        subsonic = Subsonic(json.loads(req.body))
        out = subsonic.test()
        if isinstance(out, SubsonicResponse):
            if out.is_http_error():
                return self.serv_json_not_found(out.json())
            else:
                return self.serv_json_bad_request(out.json())
        else:
            return self.serv_json_ok(out == True)

    @need_auth_api
    @csrf_exempt
    def api_start_scan_sync(self, req: HttpRequest):
        if not self.subsonic:
            return self.serv_json_ok({
                "scanning": False,
                "count": 0
            })
        out = self.subsonic.scan_sync()
        if isinstance(out, SubsonicResponse):
            if out.is_http_error():
                return self.serv_json_not_found(out.json())
            else:
                return self.serv_json_bad_request(out.json())
        else:
            return self.serv_json_ok({
                "scanning": out[0],
                "count": out[1]
            })

    @need_auth_api
    @csrf_exempt
    def api_start_scan_async(self, req: HttpRequest):
        if not self.subsonic:
            return self.serv_json_ok({
                "scanning": False,
                "count": 0
            })
        out = self.subsonic.start_scan()
        if isinstance(out, SubsonicResponse):
            if out.is_http_error():
                return self.serv_json_not_found(out.json())
            else:
                return self.serv_json_bad_request(out.json())
        else:
            return self.serv_json_ok({
                "scanning": out[0],
                "count": out[1]
            })

    @need_auth_api
    @csrf_exempt
    def api_scan_status(self, req: HttpRequest):
        if not self.subsonic:
            return self.serv_json_ok({
                "scanning": False,
                "count": 0
            })
        out = self.subsonic.scan_status()
        if isinstance(out, SubsonicResponse):
            if out.is_http_error():
                return self.serv_json_not_found(out.json())
            else:
                return self.serv_json_bad_request(out.json())
        else:
            return self.serv_json_ok({
                "scanning": out[0],
                "count": out[1]
            })


SubsonicHandler.instanciate()