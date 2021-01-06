import time
import uuid

from TrackSet import TrackSet, TrackEntry, JsonArray, Jsonable
from SpotDlWrapper import SpotDlWrapper
from fifio import FIFO
from threading import Thread, Lock

from worker import Worker


class DownloaderException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message=message

class JsonError(Jsonable):

    def __init__(self, track, reason):
        self.track=track
        self.message=reason
        self.time=time.time()

    def json(self):
        return {
            "track": self.track.json(),
            "message": self.message,
            "time" : self.time,
            "id" : str(uuid.uuid4())+str(self.time)
        }

class Downloader(Thread):

    DONE_SIZE=1024
    THREAD_TIMEOUT=3600 #1h
    def __init__(self, nThreads=1):
        super().__init__()
        self.spot = SpotDlWrapper()
        self.fifo = FIFO()
        self._lock=Lock()
        self._done=JsonArray()
        self._threads=JsonArray()
        self._errors=JsonArray()
        self._n_thread=nThreads

    def running(self):
        running = []
        for i in range(len(self._threads)):
            running.append(self._threads[i].json())
        return running

    def json(self):
        return {
            "errors" : self._errors.json(),
            "running" : self.running(),
            "done" : self._done.json(),
            "queue" : self.fifo.json(),
            "queue_count" : len(self.fifo.data),
            "errors_count" : len(self._errors),
            "running_count" : len(self._threads),
            "done_count" : len(self._done)
        }

    def start(self):
        for i in range(self._n_thread):
            self._threads.append(Worker(i, self))

    def error(self, track, reason="Unknown"):
        self._errors.append(JsonError(track, reason))

    def check_alive(self):
        for i in range(len(self._threads)):
            th = self._threads[i]
            if not th.is_alive():
                self._threads[i]=Worker(i, self)
            elif th.get_track_time>Downloader.THREAD_TIMEOUT:
                th.set_frozen(True)
                track = th.get_current_track()
                th.raise_exception()
                th.join()
                self.error(track, "TIMEOUT ERROR")
                self._threads[i]=Worker(i, self)


    def lock(self):
        self._lock.acquire()

    def unlock(self):
        self._lock.release()

    def done(self, track):
        self.lock()
        self._done.append(track)
        if len(self._done)>=Downloader.DONE_SIZE:
            self._done=self._done[-Downloader.DONE_SIZE:]
        self.unlock()

    def clear(self):
        self.lock()
        self.fifo.clear()
        self.unlock()

    def pop(self):
        self.lock()
        y = self.fifo.pop()
        self.unlock()
        return y

    def _restart_running(self, trackid, restart):
        ok=False
        for i  in range(len(self._threads)):
            thd=self._threads[i]
            trid = thd.get_current_url().split("/")[-1]
            if trid == trackid:
                thd.set_frozen(True)
                track = thd.get_current_track()
                thd.raise_exception()
                #thd.join()


                if restart:
                    self.prepend(track)

                self._threads[i]=Worker(i, self)
                return True
        return ok

    def restart_running(self, url):
        return self._restart_running(url, True)

    def cancel_running(self, url):
        return self._restart_running(url, True)

    def prepend(self, track):
        self.lock()
        v = self.fifo.prepend(track)
        self.unlock()

    def remove_track(self, urls):
        if isinstance(urls, (list, tuple)):
            for x in urls:
                self.remove_track(x)
            return

        self.fifo.lock.acquire()
        for i in range(len(self.fifo.data)):
            x=self.fifo.data[i]
            if x and x.url and x.url.split("/")[-1]==urls:
                self.fifo.data[i]=None
                print("-------------------- remove !")
        self.fifo.lock.release()

    def _add_track(self, tracks):
        if isinstance(tracks, str):
            if tracks.startswith("https://open.spotify.com/track/"):
                return self._add_track(self.spot.track(tracks))
            if tracks.startswith("https://open.spotify.com/artist/"):
                return self._add_track(self.spot.artist_tracks(tracks))
            if tracks.startswith("https://open.spotify.com/album/"):
                return self._add_track(self.spot.album_tracks(tracks))

            raise DownloaderException("add_track: la chaine passée (%s) n'est pas une url valide" % tracks)
        if isinstance(tracks, TrackSet):
            return self._add_track(tracks.tracks)
        if isinstance(tracks, (list, tuple)):
            ts = TrackSet()
            for track in tracks:
                self.fifo.push(track)
                ts.add_tracks(track)
            return ts
        if isinstance(tracks, dict):
            return self._add_track(TrackEntry(dict))

        if isinstance(tracks, TrackEntry):
            self.fifo.push(tracks)
            return tracks

        raise DownloaderException("add_track: le type passé (%s) est inattendu " % type(tracks).__name__)


    def add_track(self, tracks):
        tracks=self._add_track(tracks)
        if isinstance(tracks, TrackEntry):
            return TrackSet(tracks)
        if isinstance(tracks, TrackSet):
            return tracks

        raise DownloaderException("Erreur Downloader.add_track() : type inattendu")


    def _get_info(self, url):
        if isinstance(url, str):
            if url.startswith("https://open.spotify.com/track/"):
                return self._get_info(self.spot.track(url))
            if url.startswith("https://open.spotify.com/artist/"):
                return self._get_info(self.spot.artist_tracks(url))
            if url.startswith("https://open.spotify.com/album/"):
                return self._get_info(self.spot.album_tracks(url))

            raise DownloaderException("add_track: la chaine passée (%s) n'est pas une url valide" % url)
        if isinstance(url, TrackSet):
            return self._get_info(url.tracks)
        if isinstance(url, (list, tuple)):
            ts = TrackSet()
            for track in url:
                ts.add_tracks(track)
            return ts
        if isinstance(url, dict):
            return self._get_info(TrackEntry(dict))

        if isinstance(url, TrackEntry):
            return url

        raise DownloaderException("add_track: le type passé (%s) est inattendu " % type(url).__name__)

    def get_info(self, url):
        tracks=self._get_info(url)
        if isinstance(tracks, TrackEntry):
            return TrackSet(tracks)
        if isinstance(tracks, TrackSet):
            return tracks

        raise DownloaderException("Erreur Downloader.get_info() : type inattendu")

