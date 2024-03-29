"""

path("api/command/subsonic/test", serv.api_subsonic_test)
path("api/command/subsonic/scan/start/sync", serv.api_start_scan_sync)
path("api/command/subsonic/scan/start", serv.api_start_scan_async)
path("api/command/subsonic/scan/status", serv.api_scan_status)

path("api/command/ping", serv.api_ping)
path("api/command/exit", serv.api_exit)
path("api/command/exit/#dump", serv.api_exit)
path("api/command/restart", serv.api_restart)
path("api/command/count", serv.api_count)
path("api/command/running/cancel/*url", serv.api_running_cancel)
path("api/command/running/restart/*url", serv.api_running_restart)

path("api/command/queue", serv.api_queue)
path("api/command/queue/running", serv.api_queue_running)
path("api/command/queue/remove/*url", serv.api_queue_remove)
path("api/command/queue/clear/all", serv.api_queue_clear_all)
path("api/command/clear/queue", serv.api_queue_clear_queue)
path("api/command/clear/errors", serv.api_queue_clear_errors)
path("api/command/clear/done", serv.api_queue_clear_done)
path("api/command/clear/all", serv.api_queue_clear_all)
path("api/command/remove/errors/#index", serv.api_queue_remove_errors)
path("api/command/remove/done/#index", serv.api_queue_remove_done)
path("api/command/restart/error/#index", serv.api_queue_restart_error)
path("api/command/restart/error/#index", serv.api_queue_manual_error)

path("api/command/add/*url", serv.api_add_get)
path("api/command/add", serv.api_add_post)
path("api/command/list/*url", serv.api_list_get)
path("api/command/search/*q", serv.api_search)
path("api/command/list", serv.api_list_post)

path("api/command/user/logs", serv.api_user_logs)
path("api/command/user/logs/tracks", serv.api_user_logs_tracks)
path("api/command/user/logs/refer", serv.api_user_logs_refer)
path("api/command/user/logs/clear", serv.api_user_logs_clear)

path("api/command/config", serv.api_get_config)
path("api/command/config", serv.api_set_config)

"""

class BadParameterException(Exception): pass

class AttributeNotFoundException(Exception): pass