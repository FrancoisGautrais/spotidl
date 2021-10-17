import json
import os
import signal

from config import cfg
import spotipy
from django.http import *
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
import config
from TrackSet import TrackSet, TrackEntry
from downloader import DownloaderException, Downloader
from portail.models import DBLogger, Preferences
from subsonic.subsonic import Subsonic, SubsonicResponse

from django.contrib.auth import authenticate, login, logout

def get_prefs(request : HttpRequest):
    if request.user.is_authenticated:
        pass

def need_auth(func, isapi=False):
    def wrapper(*args, **kwargs):
        if len(args)<2: raise TypeError("La fonction demande un HttpRequest en 1er argument")
        req = None
        self = args[0]
        req = args[1]
        if req.user.is_authenticated:
            req.prefs = Preferences.get(req.user.username)
            return func(*args, **kwargs)
        if isapi: return self.serv_json_unauthorized("")
        return HttpResponseRedirect("/login")
    return wrapper

def need_auth_api(func):
    return need_auth(func, True)

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
        self.db_logger = None
        self.subsonic = None
        self.parent_pid = None


        if "parent_pid" in os.environ:
            self.parent_pid=int(os.environ["parent_pid"])


    def init(self):
        self.dl = Downloader(1)
        self.dl.start()
        self.db_logger = DBLogger()
        if cfg["subsonic.enable"]:
            self.subsonic = Subsonic(cfg["subsonic"])

    def to_track_set(self, x):
        if isinstance(x, str):
            return x
        if isinstance(x, dict) and "type" in x and x["type"]=="track":
            return TrackSet(TrackEntry(x))
        if isinstance(x, (list,tuple)):
            return TrackSet(list(map(lambda y: self.to_track_set(y), x)))

    @need_auth
    def index(self, request : HttpRequest):
        return render(request, "index.html")

    def login(self, request : HttpRequest):
        if request.method == "GET":
            return render(request, "login.html")
        else:
            return self.serv_json_bad_request(msg="Methode '%s' non prise en compte pour /login"%request.method)

    @csrf_exempt
    def api_auth(self, request : HttpRequest):
        if request.method == "POST":
            params = json.loads(request.body)
            user = authenticate(request, username=params["username"], password=params["password"])
            if user is not None:
                login(request, user)

                return self.serv_json_ok()
            return self.serv_json_unauthorized(data="Mauvais login ou mot de passe")
        return self.serv_json_bad_request("POST uniquement")

    @need_auth
    def api_logout(self, request : HttpRequest):
        logout(request)
        return HttpResponseRedirect("/login")

    @need_auth_api
    @csrf_exempt
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
        body = json.loads(request.body)
        try:
            ts=self.to_track_set(body["tracks"])
            self.db_logger.log_refer(ts)
            self.dl.add_track(ts)
            js=ts.json()
            return self.serv_json_ok(js)
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    @need_auth_api
    def api_list(self, request : HttpRequest):
        if request.method == "POST":
            return self._api_list_post(request)
        elif request.method == "GET":
            return self._api_list_get(request)
        else:
            return HttpResponseNotFound()

    @need_auth_api
    def _api_list_get(self, request : HttpRequest):
        url = request.GET["url"]
        if len(url) and url[0]=="https:": url[0]="https:/"
        if len(url) and url[0]=="http:": url[0]="http:/"
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
            return self.serv_json_ok(ts.json())
        else:"""
        body = json.loads(request.body)
        try:
            tmp=self.to_track_set(body)
            out = self.dl.get_info(tmp)
            return self.serv_json_ok(out.json())
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    @need_auth_api
    def api_search(self, req : HttpRequest, query : str):
        data = req.GET if req.method=="GET" else json.loads(req.body)
        return self.serv_json_ok(self.dl.search(query, data))

    @need_auth_api
    def api_queue_restart_error(self, req: HttpRequest, index):
        if self.dl.restart_error(index):
            return self.serv_json_ok("success")
        else:
            return self.serv_json_not_found()

    def api_queue_manual_error(self, req: HttpRequest, index):
        body = json.loads(req.body)
        url = body["url"]
        if self.dl.manual_error(index, url):
            return self.serv_json_ok("success")
        else:
            return self.serv_json_not_found()


    @need_auth_api
    def api_queue(self, req : HttpRequest):
        return self.serv_json_ok(self.dl.json())

    @need_auth_api
    def api_queue_running(self, req : HttpRequest):
        return self.serv_json_ok({
            "running" : self.dl.running(),
            "errors_count" : self.dl.errors_count(),
            "running_count" : self.dl.running_count(),
            "queue_count" : self.dl.queue_count(),
            "done_count" : self.dl.done_count()
        })

    @need_auth_api
    def api_queue_remove(self, req: HttpRequest, url):
        self.dl.remove_track(url)
        return self.serv_json_ok("Success")

    @need_auth_api
    def api_queue_clear_queue(self, req: HttpRequest):
        self.dl.clear()
        return self.serv_json_ok("Success")

    @need_auth_api
    def api_queue_clear_errors(self, req: HttpRequest):
        self.dl.clear_errors()
        return self.serv_json_ok("Success")

    @need_auth_api
    def api_queue_remove_errors(self, req: HttpRequest, index):
        self.dl.remove_error(index)
        return self.serv_json_ok("Success")

    @need_auth_api
    def api_queue_remove_queue(self, req: HttpRequest):
        self.dl.remove_queue(req.params["id"])
        return self.serv_json_ok("Success")

    @need_auth_api
    def api_queue_remove_done(self, req: HttpRequest, index):
        self.dl.remove_done(index)
        return self.serv_json_ok("Success")

    @need_auth_api
    def api_queue_clear_done(self, req: HttpRequest):
        self.dl.clear_done()
        return self.serv_json_ok("Success")

    @need_auth_api
    def api_queue_clear_all(self, req: HttpRequest):
        self.dl.clear_done()
        self.dl.clear_errors()
        self.dl.clear()
        return self.serv_json_ok("Success")

    @need_auth_api
    def api_user_logs(self, req : HttpRequest):
        return self.serv_json_ok(self.db_logger.get_log(req.GET))

    @need_auth_api
    def api_user_logs_tracks(self, req : HttpRequest):
        return self.serv_json_ok(self.users.get_log("track", req.query))

    @need_auth_api
    def api_user_logs_refer(self, req : HttpRequest):
        return self.serv_json_ok(self.users.get_log("refer", req.query))

    @need_auth_api
    def api_user_logs_clear(self, req : HttpRequest):
        self.db_logger.clear_logs()
        return self.serv_json_ok()

    @need_auth_api
    def api_get_config(self, req: HttpRequest):
        return self.serv_json_ok(config.cfg.config)

    @need_auth_api
    def api_set_config(self, req: HttpRequest):
        body = json.loads(req.body)
        config.cfg.set_complete(body)
        config.cfg.write()
        if(config.cfg["subsonic.enable"]):
            self.subsonic=Subsonic(config.cfg["subsonic"])
        else:
            self.subsonic=None
        return self.serv_json_ok(config.cfg.config)

    @need_auth_api
    @csrf_exempt
    def api_subsonic_test(self, req: HttpRequest):
        subsonic = Subsonic(json.loads(req.body))
        out=subsonic.test()
        if isinstance(out, SubsonicResponse):
            if out.is_http_error():
                return self.serv_json_not_found(out.json())
            else:
                return self.serv_json_bad_request(out.json())
        else:
            return self.serv_json_ok(out==True)

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

    @need_auth_api
    @csrf_exempt
    def api_ping(self, req: HttpRequest):
        #req.headers("Access-Control-Allow-Origin", "*")
        return self.serv_json_ok("pong")

    @need_auth_api
    @csrf_exempt
    def api_exit(self, req: HttpRequest, dump=False):
        self.dl.stop(dump)
        if self.parent_pid:
            os.kill(self.parent_pid, signal.SIGUSR2)
        else:
            os.kill(os.getpid(), signal.SIGTERM)
        return self.serv_json_ok()

    @need_auth_api
    @csrf_exempt
    def api_restart(self, req: HttpRequest):
        self.dl.stop(False)
        if self.parent_pid:
            os.kill(self.parent_pid, signal.SIGUSR1)
        else:
            os.kill(os.getpid(), signal.SIGTERM)
        return self.serv_json_ok()

    @need_auth_api
    @csrf_exempt
    def api_count(self, req: HttpRequest):
        return self.serv_json_ok(len(self.dl.fifo.data))

    @need_auth_api
    @csrf_exempt
    def api_running_cancel(self, req: HttpRequest):
        self.dl.cancel_running(req.params["url"][-1], True)
        return self.serv_json_ok("Success")

    @need_auth_api
    @csrf_exempt
    def api_running_restart(self, req: HttpRequest):
        self.dl.restart_running(req.params["url"][-1], True)
        return self.serv_json_ok("Success")
serv = Serveur()