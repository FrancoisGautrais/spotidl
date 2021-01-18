import json


import os
import time
from threading import Thread, Lock

import psutil
from http_server import log
from http_server.httpserver import HTTPResponse, HTTPServer, HTTPRequest
from config import cfg

from TrackSet import TrackEntry
from process_worker import ProcessWorker, Message
from worker import AbsWorker, ExceptionThread




class ProcessInterface(AbsWorker):

    def __init__(self, index, fifo):
        super().__init__(index)
        self.pid=-1
        self.sp=None
        self.fifo=fifo
        self._response=None
        self._request=None
        self.create_process()

    def create_process(self):
        url="http://%s:%d/" % (cfg["system.multiprocess.ip"], cfg["system.multiprocess.port"])
        self.sp=ProcessWorker.new_process("/usr/bin/python", url, self.index)
        self.pid=self.sp.pid

    def set_progress(self, n):
        self.progress.abs_progress(n)

    def init_progress(self, total):
        self.progress.new_task(total)
        self._state=AbsWorker.STATE_DOWNLOADING

    def is_waiting(self):
        return self._response is not None

    def pop_prepare(self, req, res):
        self._response=res
        self._request=req

    def respond_pop_to_process(self, task):
        self.current_track = task
        self._start_track_time = time.time()
        self._state = AbsWorker.STATE_FETCH_METADATA
        ok=True
        if self._response:
            sock = self._request.get_socket()
            self._response.content_type("application/json")
            self._response.serv(200, data=task.json())
            self._response.write(sock)
            sock.close()
        self._response=None
        self._request=None
        return ok

    def error(self, err):
        self._state = AbsWorker.STATE_IDLE
        track = self.current_track
        log.error("Impossible de télécharger '%s' : %s"%(track.name, str(err)))
        self.fifo.error(self.current_track, err)
        self.current_track=None

    def done(self):
        self._state = AbsWorker.STATE_IDLE
        self.fifo.done(self.current_track)
        self.current_track=None

    def get_id(self):
        return self.index

    def is_stopped(self):
        return psutil.pid_exists(self.pid)

    def set_frozen(self):
        pass

    def stop(self):
        if self.is_stopped():
            os.kill(self.pid, 9)


class ProcessInterfaceUpdaterScheduler(ExceptionThread):

    def __init__(self, dl):
        super().__init__(-23)
        self.process=dl._threads
        self.fifo=dl
        self.start()

    def find_available_process(self):
        for process in self.process:
            if process.is_waiting():
                return process
        return None

    def main(self):
        process=None
        while (not self.is_stopped()) and not process:
            process=self.find_available_process()
            if not process:
                time.sleep(0.5)
        if not process: return
        track = self.fifo.pop()
        process.respond_pop_to_process(track)



class ProcessInterfaceUpdater(HTTPServer, Thread):
    def __init__(self, dl):
        Thread.__init__(self)
        HTTPServer.__init__(self, cfg["system.multiprocess.ip"], {
            "mode" : HTTPServer.SINGLE_ASYNC
        })
        self._threads=dl._threads
        self.fifo=dl
        self.scheduler=ProcessInterfaceUpdaterScheduler(dl)
        self.start()


    def handlerequest(self, req : HTTPRequest, res : HTTPResponse):
        msg = Message(req.body_json())
        id, cmd, args = msg.get()
        pi = self._threads[id]
        if cmd==Message.CMD_POP:
            pi.pop_prepare(req, res)
        elif cmd==Message.CMD_ERROR:
            pi.error(args)
        elif cmd==Message.CMD_DONE:
            pi.done()
        elif cmd==Message.CMD_SET_PROGRESS:
            pi.set_progress(args)
        elif cmd==Message.CMD_INIT_PROGRESS:
            pi.init_progress(args)

        if cmd!=Message.CMD_POP:
            res.content_type("application/json")
            res.end("{}")
            res.write(req.get_socket())
            req.get_socket().close()

    def run(self):
        self.listen(cfg["system.multiprocess.port"])









