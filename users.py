import json
import time

from http_server import utils
from http_server.sqlite_conn import SQConnector

from TrackSet import TrackEntry
from config import cfg


class BadUserException(Exception):
    pass


class ImportException(Exception):
    pass


def str2json(x):
    return json.loads(x.replace("°", "'"))

def json2str(x):
    y= json.dumps(x).replace("'", "°")
    return y

def escape(x):
    return x.replace("'", "°")

def unescape(x):
    return x.replace("°", "'")



class User:

    def __init__(self, conn):
        self.conn = conn
        self.name = ""
        self.oldname = ""
        self.password = ""
        self.api = ""
        self.id=utils.new_id()
        self.data = {}
        self.permission = ""

    def set_password(self, password):
        self.password = utils.password(password)
        self.conn.exec("update users set password='%s' where name='%s' " % (self.password, self.name))
        self.conn.commit()

    def set_perm(self, p, val):
        if val:
            if not p in self.permission:
                self.permission += p
            else:
                return
        else:
            if p in self.permission:
                tmp = ""
                for c in self.permission:
                    if c != p:
                        tmp += p
                self.permission = tmp
            else:
                return
        self.conn.exec("update users set permission='%s' where name='%s' " % (self.permission, self.name))
        self.conn.commit()

    def has_perm(self, p: str):
        if len(p) > 1: return False
        return p in self.permission

    def is_admin(self):
        return self.has_perm("a")

    def set_admin(self, val):
        self.set_perm("a", val)

    def new_api(self):
        self.api = utils.new_key(64)
        self.conn.exec("update users set apikey='%s' where name='%s' " % (self.api, self.name))
        self.conn.commit()
        return self.api

    def check_password(self, pwd):
        return utils.password(pwd)==self.password



    @staticmethod
    def default_user_data(data):
        tmp = {
            "default_search": None
        }
        for key in data:
            tmp[key] = data[key]
        return tmp

    @staticmethod
    def load(conn, name):
        if isinstance(name, str):
            row = conn.onerow("select * from users where name='%s' " % name)
        else:
            row = name
        x = User(conn)
        x.id=row[0]
        x.name = row[1]
        x.oldname = row[1]
        x.password = row[2]
        x.api = row[3]
        x.data = User.default_user_data(json.loads(row[4]) if row[4] else {})
        x.permission = row[5] if row[5] else ""
        return x

    def save(self):
        if len(self.conn.exec("select * from users where name='%s' "% self.name)):
            self.conn.exec(
                "update users set name='%s', password='%s', apikey='%s', data='%s' permission='%s' where id='%s' " % (
                    self.name, self.password, self.api, json.dumps(self.data), self.permission, self.id
                ))
        else:
            self.conn.exec("insert into users values ('%s', '%s', '%s', '%s', '%s', '%s')" %(
                self.id, self.name, self.password, self.api, json.dumps(self.data), self.permission))
        self.conn.commit()
        self.oldname = self.name

    def replace_from_js(self, js):
        if js["name"] != self.name:
            raise BadUserException("utilisateur attendu '%s', trouvé '%s'" % (
                self.name, js["name"]
            ))
        n = self.conn.one("select count(*) from %s where ownnote or tosee or seen or comment or lists" % self.name)
        if n > len(js["db"]):
            raise ImportException("Le nouveau fichier contient moins de donné qu'actuellement")
        self.conn.exec("drop table %s " % self.name)
        self.conn.exec("drop table %s_requests " % self.name)
        self.conn.exec("drop table %s_lists " % self.name)
        User.import_user(self.conn, js)

    @staticmethod
    def create_user(conn, js):
        """
        js: {
            name: name,
            password: password,
            admin: admin (False)
        }
        :param conn:
        :param js:
        :return:
        """
        return User.import_user(conn,
                                {"name": js["name"]},
                                password=js["password"],
                                isadmin=js["admin"] if js["admin"] else False)

    @staticmethod
    def delete_user(conn, name):
        conn.exec("delete from users where name='%s' " % name)
        conn.commit()

    @staticmethod
    def import_user(conn, js, password="", isadmin=False):
        username = js["name"]


        return User.load(conn, username)


