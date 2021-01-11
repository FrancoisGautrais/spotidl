import json
import os
import time
import uuid

import config
from http_server import log
from TrackSet import TrackSet, TrackEntry, JsonArray, Jsonable, Refer
from SpotDlWrapper import SpotDlWrapper
from fifio import FIFO
from threading import Thread, Lock

from worker import Worker, ExceptionThread


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

    @staticmethod
    def from_json(js):
        je = JsonError(TrackEntry.from_track_entry_json(js["track"]), js["message"])
        je.time=js["time"]
        je.id=js["id"]
        return je

class WatchDogThread(ExceptionThread):
    def __init__(self, down):
        super().__init__(-1)
        self.downloader=down
        self._continue=True
        self.pause=30
        self.step=0.5
        self.n_step=int(self.pause/self.step)

    def stop(self):
        self._continue=False
        super().stop()

    def main(self):
        while self._continue:
            self.downloader.watchdog()
            for i in range(self.n_step):
                if not self._continue: return
                time.sleep(0.5)

class Downloader:

    DONE_SIZE=1024
    THREAD_TIMEOUT=3600 #1h
    def __init__(self, nThreads=1):
        self.spot = SpotDlWrapper()
        self.fifo = FIFO()
        self._lock=Lock()
        self._done=JsonArray()
        self._threads=JsonArray()
        self._errors=JsonArray()
        self._n_thread=nThreads
        self.watchdog_time=5*60
        self.dump_file="dump.json"


        if os.path.isfile(self.dump_file) and os.path.exists(self.dump_file):
            with open(self.dump_file) as f:
                js = json.loads(f.read())
            os.remove(self.dump_file)
            for track in js["queue"]:
                self.fifo.push(TrackEntry.from_track_entry_json(track))
            for track in js["done"]:
                self._done.append(TrackEntry.from_track_entry_json(track))
            for error in js["errors"]:
                self._errors.append(JsonError.from_json(error))

        self._watchdog=WatchDogThread(self)
        self._watchdog.start()

    def errors_count(self): return len(self._errors)
    def running_count(self): return len(self._threads)
    def done_count(self): return len(self._done)
    def queue_count(self): return len(self.fifo.data)

    def dump(self):
        self.lock()
        self.fifo.lock.acquire()
        tmp=[]
        for x in self._threads:
            track=x.get_current_track()
            if track:
                tmp.append(track.json())
        with open(self.dump_file, "w") as f:
            data={
                "queue" : tmp+self.fifo.json(),
                "done" : self._done.json(),
                "errors" : self._errors.json()
            }
            f.write(json.dumps(data))
        self.fifo.lock.release()
        self.unlock()

    def stop(self, dump):
        if dump: self.dump()
        self.fifo.running=False
        for th in self._threads:
            th.stop()
            th.join()
        self._watchdog.stop()
        self._watchdog.join()

    def watchdog(self):
        for i in range(len(self._threads)):
            th=self._threads[i]
            if not th.is_alive():
                if th.get_current_track():
                    track = th.get_current_track().fail()
                    log.e("WatchdogError : [%d] -> '%s' a crasher le thred %d fois" % (
                                i, track.url,  track.failcount))
                    if track.failcount < 3:
                        self.restart_running(track.url)
                    else:
                        self.cancel_running(track.url)
                self._threads[i] = Worker(i, self)
            elif th.get_track_time()>self.watchdog_time:
                track=th.get_current_track().fail()
                log.e("WatchdogError : [%d] -> '%s' after %d sec tries: %d" % (i, track.url, int(th.get_track_time()),track.failcount))
                if track.failcount<3:
                    self.restart_running(track.url)
                else:
                    self.cancel_running(track.url)

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

    def remove_error(self, i):
        self.lock()
        if not isinstance(i, int) or i < 0 or i >= len(self._errors):
            self.unlock()
            return
        self._errors.remove(self._errors[i])
        self.unlock()

    def remove_queue(self, id):
        self.fifo.remove(id)

    def remove_done(self, i):
        self.lock()
        if not isinstance(i, int) or i<0 or i>=len(self._done):
            self.unlock()
            return
        self._done.remove(self._done[i])
        self.unlock()


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

    def clear_errors(self):
        self.lock()
        self._errors = JsonArray()
        self.unlock()

    def clear_done(self):
        self.lock()
        self._done=JsonArray()
        self.unlock()

    def pop(self):
        y = self.fifo.pop()
        return y

    def restart_error(self, i ):
        if i>=0 and i< len(self._errors):
            self.fifo.prepend(self._errors[i].track)
            return True
        return False


    def manual_error(self, i, url):
        if i>=0 and i< len(self._errors):
            track = self._errors[i].track
            track.set_youtube_url(url)
            self.fifo.prepend(track)
            return True
        return False

    def _restart_running(self, trackid, restart, isManual=False):
        ok=False
        if trackid.startswith("https://"):
            trackid=trackid.split("/")[-1]
        for i  in range(len(self._threads)):
            thd=self._threads[i]
            trid = thd.get_current_url().split("/")[-1]
            if trid == trackid:
                thd.set_frozen(True)
                track = thd.get_current_track()
                thd.raise_exception()
                #thd.join()

                if restart:
                    type=("mannuel" if isManual else "automatique")
                    self.prepend(track)
                    self.error(track, "Redémarrage %s"%type)
                    log.w("Rédémarage %s de la piste '%s' "%(type, track.url))
                else:
                    type=("mannuelle" if isManual else "automatique")
                    self.error(track, "Annulation %s"%type)
                    log.w("Annulation %s de la piste '%s' "%(type, track.url))

                self._threads[i]=Worker(i, self)
                return True
        return ok

    def restart_running(self, url, isManual=False):
        return self._restart_running(url, True, isManual)

    def cancel_running(self, url, isManual=False):
        return self._restart_running(url, False, isManual)

    def search(self, query, type):
        return self.spot.search(query, type)

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
        self.fifo.lock.release()

    def _add_track(self, tracks):
        if isinstance(tracks, str):
            if tracks.startswith("https://open.spotify.com/track/"):
                return self._add_track(self.spot.track(tracks))
            if tracks.startswith("https://open.spotify.com/artist/"):
                return self._add_track(self.spot.artist_tracks(tracks))
            if tracks.startswith("https://open.spotify.com/album/"):
                return self._add_track(self.spot.album_tracks(tracks))
            if tracks.startswith("https://open.spotify.com/playlist/"):
                return self._add_track(self.spot.playlist_tracks(tracks))

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


    def _get_info(self, url, refer):
        if isinstance(url, str):
            if url.startswith("https://open.spotify.com/track/"):
                track=self.spot.track(url)
                if refer: refer.add_track(url, track)
                return self._get_info(track, None)
            if url.startswith("https://open.spotify.com/artist/"):
                tracks=self.spot.artist_tracks(url)
                if refer: refer.add_artist(url, tracks)
                return self._get_info(tracks, None)
            if url.startswith("https://open.spotify.com/album/"):
                tracks=self.spot.album_tracks(url)
                if refer: refer.add_album(url, tracks)
                return self._get_info(tracks, None)
            if url.startswith("https://open.spotify.com/playlist/"):
                tracks=self.spot.playlist_tracks(url)
                if refer: refer.add_playlist(url, tracks)
                return self._get_info(tracks, None)

            raise DownloaderException("add_track: la chaine passée (%s) n'est pas une url valide" % url)
        if isinstance(url, TrackSet):
            return self._get_info(url.tracks, None)
        if isinstance(url, (list, tuple)):
            ts = TrackSet()
            for track in url:
                ts.add_tracks(track)
            return ts
        if isinstance(url, dict):
            return self._get_info(TrackEntry(dict), None)
        if isinstance(url, TrackEntry):
            return url

        raise DownloaderException("add_track: le type passé (%s) est inattendu " % type(url).__name__)

    def get_info(self, url):
        refer=Refer()
        tracks=self._get_info(url, refer)

        if isinstance(tracks, TrackEntry):
            ts= TrackSet(tracks)
            ts.add_refer(refer)
            return ts
        if isinstance(tracks, TrackSet):
            tracks.add_refer(refer)
            return tracks

        raise DownloaderException("Erreur Downloader.get_info() : type inattendu")

