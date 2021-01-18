import os
import subprocess
import sys
import requests

if __name__=="__main__":
    import config
    config.init("config.json")
else:
    from config import cfg


from spotdl.command_line.exceptions import NoYouTubeVideoFoundError

from users import escape, unescape, str2json, json2str
from SpotDlWrapper import SpotDlWrapper
from TrackSet import TrackEntry

from worker import DownloadProgress, AbsWorker


class Message:
    ID="id"
    COMMAND="command"
    ARGS="args"
    CMD_SET_STATE="set_state"
    CMD_SET_PROGRESS="set_progress"
    CMD_INIT_PROGRESS="init_progress"
    CMD_POP="pop"
    CMD_DONE="job_done"
    CMD_ERROR="job_error"

    def __init__(self, js=None):
        if js:
            self.js=js
            if isinstance(js, str):
                self.js=str2json(js)
        else:
            self.js={
                Message.COMMAND : None,
                Message.ARGS : {},
                Message.ID : -1
            }

    def set_command(self, id, cmd, args=None):
        self.js[Message.ID]=id
        self.js[Message.COMMAND]=cmd
        if args: self.js[Message.ARGS]=args

    def get_id(self):
        return self.js[Message.ID]

    def get_command(self):
        return self.js[Message.COMMAND]

    def get_args(self):
        return self.js[Message.ARGS]

    def get(self):
        return self.js[Message.ID], self.js[Message.COMMAND], self.js[Message.ARGS]

    def json_str(self):
        return json2str(self.js)

    @staticmethod
    def new(id, cmd, args=None):
        tmp = Message()
        tmp.set_command(id, cmd, args)
        return tmp


    @staticmethod
    def cmd_set_state(id, state):
        return Message.new(id, Message.CMD_SET_STATE, state)

    @staticmethod
    def cmd_set_progress(id, n):
        return Message.new(id, Message.CMD_SET_PROGRESS, n)

    @staticmethod
    def cmd_init_progress(id, total):
        return Message.new(id, Message.CMD_INIT_PROGRESS, total)

    @staticmethod
    def cmd_pop(id):
        return Message.new(id, Message.CMD_POP)

    @staticmethod
    def cmd_done(id):
        return Message.new(id, Message.CMD_DONE)

    @staticmethod
    def cmd_error(id, error):
        return Message.new(id, Message.CMD_ERROR,  error)



class ProcessWorker:

    PROGRESS_REFRESH_RATE=16
    def __init__(self, url, id):
        self.spot=SpotDlWrapper()
        self.url=url
        self.id=id
        self.progress_count=0
        self.progress=DownloadProgress(self)
        self.start()

    def send(self, msg : Message):
        ret = requests.post(self.url, json=msg.js, timeout=None)
        return str2json(ret.content.decode("ascii"))

    def pop(self):
        return TrackEntry.from_track_entry_json(self.send(Message.cmd_pop(self.id)))

    def set_state(self, state):
        return self.send(Message.cmd_set_state(self.id, state))

    def set_progress(self, total):
        return self.send(Message.cmd_set_progress(self.id, total))

    def init_progress(self, total):
        return self.send(Message.cmd_init_progress(self.id, total))

    def done(self):
        return self.send(Message.cmd_done(self.id))

    def error(self, err):
        return self.send(Message.cmd_error(self.id, err))

    def start(self):
        while True:
            track = self.pop()
            try:
                self.spot.download(track, self.progress)
                self.done()
            except NoYouTubeVideoFoundError as err:
                self.error("NoYouTubeVideoFoundError : "+str(err))


    def on_download_start(self, x):
        self.init_progress(x.total_size)
        self.progress_count=0

    def on_download_finished(self, x):
        pass

    def on_progress(self, chunk, done, total):
        self.progress_count+=1
        if (self.progress_count%(ProcessWorker.PROGRESS_REFRESH_RATE))==0:
            self.set_progress(done)

    @staticmethod
    def new_process(pythonpath, url, i):
        return subprocess.Popen([cfg["utils.python"], __file__, url, str(i)], stderr=sys.stderr, stdout=sys.stderr)
        #return subprocess.Popen([pythonpath, __file__, url, str(i)], stderr=open("err","w"), stdout=open("out","w"))
        #os.system("%s %s %s %d"%(pythonpath, __file__, url, i))


if __name__=="__main__":
    print("Processus de travail %s crée (%s)" % (sys.argv[1], int(sys.argv[2])))
    pw = ProcessWorker(sys.argv[1], int(sys.argv[2]))