class Connector(SQConnector):

    USERS_SCHEM="""create table users (
                id text,
                name text,
                password text,
                apikey text,
                data text,
                permission text
                ) """
    HISTORY_SCHEM="""create table history (
                data text,
                type text,
                uuid text,
                search text,
                timestamp float
                )"""
    QUEUE_SCHEM="""create table queue (
                data text,
                uuid text,
                timestamp float
                )"""

    LOG_ALBUM_SCHEM = """create table log_album (
            name text,
            year text,
            uuid text,
            artist_uuid text,
            timestamp float
        )
        """
    LOG_ARTIST_SCHEM = """create table log_artist (
            name text,
            uuid text,
            timestamp float
        )
        """
    LOG_TRACK_SCHEM = """create table log_track (
            data text,
            uuid text,
            state text,
            error text,
            album_uuid text,
            artist_uuid text,
            timestamp float
        )
        """
    def __init__(self, file):
        super().__init__(file)
        self.users={}
        self.init_base()
        self.load_users()



    def _log_track(self, track):
        self.exec("insert into log_track values ('%s', '%s', '%s', '%s', '%s', '%s', %f)"%(
            json2str(track.json()), track.uuid, TrackEntry.STATE_QUEUED,
            "", track.album_uuid, track.artist_uuid, time.time()
        ))

    def _log_album(self, album):
        self.exec("insert into log_album values ('%s', '%s', '%s', '%s', %f)"%(
            escape(album.name), album.year, album.uuid, album.artist_uuid, time.time()
        ))
        for track in album:
            self._log_track(track)

    def _log_artist(self, art):
        self.exec("insert into log_artist values ('%s', '%s', %f)"%(
            escape(art.name), art.uuid, time.time()
        ))
        for alb in art.albums:
            self._log_album(art.albums[alb])

    def log_refer(self, refer):
        data = refer.artists
        for art in data:
            self._log_artist(data[art])
        self.commit()

    def load_users(self):
        ret  = self.exec("select name from users;")
        for x in ret:
            usr = User.load(self,x[0])
            self.__setitem__(usr.name, usr)

    def __contains__(self, item):
        return item in self.users

    def __getitem__(self, item):
        return self.users[item]

    def __setitem__(self, key, value):
        if isinstance(value, User):
            self.users[key]=value
        else:
            raise BadUserException()

    def get_pended_queue(self):
        ret=self.exec("select data from queue order by timestamp")
        return list(map(lambda x: TrackEntry.from_track_entry_json(
            json.loads(x[0].replace('°', "'"))), ret))

    def remove_from_queue(self, track):
        if isinstance(track, TrackEntry): track=track.json()
        self.exec("delete from queue where uuid='%s'"%track["uuid"])
        self.commit()

    def add_to_queue(self, track, commit=False):
        if isinstance(track, TrackEntry): track=track.json()
        if self.one("select count(*) from queue where uuid='%s'"%track["uuid"])==0:
            self.exec("insert into queue values ('%s', '%s', %f)"%(
                json.dumps(track).replace("'", '°'), track["uuid"],  time.time()
            ))
        if commit: self.commit()

    def create_user(self, name, isAdmin, password=""):
        usr = User(self)
        usr.name=name
        usr.save()
        usr.set_password(password)
        usr.set_admin(isAdmin)
        self.__setitem__(name, usr)

    def init_base(self):
        if not self.table_exists("users"):
            self.exec(Connector.USERS_SCHEM)
            self.conn.commit()
            self.create_user(cfg["auth.default_user.name"], True, cfg["auth.default_user.password"])

        if not self.table_exists("history"):
            self.exec(Connector.HISTORY_SCHEM)
            self.conn.commit()

        if not self.table_exists("queue"):
            self.exec(Connector.QUEUE_SCHEM)
            self.conn.commit()

        if not self.table_exists("log_track"):
            self.exec(Connector.LOG_TRACK_SCHEM)
            self.conn.commit()

        if not self.table_exists("log_album"):
            self.exec(Connector.LOG_ALBUM_SCHEM)
            self.conn.commit()

        if not self.table_exists("log_artist"):
            self.exec(Connector.LOG_ARTIST_SCHEM)
            self.conn.commit()

    LOG_DEFAULT_QUERY={
        "offset" : 0,
        "limit" : 50,
        "type" : "track",
        "date-min" : None,
        "date-max" : None
    }

    def set_logged_track_state(self, track, commit=True):
        self.exec("update log_track set state='%s', error='%s', timestamp=%f where uuid='%s'"%(
            track.state, escape(track.error), time.time(), track.uuid
        ))
        if commit: self.commit()

    def get_logged_track(self, uuid):
        js, state, error = self.onerow("select data, state, error from log_track where uuid='%s'"%uuid, False)
        js = str2json(js)
        js["state"]=state
        js["error"]=unescape(error)
        return js


    def log_set_ok(self, track):
        track.state=TrackEntry.STATE_OK
        track.error=None
        self.set_logged_track_state(track)
        self.remove_from_queue(track)

    def log_set_fail(self, track, error):
        track.state=TrackEntry.STATE_ERROR
        track.error=error
        self.set_logged_track_state(track)
        self.remove_from_queue(track)

    def log_set_queued(self, track):
        track.state=TrackEntry.STATE_QUEUED
        track.error=None
        self.set_logged_track_state(track)
        self.add_to_queue(track)

    def _get_log_tracks(self, album_uuid):
        query="select data, state, error, timestamp from log_track where album_uuid='%s'" % album_uuid
        ret = self.exec(query)
        out=[]
        for x in ret:
            js, state, error, ts = x
            js = str2json(js)
            js["state"] = state
            js["error"] = error
            js["timestamp"] = ts
            out.append(js)
        return out


    def _get_log_albums(self, artist_uuid):
        query="select name, year, uuid from log_album where artist_uuid='%s' order by timestamp" % artist_uuid
        ret = self.exec(query)
        albums=[]
        for x in ret:
            name, year, uuid = x
            albums.append({
                "name" : unescape(name),
                "year" : year,
                "tracks" : self._get_log_tracks(uuid)
            })
        return albums

    def get_log(self, query=LOG_DEFAULT_QUERY):
        prefix="select * from log_artist"
        suffix = " order by timestamp desc"
        suffix += (" limit %s " % query["limit"]) if query["limit"] != "-1" else ""
        suffix += (" offset %s " % query["offset"]) if query["offset"] != "0" else ""
        artists=[]
        tmp = self.exec(prefix+suffix, False)
        for x in tmp:
            name, uuid, ts = x
            artists.append({
                "name" : unescape(name),
                "timestamp" : ts,
                "albums" : self._get_log_albums(uuid)
            })
        return {
            "data" : artists,
            "total" : self.one("select count(uuid) from log_artist")
        }

    def clear_logs(self):
        self.exec("delete from log_album")
        self.exec("delete from log_artist")
        self.exec("delete from log_track")
        self.conn.commit()

