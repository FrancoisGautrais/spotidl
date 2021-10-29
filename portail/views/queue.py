import json

import spotipy
from django.http import HttpRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

from config import cfg
from downloader import DownloaderException, Downloader
from portail.views.base import need_auth_api, BaseHandler


class QueueHandler(BaseHandler):

    def __init__(self, logger):
        self.logger_handler = logger


    def on_init(self):
        self.dl = Downloader(cfg['system.threads'])
        self.dl.start()
        self.db_logger = self.logger_handler.db_logger

    @csrf_exempt
    @need_auth_api
    def api_add(self, request: HttpRequest):
        if request.method == "POST":
            return self._api_add_post(request)
        elif request.method == "GET":
            return self._api_add_get(request)
        else:
            return HttpResponseNotFound()

    def _api_add_get(self, request: HttpRequest):
        url = request.GET["url"]
        if len(url) and url[0] == "https:": url[0] = "https:/"
        if len(url) and url[0] == "http:": url[0] = "http:/"
        url = "/".join(url)
        try:
            out = self.dl.add_track(url)
            return self.serv_json_ok(out.json())
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    def _api_add_post(self, request: HttpRequest):
        body = json.loads(request.body)
        try:
            ts = self.to_track_set(body["tracks"])
            self.db_logger.log_refer(ts)
            self.dl.add_track(ts)
            js = ts.json()
            return self.serv_json_ok(js)
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    @need_auth_api
    def api_list(self, request: HttpRequest):
        if request.method == "POST":
            return self._api_list_post(request)
        elif request.method == "GET":
            return self._api_list_get(request)
        else:
            return HttpResponseNotFound()

    @need_auth_api
    def _api_list_get(self, request: HttpRequest):
        url = request.GET["url"]
        if len(url) and url[0] == "https:": url[0] = "https:/"
        if len(url) and url[0] == "http:": url[0] = "http:/"
        try:
            out = self.dl.get_info(url)
            return self.serv_json_ok(out.json())
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    def _api_list_post(self, request: HttpRequest):
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
            tmp = self.to_track_set(body)
            out = self.dl.get_info(tmp)
            return self.serv_json_ok(out.json())
        except spotipy.exceptions.SpotifyException as err:
            return self.serv_json_bad_request(str(err))
        except DownloaderException as err:
            return self.serv_json_bad_request(str(err))

    @need_auth_api
    def api_search(self, req: HttpRequest, query: str):
        data = req.GET if req.method == "GET" else json.loads(req.body)
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
    def api_queue(self, req: HttpRequest):
        return self.serv_json_ok(self.dl.json())

    @need_auth_api
    def api_queue_running(self, req: HttpRequest):
        return self.serv_json_ok({
            "running": self.dl.running(),
            "errors_count": self.dl.errors_count(),
            "running_count": self.dl.running_count(),
            "queue_count": self.dl.queue_count(),
            "done_count": self.dl.done_count()
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
    def api_queue_remove_queue(self, req: HttpRequest, id):
        self.dl.remove_queue(id)
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
    def api_running_cancel(self, req: HttpRequest):
        self.dl.cancel_running(req.GET["url"][-1], True)
        return self.serv_json_ok("Success")

    @need_auth_api
    @csrf_exempt
    def api_running_restart(self, req: HttpRequest):
        self.dl.restart_running(req.GET["url"][-1], True)
        return self.serv_json_ok("Success")

    @need_auth_api
    @csrf_exempt
    def api_count(self, req: HttpRequest):
        return self.serv_json_ok(len(self.dl.fifo.data))


QueueHandler.instanciate()