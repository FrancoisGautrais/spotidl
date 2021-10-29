from django.shortcuts import render


from .base import BaseHandler
from .queue import QueueHandler
from .server import ServerHandler
from .subsonic import SubsonicHandler
from .user import UserHandler
from .views import ViewsHandler
from .log import LogHandler

user = BaseHandler.get("UserHandler")
views = BaseHandler.get("ViewsHandler")
log = BaseHandler.get("LogHandler")
queue = BaseHandler.get("QueueHandler", log)
subsonic = BaseHandler.get("SubsonicHandler")
server = BaseHandler.get("ServerHandler", queue, subsonic)
