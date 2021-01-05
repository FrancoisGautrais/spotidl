
def indent(i):
    return "  "*i

class ArtistEntryShort:
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

class TrackEntry:
    def __init__(self, track):
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
            if isinstance(self.album, dict):
                self.album=self.album["name"]
        else:
            self.artists=[]
            self.duration=None
            self.url=None
            self.name=None
            self.track_number=None
            self.album=None

    def json(self):
        return {
            "type" : "track",
            "artists" : list(map(lambda x: x.json(), self.artists)),
            "duration" : self.duration,
            "url" : self.url,
            "name" : self.name,
            "track_number" : self.track_number,
            "album": self.album
        }

    def trackset(self):
        return TrackSet(self)
    def __str__(self): return self.str(0)

    def __repr__(self): return str(self)
    def str(self,i ):
        return indent(i)+" feat ".join(list(map(lambda x: x.name, self.artists)))+" - %s (%f s)"%(self.name, self.duration)

class AlbumEntry(list):
    def __init__(self):
        super().__init__()
        self.ids={}
        self.name=None
        self.artists=[]

    def set_name(self, name): self.name=name

    def add_artist(self, x):
        if isinstance(x, (list, tuple)):
            for y in x:
                self.add_artist(y)
        elif isinstance(x, ArtistEntryShort):
            if not x.id in self.ids:
                self.ids[x.id]=True
                self.artists.append(x)

    def append(self, track):
        self.add_artist(track.artists)
        super().append(track)

    def json(self):
        return {
            "type" : "album",
            "artists" : list(map( lambda x: x.json(), self.artists)),
            "name" : self.name,
            "tracks" :  list(map( lambda x: x.json(), self))
        }

    def trackset(self):
        return TrackSet(self)

    def __str__(self): return self.str()
    def __repr__(self): return str(self)

    def str(self, i=0):
        return indent(i)+self.name+"("+" feat ".join(list(map(lambda x: x.name, self.artists)))+") "+"\n"\
                        +"\n".join(list(map(lambda t: t.str(i+1), self)))

class ArtistEntry:

    def __init__(self):
        self.tracks=[]
        self.albums={}

    def set_name(self, n): self.name=n

    def add_tracks(self, track):
        if isinstance(track, (list, tuple)):
            for x in track:
                self.add_tracks(x)
            return
        if not isinstance(track, TrackEntry):
            track=TrackEntry(track)
        self.tracks.append(track)
        alb = track.album
        if not alb: alb=None
        if not alb in self.albums:
            self.albums[alb]=AlbumEntry()
            self.albums[alb].set_name(alb)
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
            "name" : self.name
        }

class TrackSet:
    def __init__(self, tracks=[]):
        self.tracks=[]
        self.artists={}
        self.add_tracks(tracks)

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
            "count" : len(self.tracks)
        }

    def __str__(self): return self.str()
    def __repr__(self): return str(self)

    def str(self, i=0):
        return indent(i)+"\n".join(list(map(lambda t: t.str(i), self.artists.values())))