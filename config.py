import os


DEFAULT_CONFIG={
    "server" : {
        "www" :  "www",
        "address" : "localhost",
        "port" : 8080,
        "debug" : True
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
    "system" : {
        "threads" : 4
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

import json
import utils
import log
class Config:

    def __init__(self):
        self.is_init=False
        self.output_file="config.json"
        self.is_default=True


    def _load(self, filename):
        try:
            with open(filename, "r") as f:
                js = json.loads(f.read())
                if isinstance(js, dict):
                    self.config=utils.deepassign(self.config, js)
                    self.is_default=False
                    return True
        except:
            pass
        return False

    def init(self, default=None, filename=[]):
        if not default: default={}
        self.is_init=False
        self.config=default
        if not isinstance(filename, (list, tuple)): filename=[filename]
        for file in filename:
            if self._load(file):
                log.i("Configuration '%s' chargée" % file)
                break

    def write(self, path=None):
        if not path: path=self.output_file
        with open(path,"w") as f:
            f.write(json.dumps(self.config, indent=4))

    def get(self, path):
        l = path.split(".")
        i=0
        n=len(l)
        curr = self.config
        for key in l:
            if key in curr:
                curr=curr[key]
            else: return None
        return curr



    def has(self, path):
        l = path.split(".")
        i=0
        n=len(l)
        curr = self.config
        for key in l:
            if key in curr:
                curr=curr[key]
            else: return None
        return curr.__class__


    def set_complete(self, x):
        utils.deepassign(self.config, x)

    def set(self, path, value):
        l = path.split(".")[:]
        l1 = l[:-1]
        lastkey =  l[-1]
        i = 0
        n = len(l)
        curr = self.config
        for key in l1:
            if key in curr:
                curr = curr[key]
            else: return None
        curr[lastkey]=value
        return value

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, item, val):
        return self.set(item, val)






cfg = Config()
def init(x=["config.json"]):
    if not isinstance(x, (list, tuple)): x=[x]
    cfg.init(DEFAULT_CONFIG, x)
    return cfg





