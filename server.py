import spotipy
from http_server.restserver import RESTServer
from http_server.httprequest import HTTPRequest, HTTPResponse

from downloader import Downloader, DownloaderException


class DlServer(RESTServer):

    def __init__(self):
        super().__init__()
        self.dl = Downloader()
        self.dl.start()
        self.route("GET", "/api/command/exit", self.api_exit)
        self.route("GET", "/api/command/count", self.api_count)
        self.route("GET", "/api/command/done", self.api_done)
        self.route("GET", "/api/command/running", self.api_running)
        self.route("GET", "/api/command/queue", self.api_queue)
        self.route("GET", "/api/command/add/*url", self.api_add_get)
        self.route("POST", "/api/command/add", self.api_add_post)
        self.static("/", "www")
        self.route_file_gen("GET", "/", "www/index.html", needAuth=False)
        self.route_file_gen("GET", "/queue", "www/queue.html", needAuth=False)
        self.route_file_gen("GET", "/add", "www/add.html", needAuth=False)
        self.static_gen("GET", "/gen", "www/gen")


    def api_exit(self, req : HTTPRequest, res : HTTPResponse):
        res.serv_json_ok(None)
        self.dl.exit()
        self.stop()

    def api_count(self, req : HTTPRequest, res : HTTPResponse):
        res.serv_json_ok(len(self.dl.fifo.data))

    def api_done(self, req : HTTPRequest, res : HTTPResponse):
        res.serv_json_ok(list(map(lambda x: x.json(), self.dl.done)))

    def api_queue(self, req : HTTPRequest, res : HTTPResponse):
        res.serv_json_ok(list(map(lambda x: x.json(), self.dl.fifo.data) ))

    def api_running(self, req : HTTPRequest, res : HTTPResponse):
        res.serv_json_ok(list(map(lambda x: x.json(), self.dl.running.values()) ))

    def api_add_get(self, req : HTTPRequest, res : HTTPResponse):
        url = req.params["url"]
        if len(url) and url[0]=="https:": url[0]="https:/"
        if len(url) and url[0]=="http:": url[0]="http:/"
        url="/".join(url)
        print("Adding '%s'"%url)
        try:
            out = self.dl.add_track(url)
            res.serv_json_ok(out)
        except spotipy.exceptions.SpotifyException as err:
            res.serv_json_bad_request(str(err))
        except DownloaderException as err:
            res.serv_json_bad_request(str(err))

    def api_add_post(self, req : HTTPRequest, res : HTTPResponse):
        body = req.body_json()
        urls=[]
        if "urls" in  body:
            try:
                urls=body["urls"]
                out = self.dl.add_track(urls)
                res.serv_json_ok(out)
            except spotipy.exceptions.SpotifyException as err:
                res.serv_json_bad_request(str(err))
            except DownloaderException as err:
                res.serv_json_bad_request(str(err))
        else:
            res.serv_json_bad_request("L'url doit être passé par le parametre POST (en json) 'urls' (tableau ou str)")
