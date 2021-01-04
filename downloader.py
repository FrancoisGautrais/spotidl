from TrackSet import TrackSet, TrackEntry
from SpotDlWrapper import SpotDlWrapper
from fifio import FIFO
from threading import Thread, Lock

class DownloaderException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message=message

class Downloader(Thread):

    def __init__(self):
        super().__init__()
        self.spot = SpotDlWrapper()
        self.fifo = FIFO()
        self.lock=Lock()
        self.do_exit=False
        self.done=[]
        self.running={}

    def exit(self):
        self.lock.acquire()
        self.do_exit=True
        self.lock.release()

    def run(self):
        while True:
            self.lock.acquire()
            ex = self.do_exit
            self.lock.release()
            if ex: return

            track = self.fifo.pop(True)
            if not track:
                continue

            self.running[track.url] = track
            try:
                self.spot.download(track)
            except:
                print("Erreur impossible de télécharger")

            self.fifo.lock.acquire()
            del self.running[track.url]
            self.done.append(track)
            if len(self.done)>128: self.done=self.done[-128:]
            self.fifo.lock.release()

    def clear(self):
        self.fifo.lock.acquire()
        self.fifo.data=[]
        self.fifo.lock.release()


    def remove_track(self, urls):
        if isinstance(urls, (list, tuple)):
            for x in urls:
                self.remove_track(x)
            return

        self.fifo.lock.acquire()
        for i in range(len(self.fifo.data)):
            x=self.fifo.data[i]
            if x.url==urls:
                self.fifo.data[i]=None
        self.fifo.lock.release()

    def add_track(self, tracks):
        if isinstance(tracks, str):
            if tracks.startswith("https://open.spotify.com/track/"):
                return self.add_track(self.spot.track(tracks))
            if tracks.startswith("https://open.spotify.com/artist/"):
                return self.add_track(self.spot.artist_tracks(tracks))
            if tracks.startswith("https://open.spotify.com/album/"):
                return self.add_track(self.spot.album_tracks(tracks))

            raise DownloaderException("add_track: la chaine passée (%s) n'est pas une url valide" % tracks)
        if isinstance(tracks, TrackSet):
            return self.add_track(tracks.tracks)
        if isinstance(tracks, (list, tuple)):
            n=0
            for track in tracks:
                self.fifo.push(track)
                n +=1
            return n
        if isinstance(tracks, dict):
            return self.add_track(TrackEntry(dict))

        if isinstance(tracks, TrackEntry):
            self.fifo.push(tracks)
            return 1

        raise DownloaderException("add_track: le type passé (%s) est inattendu " % type(tracks).__name__)


