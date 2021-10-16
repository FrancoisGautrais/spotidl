"""

path("command/subsonic/test", serv.api_subsonic_test)
path("command/subsonic/scan/start/sync", serv.api_start_scan_sync)
path("command/subsonic/scan/start", serv.api_start_scan_async)
path("command/subsonic/scan/status", serv.api_scan_status)

path("command/ping", serv.api_ping)
path("command/exit", serv.api_exit)
path("command/exit/#dump", serv.api_exit)
path("command/restart", serv.api_restart)
path("command/count", serv.api_count)
path("command/running/cancel/*url", serv.api_running_cancel)
path("command/running/restart/*url", serv.api_running_restart)

path("command/queue", serv.api_queue)
path("command/queue/running", serv.api_queue_running)
path("command/queue/remove/*url", serv.api_queue_remove)
path("command/queue/clear/all", serv.api_queue_clear_all)
path("command/clear/queue", serv.api_queue_clear_queue)
path("command/clear/errors", serv.api_queue_clear_errors)
path("command/clear/done", serv.api_queue_clear_done)
path("command/clear/all", serv.api_queue_clear_all)
path("command/remove/errors/#index", serv.api_queue_remove_errors)
path("command/remove/done/#index", serv.api_queue_remove_done)
path("command/restart/error/#index", serv.api_queue_restart_error)
path("command/restart/error/#index", serv.api_queue_manual_error)

path("command/add/*url", serv.api_add_get)
path("command/add", serv.api_add_post)
path("command/list/*url", serv.api_list_get)
path("command/search/*q", serv.api_search)
path("command/list", serv.api_list_post)

path("command/user/logs", serv.api_user_logs)
path("command/user/logs/tracks", serv.api_user_logs_tracks)
path("command/user/logs/refer", serv.api_user_logs_refer)
path("command/user/logs/clear", serv.api_user_logs_clear)

path("command/config", serv.api_get_config)
path("command/config", serv.api_set_config)

"""