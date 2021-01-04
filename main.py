
import logging
import os
import time

import spotdl
import spotipy
from spotdl.authorize.services import AuthorizeSpotify
from spotdl.command_line.core import Spotdl, MetadataSearch
from spotdl.command_line.exceptions import NoYouTubeVideoFoundError, NoYouTubeVideoMatchError
from spotdl.encode.encoders import EncoderFFmpeg
from spotdl.helpers import SpotifyHelpers
from spotdl.track import Track
from spotdl.config import DEFAULT_CONFIGURATION

from TrackSet import TrackSet

logger = logging.getLogger(name=__name__)
"""
from downloader import Downloader

dl = Downloader()
#"https://open.spotify.com/album/4eEbMGFrUutpgGIq4dmMOm"
dl.start()
while(True) :
    line = input("Entrez une URL\n").lstrip(" ").rstrip(" ")
    if line.startswith("https://open.spotify.com/"):
        n=dl.add_track(line)
        print("%d pistes ajourées en file d'attente"%n)
    if line.startswith("add "):
        line=line[4:].lstrip(" ")
        n=dl.add_track(line)
        print("%d pistes ajourées en file d'attente"%n)

    if line.startswith("count"):
        print(len(dl.fifo.data))
    if line.startswith("list"):
        print("\n".join(list(map(lambda x: str(x), dl.fifo.data))))
    if line.startswith("running"):
        print("\n".join(list(map(lambda x: str(x), dl.running.values()))))
    if line.startswith("done"):
        print("\n".join(list(map(lambda x: str(x), dl.done))))
    if line.startswith("exit"):
        dl.exit()
        exit()



"""

from server import DlServer

dl = DlServer()
dl.listen(8080)

