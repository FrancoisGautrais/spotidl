from django.shortcuts import render

from .base import BaseHandler, need_auth, HttpRequest
from django.forms.models import model_to_dict


class ViewsHandler(BaseHandler):

    @need_auth
    def index(self, request : HttpRequest):
        return render(request, "index.html", {
            "prefs" : request.prefs.json()
        })

    def login(self, request : HttpRequest):
        if request.method == "GET":
            return render(request, "login.html")
        else:
            return self.serv_json_bad_request(msg="Methode '%s' non prise en compte pour /login"%request.method)

ViewsHandler.instanciate()