import json
from abc import ABCMeta, abstractmethod

import utils


class Jsonable:
    @abstractmethod
    def json(self):
        raise NotImplementedError("")

class JsonArray(list):
    def __init__(self):
        super().__init__()

    def json(self):
        return list(map(lambda x: (x.json() if isinstance(x, Jsonable) else x), self))



class ReferEntry(Jsonable):
    def __init__(self, url, js, type):
        self.url=url
        self.js=js
        self.type=type

    def json(self):
        return {
            "url" : self.url,
            "data" : self.js,
            "type" : self.type
        }

class Refer:
    def __init__(self):
        self.data=JsonArray()

    def add(self, x):
        for i in x.data:
            self.data.append(i)

    def add_track(self, url, x):
        self.data.append(ReferEntry(url, x.json(), "track"))


    """
    def add_track(self, url, x):
        self.data.append(ReferEntry(url, x.json(), "track"))

    def add_artist(self, url, x):
        name="None"
        for k in x.artists:
            name=k
            break
        self.data.append(ReferEntry(url, {
            "name" : name
        }, "artist"))


    def add_album(self, url, x):
        artist="None"
        album="None"
        for k in x.artists:
            artist=k
            for l in x.artists[k].albums:
                album=l
                if "year" in x.artists[k].albums[l]:
                    year=x.artists[k].albums[l]["year"]
                break
            break
        self.data.append(ReferEntry(url, {
            "album" : album,
            "artist" : artist
        }, "album"))

    def add_playlist(self, url, x):
        self.data.append(ReferEntry(url, {
        }, "playlist"))"""

    def json(self):
        return self.data.json()


def indent(i):
    return "  "*i

class ArtistEntryShort(Jsonable):
    def __init__(self, js):
        if js:
            self.name=js["name"]
            self.id=js["id"]
        else:
            self.name=None
            self.id=None

    def json(self):
        return {
            "name": self.name,
            "id" : self.id
        }

    def __str__(self): return self.name
    def __repr__(self): return str(self)
    def str(self): return str(self)



class TrackEntry(Jsonable):
    STATE_NONE="none"
    STATE_QUEUED="queued"
    STATE_ERROR="error"
    STATE_OK="ok"
    def __init__(self, track):
        self.failcount=0
        self.youtube_url=None
        self.uuid=utils.new_id()
        self.album_uuid=0
        self.artist_uuid=""
        self.state=TrackEntry.STATE_NONE
        self.error=None
        if track:
            self.artists=list(map(lambda x: ArtistEntryShort(x), track["artists"]))
            self.duration=None
            if "duration_ms" in track:
                self.duration=(track["duration_ms"]/1000)
            elif "duration" in track:
                self.duration = track["duration"]
            self.url=track["external_urls"]["spotify"] if "external_urls" in track else track["url"]
            self.name=track["name"]
            self.track_number=track["track_number"]
            self.album=track["album"] if "album" in track else "__none__"
            self.year=track["year"] if "year" in track else "-00"
            if isinstance(self.album, dict):
                self.year=self.album["release_date"][0:4]
                self.album=self.album["name"]
        else:
            self.artists=[]
            self.duration=None
            self.url=None
            self.name=None
            self.track_number=None
            self.album=None
            self.year=None


    @staticmethod
    def from_track_entry_json(x):
        if isinstance(x, str): x= json.loads(x)
        te = TrackEntry(None)
        te.artists=list(map(lambda y: ArtistEntryShort(y), x["artists"]))
        te.duration=x["duration"]
        te.url=x["url"]
        te.name=x["name"]
        te.track_number=x["track_number"]
        te.album=x["album"]
        te.year=x["year"]
        te.youtube_url=x["youtube_url"] if "youtube_url" in x else None
        te.uuid=x["uuid"]
        te.album_uuid=x["album_uuid"]
        te.artist_uuid=x["artist_uuid"]
        te.state=x["state"]
        te.error=x["error"]
        return te

    def json(self):
        return {
            "type" : "track",
            "artists" : list(map(lambda x: x.json(), self.artists)),
            "duration" : self.duration,
            "url" : self.url,
            "name" : self.name,
            "track_number" : self.track_number,
            "album": self.album,
            "year": self.year,
            "youtube_url" : self.youtube_url,
            "uuid" : self.uuid,
            "album_uuid" : self.album_uuid,
            "artist_uuid" : self.artist_uuid,
            "state" : self.state,
            "error" : self.error
        }

    def set_youtube_url(self, url):
        self.youtube_url=url

    def fail(self):
        self.failcount+=1
        return self

    def trackset(self):
        return TrackSet(self)
    def __str__(self): return self.str(0)

    def __repr__(self): return str(self)
    def str(self,i ):
        return indent(i)+" feat ".join(list(map(lambda x: x.name, self.artists)))+" - %s (%f s)"%(self.name, self.duration)

