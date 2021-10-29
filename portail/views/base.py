from django.http import JsonResponse, HttpResponseRedirect, HttpRequest
from django.urls import reverse

from TrackSet import TrackSet, TrackEntry
from portail.models import Preferences


def need_auth(func, isapi=False):
    def wrapper(*args, **kwargs):
        if len(args)<2: raise TypeError("La fonction demande un HttpRequest en 1er argument")
        req = None
        self = args[0]
        req = args[1]
        if req.user.is_authenticated:
            req.prefs = Preferences.from_user(req.user.username)
            return func(*args, **kwargs)
        if isapi: return self.serv_json_unauthorized("")
        return HttpResponseRedirect(reverse('login'))
    return wrapper

def need_auth_api(func):
    return need_auth(func, True)

class BaseHandler:
    HANDLERS_CLASS={}
    HANDLERS={}

    @classmethod
    def instanciate(cls):
        if not cls.__name__ in BaseHandler.HANDLERS:
            BaseHandler.HANDLERS_CLASS[cls.__name__] = cls

    @classmethod
    def get(cls, name, *args, **kwargs):
        if not name in BaseHandler.HANDLERS_CLASS:
            raise Exception("'%s' n'est pas un handler de vue" % name)
        BaseHandler.HANDLERS[name] = BaseHandler.HANDLERS_CLASS[name](*args, **kwargs)
        return BaseHandler.HANDLERS[name]


    def serv_json(self, httpcode, code, msg, data=None):
        return JsonResponse({
            "code": code,
            "message": msg,
            "data": data
        }, status=httpcode)


    @staticmethod
    def init():
        return [ BaseHandler.HANDLERS[x].on_init() for x in BaseHandler.HANDLERS]

    def serv_json_ok(self, data=None, msg="Success"):
        return self.serv_json(200, 0, msg, data)

    def serv_json_bad_request(self, data=None, msg="Bad Request"):
        return self.serv_json(400, 400, msg, data)

    def serv_json_unauthorized(self, data=None, msg="Unauthorised"):
        return self.serv_json(401, 401, msg, data)

    def serv_json_forbidden(self, data=None, msg="Forbidden"):
        return self.serv_json(403, 403, msg, data)

    def serv_json_not_found(self, data=None, msg="Ressource not found"):
        return self.serv_json(404, 404, msg, data)

    def serv_json_method_not_allowed(self, data=None, msg="Method Not Allowed"):
        return self.serv_json(405, 405, msg, data)

    def serv_json_teapot(self, data=None, msg="I’m a teapot"):
        return self.serv_json(418, 418, msg, data)


    def on_init(self):
        pass


    def to_track_set(self, x):
        if isinstance(x, str):
            return x
        if isinstance(x, dict) and "type" in x and x["type"] == "track":
            return TrackSet(TrackEntry(x))
        if isinstance(x, (list, tuple)):
            return TrackSet(list(map(lambda y: self.to_track_set(y), x)))