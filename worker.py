import json
import threading
import ctypes
import time

from http_server import log
from spotdl.command_line.exceptions import NoYouTubeVideoFoundError

class DownloadProgress:
    def __init__(self, handler):
        self.total_size=0
        self.done=0
        self.handler=handler

    def get_percent(self):
        return (100*self.done/self.total_size) if self.total_size else 0

    def progress(self, x):
        if isinstance(x, bytes): x=len(x)
        self.done+=x
        if self.done>=self.total_size and self.handler:
            self.handler.on_download_finished(self)

    def new_task(self, total):
        self.total_size=total
        self.done=0
        if self.handler:
            self.handler.on_download_start(self)

    def is_finished(self):
        return self.done>=self.total_size

class ExceptionThread(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self._lock=threading.Lock()
        self._is_stopped=False
        self._frozen=False
        self._index=index
        self._interrupted=False

    def is_interrupt(self):
        return self._interrupted

    def is_stopped(self):
        x=True
        self.lock()
        x=self._is_stopped
        self.unlock()
        return x

    def is_frozen(self):
        x=True
        self.lock()
        x=self._frozen
        self.unlock()
        return x

    def set_frozen(self, val=True):
        self.lock()
        self._frozen=val
        self.unlock()

    def main(self):
        raise NotImplementedError("")

    def run(self):
        while not self.is_stopped():
            self._interrupted=False
            self.main()
            while self.is_frozen():
                time.sleep(0.1)
        log.e("Thread %d fini"%self._index)

    def stop(self, force=False):
        self.lock()
        self._is_stopped=True
        self.unlock()
        if force:
            self.raise_exception()

    def get_id(self):
        return self.ident

    def raise_exception(self):
        self._interrupted=True
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    def lock(self):
        self._lock.acquire()

    def unlock(self):
        self._lock.release()

class Worker(ExceptionThread):

    STATE_IDLE="IDLE"
    STATE_FETCH_METADATA="FETCH_METADATA"
    STATE_DOWNLOADING="DOWNLOADING"
    def __init__(self, index, fifo):
        super().__init__(index)
        self.fifo=fifo
        self.spot=fifo.spot
        self.current_track=None
        self._start_track_time=0
        self._state=Worker.STATE_IDLE
        self.progress=DownloadProgress(self)
        self.failcount=0
        self.start()


    def get_current_track(self):
        return self.current_track

    def get_current_url(self):
        return self.current_track.url if self.current_track else None

    def main(self):
        self.current_track = self.fifo.pop()
        self._start_track_time=time.time()

        if not self.current_track:
            return

        try:
            self._state= Worker.STATE_FETCH_METADATA
            self.spot.download(self.current_track, self.progress)
            if not self.is_interrupt():
                self.fifo.done(self.current_track)
            self._state= Worker.STATE_IDLE
        except NoYouTubeVideoFoundError as err:
            self.fifo.error(self.current_track, "NoYouTubeVideoFoundError : "+str(err))
        self.current_track=None

    def get_state(self):
        return self._state

    def on_download_start(self, x):
        self._state = Worker.STATE_DOWNLOADING

    def on_download_finished(self, x):
        pass

    def get_progress(self):
        if self._state==Worker.STATE_DOWNLOADING:
            prg = self.progress.get_percent()
            return prg
        if self._state==Worker.STATE_FETCH_METADATA:
            return 0
        return None


    def get_track_time(self):
        if self._start_track_time and self._state!=Worker.STATE_IDLE:
            return time.time()-self._start_track_time
        return -1

    def json(self):
        js= {
            "id" : self._index,
            "track" : self.current_track.json() if self.current_track else None,
            "track_time" : self.get_track_time(),
            "state" : self.get_state(),
            "progress" : self.get_progress(),
            "total_size" : self.progress.total_size
        }
        return js
