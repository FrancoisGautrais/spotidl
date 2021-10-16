import json
import time

from django.db import models

# Create your models here.
from TrackSet import TrackEntry, AlbumEntry, ArtistEntry

class History(models.Model):
    data = models.TextField()
    type = models.TextField()
    uuid = models.TextField()
    search = models.TextField()
    timestamp = models.FloatField()



class Queue(models.Model):
    data = models.TextField()
    uuid = models.TextField()
    timestamp = models.FloatField()

    @staticmethod
    def from_json(track):
        return Queue.objects.create(
            data=json.dumps(track).replace("'", '°'),
            uuid=track["uuid"],
            timestamp=time.time()
        )


    @staticmethod
    def add(track):
        if isinstance(track, TrackEntry): track=track.json()
        qs = Queue.objects.filter(uuid=track["uuid"])
        if not qs:
            Queue.from_json(track)

    @staticmethod
    def remove(track):
        if isinstance(track, TrackEntry): track=track.json()
        Queue.objects.filter(uuid=track["uuid"]).delete()

    @staticmethod
    def get(): #get_pended_queue
        return [ elem.data.replace('°', "'") for elem in Queue.objects.all() ]

    @staticmethod
    def clear():
        Queue.objects.all().delete()


class LogAlbum(models.Model):
    name = models.TextField()
    year = models.TextField()
    uuid = models.TextField()
    artist_uuid = models.TextField()
    timestamp = models.FloatField()

    @staticmethod
    def log(album : AlbumEntry):
        LogTrack.object.create(
            name=album.name,
            year=album.year,
            uuid=album.uuid,
            artist_uuid=album.artist_uuid,
            timestamp=time.time()
        )

    @staticmethod
    def clear():
        LogAlbum.objects.all().delete()

    @staticmethod
    def get_from_artist(uuid):
        return LogAlbum.objects.filter(artist_uuid=uuid).values("name", "year", "uuid")

class LogArtist(models.Model):
    name = models.TextField()
    uuid = models.TextField()
    timestamp = models.FloatField()

    @staticmethod
    def log(artist : ArtistEntry):
        LogTrack.object.create(
            name=artist.name,
            uuid=artist.uuid,
            timestamp=time.time()
        )

    @staticmethod
    def clear():
        LogArtist.objects.all().delete()

class LogTrack(models.Model):
    data = models.TextField()
    uuid = models.TextField()
    state = models.TextField()
    error = models.TextField()
    album_uuid = models.TextField()
    artist_uuid = models.TextField()
    timestamp = models.FloatField()


    @staticmethod
    def clear():
        LogTrack.objects.all().delete()

    @staticmethod
    def log(track : TrackEntry):
        LogTrack.object.create(
            data=json.dumps(track.json()),
            uuid=track.uuid,
            state=TrackEntry.STATE_QUEUED,
            error="",
            album_uuid=track.album_uuid,
            artist_uuid=track.artist_uuid,
            timestamp=time.time()
        )

    @staticmethod
    def set(track : TrackEntry):
        t = LogTrack.objects.get(uuid=track.uuid)
        t.state=TrackEntry.STATE_QUEUED,
        t.error=track.error,
        t.timestamp=time.time()

    @staticmethod
    def get(uuid : str):
        return  LogTrack.objects.get(uuid=uuid)

    @staticmethod
    def set_ok(track):
        track.state=TrackEntry.STATE_OK
        track.error=None
        LogTrack.set(track)
        Queue.remove(track)


    @staticmethod
    def set_fail(track, error):
        track.state=TrackEntry.STATE_ERROR
        track.error=error
        LogTrack.set(track)
        Queue.remove(track)


    @staticmethod
    def set_queued(track):
        track.state=TrackEntry.STATE_QUEUED
        track.error=None
        LogTrack.set(track)
        Queue.add(track)

    @staticmethod
    def get_from_artist(uuid):
        tmp = LogTrack.objects.filter(artist_uuid=uuid).values("data", "state", "error", "timestamp")
        for x in tmp:
            x["data"] = json.loads(x["data"])
        return tmp

def LOG_DEFAULT_QUERY():
    return{
        "offset" : 0,
        "limit" : 50,
        "type" : "track",
        "date-min" : None,
        "date-max" : None
    }


class DBLogger:

    def log_refer(self, refer):
        data = refer.artists
        for art in data:
            LogArtist.log(data[art])


    def get_log(self, query = None):
        if query is None: query = LOG_DEFAULT_QUERY()
        base =  LogArtist.objects.all().order_by("-timestamp")
        limit = int(query["limit"])
        offset = int(query["offset"])
        if limit>0 :
            base = base[offset:offset+limit]
        else:
            base = base[offset:]

        return {
            "artists" : base.values("name", "uuid", "timestamp"),
            "total" : len(base)
        }

    def clear_logs(self):
        LogArtist.clear()
        LogAlbum.clear()
        LogTrack.clear()

