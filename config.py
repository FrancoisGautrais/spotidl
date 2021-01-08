






import os



from http_server import config

DEFAULT_CONFIG={
    "server" : {
        "www" :  "www",
        "address" : "localhost",
        "port" : 8080
    },
    "output" : {
        "extension" : "mp3",
        "format" : "{artist}/{album}/{track-number}-{track-name}.{output-ext}",
        "dir" : "out",
        "quality" : "best"
    },
    "utils" : {
        "ffmpeg" : "ffmpeg"
    }
}

from http_server.config import cfg as config
def init(x=[]):
    if not isinstance(x, (list, tuple)): x=[x]
    config.init(DEFAULT_CONFIG, x)


