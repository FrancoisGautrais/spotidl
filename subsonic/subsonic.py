import hashlib
import random
import time
import xml.etree.ElementTree as ET
import requests

class BadResponseException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class SubsonicResponse:

    ERROR_SUCCESS="success"
    ERROR_HTTP="http"
    ERROR_SUBSONIC="subsonic"
    def __init__(self):
        self.error_type=SubsonicResponse.ERROR_SUCCESS
        self.error_http=None
        self.error_subsonic_code=None
        self.error_subsonic_message=None
        self.data=None

    def json(self):
        if self.error_type==SubsonicResponse.ERROR_HTTP:
            return {
                "code" : -1,
                "message" : str(self.error_http)
            }
        elif self.error_type==SubsonicResponse.ERROR_SUBSONIC:
            return {
                "code" : self.error_subsonic_code,
                "message" : self.error_subsonic_message
            }
        return {
            "code" : 0,
            "message" : "ok"
        }

    def set_data(self, d):
        self.data=d

    def is_http_error(self):
        return self.error_type==SubsonicResponse.ERROR_HTTP

    def is_subsonic_error(self):
        return self.error_type==SubsonicResponse.ERROR_SUBSONIC

    def set_error_http(self, err):
        self.error_type=SubsonicResponse.ERROR_HTTP
        self.error_http=err

    def set_error_subsonic(self, code, message):
        self.error_type=SubsonicResponse.ERROR_SUBSONIC
        self.error_subsonic_code=code
        self.error_subsonic_message=message

    def get_error(self):
        if self.error_type==SubsonicResponse.ERROR_SUCCESS:
            return self.error_subsonic_code, self.error_subsonic_message
        elif self.error_type==SubsonicResponse.ERROR_HTTP:
            return self.error_http
        else:
            return None

    def fail(self):
        return self.error_type!=SubsonicResponse.ERROR_SUCCESS

    def ok(self):
        return self.error_type==SubsonicResponse.ERROR_SUCCESS

    def get_data(self):
        return self.data

    def __str__(self):
        if(self.error_type==SubsonicResponse.ERROR_SUCCESS):
            return "SubsonicRespone(OK, %s)" % str(self.data)
        elif self.error_type==SubsonicResponse.ERROR_HTTP:
            return "SubsonicRespone(ERR_HTTP, %s)" % str(self.error_http)
        elif self.error_type==SubsonicResponse.ERROR_SUBSONIC:
            return "SubsonicRespone(ERR_SUSBONIC, %d, %s)" %(
                self.error_subsonic_code,
                str(self.error_subsonic_message)
            )
    def __repr__(self): return str(self)


class Subsonic:
    SALT_CHARS="abcdefghijklmnopqrstuvwxyzaABCDEFGHIJKLMNOPQRSTUVWXY0123456789"
    def __init__(self, config):
        self.base_url=config["url"]
        self.password=config["password"]
        self.user=config["user"]
        self.app_name=config["app_name"] if "app_name" in config else "SpotiDL"

    def url(self, x):
        return "%s%s" % (self.base_url, x)

    @staticmethod
    def salt(n=16):
        out=""
        l=len(Subsonic.SALT_CHARS)-1
        for _ in range(n):
            out+=Subsonic.SALT_CHARS[random.randint(0,l)]
        return out

    def get_md5_pwd(self):
        salt=Subsonic.salt()
        return salt,hashlib.md5((self.password+salt).encode()).hexdigest()


    """
        Envoi d'une commande au serveur
        Params
            -url: l'url à rajouter après le nom de domaine et le port
        Retour (ROOT, CODE, MESSAGE)
            ROOT: l'objet reçu 
            OK: Si il y aeu un retour et qu'il est "ok"
            ERROR: Le message d'erreur
    """
    def _send(self, url):
        error=SubsonicResponse()
        salt, md5 = self.get_md5_pwd()
        params="%s?u=%s&t=%s&s=%s&v=1.12.0&c=%s" % (
            url, self.user, md5, salt, self.app_name
        )
        url = self.url(params)
        try:
            ret=requests.get(url)
        except requests.exceptions.ConnectionError as err:
            error.set_error_http(err)
            return error

        try:
            root=ET.fromstring(ret.content.decode("ascii"))
            error.set_data(root)
        except:
            error.set_error_http(BadResponseException("La réponse n'est pas du xml"))
            error.set_data(ret.content)
            return error

        if root.attrib["status"]!="ok":
            y = root.find(".//*")
            error.set_error_subsonic(int(y.attrib["code"]), y.attrib["message"])

        return error


    def start_scan(self):
        err=self._send("/rest/startScan")
        if err.fail():
            return err
        root=err.get_data()
        y=root.find(".//*")
        return y.attrib["scanning"], int(y.attrib["count"])

    """
        Ping le serveur subsonic
        Retour (OK, CODE, MESSAGE)
            OK: bool 
            CODE: le code si la connexion hhtp a aboutie sinon -1
            MESSAGE: Le message d'erreur
    """
    def test(self):
        err = self._send("/rest/ping.view")
        if err.ok():
            return True
        else:
            return err

    def scan_status(self):
        err=self._send("/rest/getScanStatus")
        if err.fail():
            return err
        y=err.get_data().find(".//*")
        return y.attrib["scanning"]=="true", int(y.attrib["count"])

    def scan_sync(self, t=1):
        out = self.start_scan()
        if isinstance(out, SubsonicResponse):
            return out
        out = self.scan_status()
        if isinstance(out, SubsonicResponse):
            return out
        while out[0]:
            out = self.scan_status()
            if isinstance(out, SubsonicResponse):
                return out
            time.sleep(t)
        return out[1]

