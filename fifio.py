import time
from threading import Thread, Lock
import log
from TrackSet import Jsonable, JsonArray, TrackEntry


class FIFO(Jsonable):

    def __init__(self):
        self.data=[]
        self.lock=Lock()
        self.running=True

    def push(self, url):
        self.lock.acquire()
        self.data.append(url)
        self.lock.release()

    def prepend(self, track):
        self.lock.acquire()
        self.data=[track]+self.data
        self.lock.release()

    def json(self):
        v = []
        for x in self.data:
            v.append(x.json() if x is not None else None)
        return v

    def peak(self):
        if not len(self.data): return None
        self.lock.acquire()
        x= self.data[0]
        self.lock.release()
        return x

    def pop(self, blocking=True):
        if not blocking and not len(self.data): return None
        while self.running:
            if len(self.data):
                self.lock.acquire()
                x= self.data[0]
                self.data=self.data[1:]
                self.lock.release()
                return x
            else:
                time.sleep(0.1)

    def clear(self):
        self.lock.acquire()
        self.data=[]
        self.lock.release()

    def remove(self, id):
        self.lock.acquire()
        if not id.startswith("https://"):
            id="https://open.spotify.com/track/"+id
        for track in self.data:
            if track.url==id:
                self.data.remove(track)
                break
        self.lock.release()
