import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .base import BaseHandler, need_auth, HttpRequest



class UserHandler(BaseHandler):
    @csrf_exempt
    def api_auth(self, request: HttpRequest):
        if request.method == "POST":
            params = json.loads(request.body)
            user = authenticate(request, username=params["username"], password=params["password"])
            if user is not None:
                login(request, user)

                return self.serv_json_ok()
            return self.serv_json_unauthorized(data="Mauvais login ou mot de passe")
        return self.serv_json_bad_request("POST uniquement")

    @need_auth
    def api_logout(self, request: HttpRequest):
        logout(request)
        return HttpResponseRedirect("/login")


    def _set_pref(self, request : HttpRequest, field = None):
        if request.method !="POST":
            return self.serv_json_bad_request("POST attendu")
        data = json.loads(request.body)
        pref = request.prefs
        if field is not None:
            pref.set(field, data)
        else:
            pref.set(data)
        return self.serv_json_ok(data=data)

    def _get_pref(self, request : HttpRequest, field = None):
        return self.serv_json_ok(request.prefs.get(field))

    @need_auth
    def pref(self, request : HttpRequest, field = None):
        if request.method !="POST":
            return self._get_pref(request, field)
        return self._set_pref(request, field)




UserHandler.instanciate()