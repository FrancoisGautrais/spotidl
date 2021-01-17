from http_server import utils

import config
import spotipy
from TrackSet import TrackSet, TrackEntry
from http_server.restserver import RESTServer
from http_server.httprequest import HTTPRequest, HTTPResponse
from config import cfg
from downloader import Downloader, DownloaderException
from subsonic.subsonic import Subsonic, SubsonicResponse
from users import Connector


class DlServer(RESTServer):

    def route_auth(self, *args):
        if self.enable_auth:
            super().route_auth(*args)
        else:
            super().route(*args)


    def __init__(self):
        super().__init__(ip=cfg["server.address"], restoption={
            "auth" : {
                "users" : Connector(cfg["auth.file"]),
                "url" : "/api/command/auth"
            }
        } if cfg["auth.enable"] else {})
        www=cfg["server.www"]
        self.enable_auth=cfg["auth.enable"]
        self._do_continue=False
        self.subsonic=None
        if cfg["subsonic.enable"]:
            self.subsonic=Subsonic(cfg["subsonic"])

        # A supprimer debut
        """self.users.exec("delete from log_album;")
        self.users.exec("delete from log_artist;")
        self.users.exec("delete from log_track;")
        self.users.exec("delete from queue;")"""
        # A supprimer fin

        self.dl = Downloader(self.users, cfg["system.threads"])
        self.dl.start()


        self.route_auth("POST", "/api/command/subsonic/test", self.api_subsonic_test)
        self.route_auth("GET", "/api/command/subsonic/scan/start/sync", self.api_start_scan_sync)
        self.route_auth("GET", "/api/command/subsonic/scan/start", self.api_start_scan_async)
        self.route_auth("GET", "/api/command/subsonic/scan/status", self.api_scan_status)

        self.route_auth("GET", "/api/command/ping", self.api_ping)
        self.route_auth("GET", "/api/command/exit", self.api_exit)
        self.route_auth("GET", "/api/command/exit/#dump", self.api_exit)
        self.route_auth("GET", "/api/command/restart", self.api_restart)
        self.route_auth("GET", "/api/command/count", self.api_count)
        self.route_auth("GET", "/api/command/running/cancel/*url", self.api_running_cancel)
        self.route_auth("GET", "/api/command/running/restart/*url", self.api_running_restart)

        self.route_auth("GET", "/api/command/queue", self.api_queue)
        self.route_auth("GET", "/api/command/queue/running", self.api_queue_running)
        self.route_auth("GET", "/api/command/queue/remove/*url", self.api_queue_remove)
        self.route_auth("GET", "/api/command/queue/clear/all", self.api_queue_clear_all)
        self.route_auth("GET", "/api/command/clear/queue", self.api_queue_clear_queue)
        self.route_auth("GET", "/api/command/clear/errors", self.api_queue_clear_errors)
        self.route_auth("GET", "/api/command/clear/done", self.api_queue_clear_done)
        self.route_auth("GET", "/api/command/clear/all", self.api_queue_clear_all)
        self.route_auth("GET", "/api/command/remove/errors/#index", self.api_queue_remove_errors)
        self.route_auth("GET", "/api/command/remove/done/#index", self.api_queue_remove_done)
        self.route_auth("GET", "/api/command/restart/error/#index", self.api_queue_restart_error)
        self.route_auth("POST", "/api/command/restart/error/#index", self.api_queue_manual_error)

        self.route_auth("GET", "/api/command/add/*url", self.api_add_get)
        self.route_auth("POST", "/api/command/add", self.api_add_post)
        self.route_auth("GET", "/api/command/list/*url", self.api_list_get)
        self.route_auth("GET", "/api/command/search/*q", self.api_search)
        self.route_auth("POST", "/api/command/list", self.api_list_post)

        self.route_auth("GET", "/api/command/user/logs", self.api_user_logs)
        self.route_auth("GET", "/api/command/user/logs/tracks", self.api_user_logs_tracks)
        self.route_auth("GET", "/api/command/user/logs/refer", self.api_user_logs_refer)
        self.route_auth("GET", "/api/command/user/logs/clear", self.api_user_logs_clear)

        self.route_auth("GET", "/api/command/config", self.api_get_config)
        self.route_auth("POST", "/api/command/config", self.api_set_config)

        self.precache(www)
        self.static("/", www, cached=True)

        debug=cfg["server.debug"]
        self.route_file_meta("GET", "/", "%s/index.html" % www,needAuth=self.enable_auth, cached=False, debug=debug)
        self.route_file_meta("GET", "/login", "%s/login.html" % www,needAuth=False, cached=False, debug=debug)
        self.route_file("GET", "/favicon.ico", "%s/favicon.ico" % www)

    def do_continue(self):
        return self._do_continue


    def set_continue(self, x=True):
        self._do_continue=x

    def api_subsonic_test(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        subsonic = Subsonic(req.body_json())
        out=subsonic.test()
        if isinstance(out, SubsonicResponse):
            if out.is_http_error():
                res.serv_json_not_found(out.json())
            else:
                res.serv_json_bad_request(out.json())
        else:
            res.serv_json_ok(out==True)

    def api_start_scan_sync(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        if not self.subsonic:
            res.serv_json_ok({
                "scanning" : False,
                "count" : 0
            })
        out=self.subsonic.scan_sync()
        if isinstance(out, SubsonicResponse):
            if out.is_http_error():
                res.serv_json_not_found(out.json())
            else:
                res.serv_json_bad_request(out.json())
        else:
            res.serv_json_ok({
                "scanning" : out[0],
                "count" : out[1]
            })

    def api_start_scan_async(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        if not self.subsonic:
            res.serv_json_ok({
                "scanning" : False,
                "count" : 0
            })
        out=self.subsonic.start_scan()
        if isinstance(out, SubsonicResponse):
            if out.is_http_error():
                res.serv_json_not_found(out.json())
            else:
                res.serv_json_bad_request(out.json())
        else:
            res.serv_json_ok({
                "scanning" : out[0],
                "count" : out[1]
            })

    def api_scan_status(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        if not self.subsonic:
            res.serv_json_ok({
                "scanning" : False,
                "count" : 0
            })
        out=self.subsonic.scan_status()
        if isinstance(out, SubsonicResponse):
            if out.is_http_error():
                res.serv_json_not_found(out.json())
            else:
                res.serv_json_bad_request(out.json())
        else:
            res.serv_json_ok({
                "scanning" : out[0],
                "count" : out[1]
            })


    def api_user_logs(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        if user:
            res.serv_json_ok(self.users.get_log(req.query))
        else:
            res.serv_json_ok([])

    def api_user_logs_tracks(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        if user:
            res.serv_json_ok(self.users.get_log("track", req.query))
        else:
            res.serv_json_ok([])

    def api_user_logs_refer(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        if user:
            res.serv_json_ok(self.users.get_log("refer", req.query))
        else:
            res.serv_json_ok([])

    def api_user_logs_clear(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        if user:
            self.users.clear_logs()
            res.serv_json_ok("success")
        else:
            res.serv_json_ok("success")

    def api_queue_restart_error(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        i = int(req.params["index"])
        if self.dl.restart_error(i):
            res.serv_json_ok("success")
        else:
            res.serv_json_not_found()

    def api_queue_manual_error(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        i = int(req.params["index"])
        body = req.body_json()
        url = body["url"]
        if self.dl.manual_error(i, url):
            res.serv_json_ok("success")
        else:
            res.serv_json_not_found()

    def api_ping(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        res.header("Access-Control-Allow-Origin", "*")
        res.serv_json_ok("pong")

    def api_exit(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        dump=True
        if "dump" in req.params and (req.params["dump"].lower()=="false" or req.params["dump"]=="0"):
            dump=False
        res.serv_json_ok(None)
        self.dl.stop(dump)
        self.set_continue(False)
        self.users.close()
        self.stop()

    def api_restart(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        res.serv_json_ok(None)
        self.dl.stop(True)
        self.set_continue(True)
        self.users.close()
        self.stop()

    def api_count(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        res.serv_json_ok(len(self.dl.fifo.data))

    def api_running_cancel(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.cancel_running(req.params["url"][-1], True)
        res.serv_json_ok("Success")

    def api_running_restart(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.restart_running(req.params["url"][-1], True)
        res.serv_json_ok("Success")

    def api_set_config(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        body = req.body_json()
        config.cfg.set_complete(body)
        config.cfg.write()
        if(config.cfg["subsonic.enable"]):
            self.subsonic=Subsonic(config.cfg["subsonic"])
        else:
            self.subsonic=None
        res.serv_json_ok(config.cfg.config)

    def api_get_config(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        res.serv_json_ok(config.cfg.config)

    def api_search(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        data = req.query if req.method=="GET" else req.body_json()
        res.serv_json_ok(self.dl.search(req.params["q"], data))

    def api_queue(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        res.serv_json_ok(self.dl.json())

    def api_queue_running(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        res.serv_json_ok({
            "running" : self.dl.running(),
            "errors_count" : self.dl.errors_count(),
            "running_count" : self.dl.running_count(),
            "queue_count" : self.dl.queue_count(),
            "done_count" : self.dl.done_count()
        })

    def api_queue_remove(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.remove_track(req.params["url"][-1])
        res.serv_json_ok("Success")

    def api_queue_clear_queue(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.clear()
        res.serv_json_ok("Success")

    def api_queue_clear_errors(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.clear_errors()
        res.serv_json_ok("Success")

    def api_queue_remove_errors(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.remove_error(int(req.params["index"]))
        res.serv_json_ok("Success")

    def api_queue_remove_queue(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.remove_queue(req.params["id"])
        res.serv_json_ok("Success")

    def api_queue_remove_done(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.remove_done(int(req.params["index"]))
        res.serv_json_ok("Success")

    def api_queue_clear_done(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.clear_done()
        res.serv_json_ok("Success")

    def api_queue_clear_all(self, req: HTTPRequest, res: HTTPResponse, session=None, user=None):
        self.dl.clear_done()
        self.dl.clear_errors()
        self.dl.clear()
        res.serv_json_ok("Success")

    def api_add_get(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        url = req.params["url"]
        if len(url) and url[0]=="https:": url[0]="https:/"
        if len(url) and url[0]=="http:": url[0]="http:/"
        url="/".join(url)
        try:
            out = self.dl.add_track(url)
            res.serv_json_ok(out.json())
        except spotipy.exceptions.SpotifyException as err:
            res.serv_json_bad_request(str(err))
        except DownloaderException as err:
            res.serv_json_bad_request(str(err))

    def api_add_post(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        body = req.body_json()
        try:
            ts=self.to_track_set(body["tracks"])
            if user:
                self.users.log_refer(ts)
            self.dl.add_track(ts)
            js=ts.json()
            res.serv_json_ok(js)
        except spotipy.exceptions.SpotifyException as err:
            res.serv_json_bad_request(str(err))
        except DownloaderException as err:
            res.serv_json_bad_request(str(err))

    def api_list_get(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        url = req.params["url"]
        if len(url) and url[0]=="https:": url[0]="https:/"
        if len(url) and url[0]=="http:": url[0]="http:/"
        url="/".join(url)
        try:
            out = self.dl.get_info(url)
            res.serv_json_ok(out.json())

        except spotipy.exceptions.SpotifyException as err:
            res.serv_json_bad_request(str(err))
        except DownloaderException as err:
            res.serv_json_bad_request(str(err))

    def api_list_post(self, req : HTTPRequest, res : HTTPResponse, session=None, user=None):
        if req.is_multipart():
            file = req.multipart_next_file()
            data=file.parse_content().decode("utf-8")
            data=data.replace("\r", "").split("\n")
            ts = TrackSet()
            for url in data:
                try:
                    ts.add_tracks(self.dl.get_info(url))
                except DownloaderException as err:
                    pass
            res.serv_json_ok(ts.json())
        else:
            body = req.body_json()
            try:
                tmp=self.to_track_set(body)
                out = self.dl.get_info(tmp)
                res.serv_json_ok(out.json())
            except spotipy.exceptions.SpotifyException as err:
                res.serv_json_bad_request(str(err))
            except DownloaderException as err:
                res.serv_json_bad_request(str(err))

    def to_track_set(self, x):
        if isinstance(x, str):
            return x
        if isinstance(x, dict) and "type" in x and x["type"]=="track":
            return TrackSet(TrackEntry(x))
        if isinstance(x, (list,tuple)):
            return TrackSet(list(map(lambda y: self.to_track_set(y), x)))

