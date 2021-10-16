import spotipy
from django.http import *
from django.shortcuts import render

# Create your views here.
from TrackSet import TrackSet, TrackEntry
from downloader import DownloaderException, Downloader
from portail.models import DBLogger


class BaseServeur:

    def serv_json(self, httpcode, code, msg, data=None):
        return JsonResponse({
            "code": code,
            "message": msg,
            "data": data
        }, status=httpcode)


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

class Serveur(BaseServeur):

    def __init__(self):
        #self.dl = Downloader(self.users, cfg["system.threads"])
        self.dl = None

    def init(self):
        self.dl = Downloader(1)
        self.dl.start()

    def to_track_set(self, x):
        if isinstance(x, str):
            return x
        if isinstance(x, dict) and "type" in x and x["type"]=="track":
            return TrackSet(TrackEntry(x))
        if isinstance(x, (list,tuple)):
            return TrackSet(list(map(lambda y: self.to_track_set(y), x)))

    def index(self, request : HttpRequest):
        print("Here")
        return render(request, "index.html")

    def api_add(self, request : HttpRequest):
        if request.method == "POST":
            return self._api_add_post(request)
        elif request.method == "GET":
            return self._api_add_get(request)
        else:
            return HttpResponseNotFound()


    def _api_add_get(self, request : HttpRequest):
        url = request.GET["url"]
        if len(url) and url[0]=="https:": url[0]="https:/"
        if len(url) and url[0]=="http:": url[0]="http:/"
        url="/".join(url)
        try:
            out = self.dl.add_track(url)
            return self.serv_json_ok(out.json())
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    def _api_add_post(self, request : HttpRequest):
        body = request.POST
        try:
            ts=self.to_track_set(body["tracks"])
            DBLogger.log_refer(ts)
            self.dl.add_track(ts)
            js=ts.json()
            return self.serv_json_ok(js)
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    def api_list(self, request : HttpRequest):
        if request.method == "POST":
            return self._api_list_post(request)
        elif request.method == "GET":
            return self._api_list_get(request)
        else:
            return HttpResponseNotFound()

    def _api_list_get(self, request : HttpRequest):
        url = request.GET["url"]
        if len(url) and url[0]=="https:": url[0]="https:/"
        if len(url) and url[0]=="http:": url[0]="http:/"
        url="/".join(url)
        try:
            out = self.dl.get_info(url)
            return self.serv_json_ok(out.json())
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    def _api_list_post(self, request : HttpRequest):
        """if req.is_multipart():
            file = req.multipart_next_file()
            data=file.parse_content().decode("utf-8")
            data=data.replace("\r", "").split("\n")
            ts = TrackSet()
            for url in data:
                try:
                    ts.add_tracks(self.dl.get_info(url))
                except DownloaderException as err:
                    pass
            self.serv_json_ok(ts.json())
        else:"""
        body = request.POST
        try:
            tmp=self.to_track_set(body)
            out = self.dl.get_info(tmp)
            return self.serv_json_ok(out.json())
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    def api_search(self, req : HttpRequest, query : str):
        data = req.GET if req.method=="GET" else req.POST()
        return self.serv_json_ok(self.dl.search(query, data))

serv = Serveur()