import os

from .views import user, views, queue, log, subsonic, server
from django import urls


PREFIIX=""
def path(p, fct):
    return urls.path(os.path.join(PREFIIX,p), fct)
def abspath(p, fct):
    return urls.path(p, fct)



urlpatterns = [
    path("queue/add", queue.api_add),
    path("queue/list", queue.api_list),
    path("queue", queue.api_queue),
    path("queue/running", queue.api_queue_running),
    path("queue/running/cancel", queue.api_running_cancel),
    path("queue/running/restart", queue.api_running_restart),
    path("queue/remove/(?P<url>.*)$", queue.api_queue_remove),
    path("queue/count", queue.api_count),
    path("queue/clear", queue.api_queue_clear_queue),
    path("queue/done/<int:index>/remove", queue.api_queue_remove_done),
    path("queue/errors/<int:index>/remove", queue.api_queue_remove_errors),
    path("queue/error/<int:index>/restart", queue.api_queue_restart_error),
    path("queue/error/<int:index>/restart/manual", queue.api_queue_manual_error),
    path("queue/errors/clear", queue.api_queue_clear_errors),
    path("queue/done/clear", queue.api_queue_clear_done),
    path("queue/all/clear", queue.api_queue_clear_all),
    path("search/<str:query>", queue.api_search), #todo changer de classe

    path("logs", log.api_user_logs),
    path("logs/tracks", log.api_user_logs_tracks),
    path("logs/refer", log.api_user_logs_refer),
    path("logs/clear", log.api_user_logs_clear),

    path("subsonic/test", subsonic.api_subsonic_test),
    path("subsonic/scan/start/sync", subsonic.api_start_scan_sync),
    path("subsonic/scan/start", subsonic.api_start_scan_async),
    path("subsonic/scan/status", subsonic.api_scan_status),

    path("config", server.config),
    path("ping", server.api_ping),
    path("exit", server.api_exit),
    path("exit/<str:dump>", server.api_exit),
    path("restart", server.api_restart),

    abspath("", views.index),
    abspath("login", views.login),

    path("user/logout", user.api_logout),
    path("user/auth", user.api_auth),
    path("user/prefs/", user.pref),
    path("user/prefs/<str:field>", user.pref)
]
"""path("api/user/list", serv.api_user_list),
path("api/user/<str:name>/", serv.api_user),
path("api/user/<str:name>/create", user.api_user_create),
path("api/user/<str:name>/delete", serv.api_user_delete),
path("api/user/<str:name>/password/update", serv.api_user_set_password)"""