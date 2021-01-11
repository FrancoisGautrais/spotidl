
import os
os.chdir(os.path.dirname(__file__))

from http_server import log


import config
cfg = config.init("config.json")
if cfg.is_default:
    cfg.write("config.json")

from server import DlServer

log.init(log.Log.INFO)
dl=None
while not dl or dl.do_continue():
    dl = DlServer()
    dl.listen(cfg["server.port"])
    dl.close()
