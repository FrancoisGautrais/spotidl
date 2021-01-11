






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
    },
    "auth" : {
        "enable" : True,
        "file" : "data.db",
        "default_user" : {
            "name" : "fanch",
            "password" : "password"
        }
    },
    "subsonic" : {
        "enable" : True,
        "url" : "http://dom:1234/",
        "user" : "Your Login",
        "password" : "Your Password"
    }
}

from http_server import  config as _config

cfg = _config.Config()
def init(x=["config.json"]):
    if not isinstance(x, (list, tuple)): x=[x]
    cfg.init(DEFAULT_CONFIG, x)
    return cfg





