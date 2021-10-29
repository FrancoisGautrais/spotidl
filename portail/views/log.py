from django.http import HttpRequest

from portail.models import DBLogger
from portail.views import BaseHandler
from portail.views.base import need_auth_api


class LogHandler(BaseHandler):

    def on_init(self):
        self.db_logger = DBLogger()

    @need_auth_api
    def api_user_logs(self, req: HttpRequest):
        return self.serv_json_ok(self.db_logger.get_log(req.GET))

    @need_auth_api
    def api_user_logs_tracks(self, req: HttpRequest):
        return self.serv_json_ok(self.users.get_log("track", req.query))

    @need_auth_api
    def api_user_logs_refer(self, req: HttpRequest):
        return self.serv_json_ok(self.users.get_log("refer", req.query))

    @need_auth_api
    def api_user_logs_clear(self, req: HttpRequest):
        self.db_logger.clear_logs()
        return self.serv_json_ok()

LogHandler.instanciate()