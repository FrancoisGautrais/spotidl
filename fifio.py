import time
from threading import Thread, Lock

class FIFO:

    def __init__(self):
        self.data=[]
        self.lock=Lock()

    def push(self, url):
        self.lock.acquire()
        self.data.append(url)
        self.lock.release()


    def peak(self):
        if not len(self.data): return None
        self.lock.acquire()
        x= self.data[0]
        self.lock.release()
        return x

    def pop(self, blocking=True):
        if not blocking and not len(self.data): return None
        while True:
            if len(self.data):
                self.lock.acquire()
                x= self.data[0]
                self.data=self.data[1:]
                self.lock.release()
                return x
            else:
                time.sleep(0.1)
