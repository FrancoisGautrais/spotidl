import json
import time

from http_server import utils
from http_server.sqlite_conn import SQConnector
from config import cfg


class BadUserException(Exception):
    pass


class ImportException(Exception):
    pass




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

    def log_refer(self, refer):
        if not isinstance(refer, (list, tuple)): refer=[refer]
        for re in refer:
            self.conn.exec("insert into history values ('%s', '%s', '%s', %f)" % (
                json.dumps(re).replace("'", "°"), "refer", self.id, time.time()
            ))
        self.conn.commit()


    def log_tracks(self, tracks):
        for track in tracks:
            self.conn.exec("insert into history values ('%s', '%s', '%s', %f)" % (
                json.dumps(track).replace("'", "°"), "track", self.id, time.time()
            ))
        self.conn.commit()

    LOG_DEFAULT_QUERY={
        "offset" : 0,
        "limit" : 50,
        "type" : "track",
        "date-min" : None,
        "date-max" : None
    }
    def get_log(self, query=LOG_DEFAULT_QUERY):
        out=[]
        prefix_count="select count(type) from history where user='%s'"%self.id
        prefix="select data, type, timestamp from history where user='%s'"%self.id
        q=""
        if query["type"]!="all": q+=" and type='%s' "%query["type"]
        if "date-min" in query and query["date-min"]: q+=" and timestamp>=%d" % query["date-min"]
        if "date-max" in query and query["date-max"]: q+=" and timestamp<=%d" % query["date-max"]
        suffix=" order by timestamp desc"
        suffix+= (" limit %s " % query["limit"]) if query["limit"]!="-1" else ""
        suffix+=(" offset %s " % query["offset"]) if query["offset"]!="0" else ""
        tmp=self.conn.exec(prefix+q+suffix)
        for x in tmp:
            out.append({
                "data" : json.loads(x[0].replace("°", "'")),
                "type" : x[1],
                "timestamp" : x[2]
            })
        return {
            "data" : out,
            "total" : self.conn.one(prefix_count+q)
        }


    def clear_logs(self):
        self.conn.exec("delete from history where user='%s'"%self.id)
        self.conn.commit()



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
                user text,
                timestamp float
                )"""
    def __init__(self, file):
        super().__init__(file)
        self.users={}
        self.init_base()
        self.load_users()


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

