import json
import time

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
import utils
from TrackSet import TrackEntry, AlbumEntry, ArtistEntry
from utils import Jsonable


class JsonField(models.TextField):
    def __init__(self, classe : type=None, *args, **kwargs):
        if classe is not None and not issubclass(classe, Jsonable):
            raise Exception("Erreur le type de Jsonfield doit être une classe hérité de Jsonable ou None")
        self.classe = classe
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if isinstance(value, str) or value is None:
            return value
        if isinstance(value, dict):
            return json.dumps(value)
        if self.classe and isinstance(value, self.classe):
            return json.dumps(value.to_json())
        raise Exception()

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        if isinstance(value, str):
            return self.classe.from_json(json.loads(value))
        if isinstance(value, dict):
            return self.classe.from_json(value)
        raise Exception()

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            return self.classe.from_json(json.loads(value))
        if isinstance(value, dict):
            return self.classe.from_json(value)
        raise Exception()



class History(models.Model):
    data = models.TextField()
    type = models.TextField()
    uuid = models.TextField()
    search = models.TextField()
    timestamp = models.FloatField()

class PreferencesData(Jsonable):
    FIELDS = []
    DEFAULT = {

    }

    def __init__(self, **kwargs):
        kwargs = utils.deepassign({}, PreferencesData.DEFAULT, kwargs)
        for k in kwargs:
            if k in PreferencesData.FIELDS:
                setattr(self, k, kwargs[k])

    def to_json(self):
        return { k: ((getattr(self,k)) if hasattr(self,k) else None) for k in PreferencesData.FIELDS}

    @staticmethod
    def from_json(js : (dict, list, int, float)):
        return PreferencesData(**js)

class Preferences(models.Model):
    user = models.ForeignKey(User, primary_key=True, on_delete=models.CASCADE)
    data = JsonField(classe=PreferencesData)


    @staticmethod
    def get(username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Exception("OK !!")
        try:
            return Preferences.objects.get(user=user)
        except Preferences.DoesNotExist:
            return Preferences.new(user.username)


    @staticmethod
    def new(username, **kwargs):
        user = User.objects.get(username=username)
        return Preferences.objects.create(user=user, data = PreferencesData(**kwargs))


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
        LogAlbum.objects.create(
            name=album.name,
            year=album.year,
            uuid=album.uuid,
            artist_uuid=album.artist_uuid,
            timestamp=time.time()
        )
        for track in album:
            LogTrack.log(track)

    @staticmethod
    def get(**kwargs):
        res = LogAlbum.objects.filter(**kwargs)
        out = []
        for x in res:
            out.append(
                {
                    "name" : x.name,
                    "year" : x.year,
                    "tracks" : LogTrack.get(album_uuid=x.uuid)
                }
            )
        return list(out)


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
        LogArtist.objects.create(
            name=artist.name,
            uuid=artist.uuid,
            timestamp=time.time()
        )
        for alb in artist.albums:
            LogAlbum.log(artist.albums[alb])

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
        LogTrack.objects.create(
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
    def get(**kwargs):
        tracks = LogTrack.objects.filter(**kwargs)
        out = []
        for track in tracks:
            js =  json.loads(track.data)
            js["state"] = track.state
            js["error"] = track.error
            js["timestamp"] = track.timestamp
            out.append(js)
        return out

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


admin.site.register(LogTrack)
admin.site.register(LogAlbum)
admin.site.register(LogArtist)
admin.site.register(Queue)
admin.site.register(History)

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
        out=[]
        for art in base.values("name", "uuid", "timestamp"):
            art["albums"] = LogAlbum.get(artist_uuid=art["uuid"])
            out.append(art)

        return {
            "data" : out,
            "total" : len(out)
        }

    def clear_logs(self):
        LogArtist.clear()
        LogAlbum.clear()
        LogTrack.clear()