class AlbumEntry(list,Jsonable):
    def __init__(self):
        super().__init__()
        self.ids={}
        self.name=None
        self.year=None
        self.artists=[]
        self.uuid=utils.new_id()

    def set_name(self, name): self.name=name
    def set_year(self, year): self.year=year

    def add_artist(self, x):
        if isinstance(x, (list, tuple)):
            for y in x:
                self.add_artist(y)
        elif isinstance(x, ArtistEntryShort):
            if not x.id in self.ids:
                self.ids[x.id]=True
                self.artists.append(x)

    def append(self, track):
        track.album_uuid=self.uuid
        self.add_artist(track.artists)
        super().append(track)

    def json(self):
        return {
            "type" : "album",
            "artists" : list(map( lambda x: x.json(), self.artists)),
            "name" : self.name,
            "year" : self.year,
            "tracks" :  list(map( lambda x: x.json(), self)),
            "uuid" : self.uuid
        }

    def as_log_dict(self):
        return {
            "name": self.name,
            "year": self.year,
            "uuid" : self.uuid
        }

    def trackset(self):
        return TrackSet(self)

    def __str__(self): return self.str()
    def __repr__(self): return str(self)

    def str(self, i=0):
        return indent(i)+self.name+"("+" feat ".join(list(map(lambda x: x.name, self.artists)))+") "+"\n"\
                        +"\n".join(list(map(lambda t: t.str(i+1), self)))

class ArtistEntry(Jsonable):

    def __init__(self):
        self.tracks=[]
        self.albums={}
        self.uuid=utils.new_id()
        self.artist_uuid=""

    def set_name(self, n): self.name=n

    def add_tracks(self, track):
        if isinstance(track, (list, tuple)):
            for x in track:
                self.add_tracks(x)
            return
        if not isinstance(track, TrackEntry):
            track=TrackEntry(track)

        self.tracks.append(track)
        track.artist_uuid=self.uuid
        alb = track.album
        if not alb: alb=None
        if not alb in self.albums:
            self.albums[alb]=AlbumEntry()
            self.albums[alb].set_name(alb)

            try:
                self.albums[alb].set_year(track.year)
            except:
                pass
            self.albums[alb].artist_uuid=self.uuid

        self.albums[alb].append(track)

    def __str__(self): return self.str()
    def __repr__(self): return str(self)
    def str(self, i=0):
        return indent(i)+self.name+"\n"+"\n".join(list(map(lambda t: t.str(i+1), self.albums.values())))

    def trackset(self):
        return TrackSet(self.tracks)

    def append(self, track): self.add_tracks(track)

    def json(self):
        return {
            "type" : "artist",
            "albums" : list(map(lambda x: x.json(), self.albums.values())),
            "name" : self.name,
            "uuid" : self.uuid
        }

class TrackSet(Jsonable):
    def __init__(self, tracks=[]):
        self.tracks=[]
        self.artists={}
        self.add_tracks(tracks)
        self.refer=Refer()

    def add_refer(self, x):
        self.refer.add(x)

    def each(self, fct):
        for x in self.tracks:
            fct(x)

    def get_tracks(self): return self.tracks

    def add_tracks(self, track):
        if isinstance(track, TrackSet):
            self.add_tracks(track.tracks)
            return
        if isinstance(track, (list, tuple)):
            for x in track:
                self.add_tracks(x)
            return
        if not isinstance(track, TrackEntry):
            track=TrackEntry(track)
        self.tracks.append(track)
        art = track.artists[0].name
        if not art in self.artists:
            self.artists[art]=ArtistEntry()
            self.artists[art].set_name(art)
        self.artists[art].append(track)

    def trackset(self):
        return self

    def json(self):
        return {
            "artists" : list(map(lambda x: x.json(), self.artists.values())),
            "count" : len(self.tracks),
            "refer" : self.refer.json()
        }

    def __str__(self): return self.str()
    def __repr__(self): return str(self)

    def str(self, i=0):
        return indent(i)+"\n".join(list(map(lambda t: t.str(i), self.artists.values())))