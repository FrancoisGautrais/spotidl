import os

from http_server import log
from spotdl.command_line.exceptions import NoYouTubeVideoFoundError

from config import config as cfg
import spotdl
from spotdl.authorize.services import AuthorizeSpotify
from spotdl.config import DEFAULT_CONFIGURATION
from spotdl.encode.encoders import EncoderFFmpeg
from spotdl.helpers import SpotifyHelpers
from spotdl.metadata_search import MetadataSearch
from spotdl.track import Track

import config
from TrackSet import TrackSet, TrackEntry


def has_artist(track, artist_id):
    artists=track["artists"]
    for art in artists:
        if art["id"]==artist_id:
            return True
    return False



class SpotDlWrapper:

    def __init__(self, init=True):
        self.spotipy=None
        self.tool=None
        self.dir=config.config["output.dir"]
        self.format=config.config["output.format"]
        self.ext=config.config["output.extension"]
        self.completeFormat=os.path.join(self.dir, self.format)
        if init: self.init()

    def init(self):
        self.spotipy=AuthorizeSpotify(
            client_id=DEFAULT_CONFIGURATION["spotify-downloader"]["spotify_client_id"],
            client_secret=DEFAULT_CONFIGURATION["spotify-downloader"]["spotify_client_secret"],
        )
        self.tool=SpotifyHelpers(self.spotipy)


    def search(self, query, type):
        return self.spotipy.search(query, type=type)

    def download_track(self, track, progress, youtubeurl=None):
        log.debug("Récupération des metadata %s " % track)
        metadata = self.get_metadata(track, youtubeurl)
        return self.download_track_with_meta(metadata, progress)




    def download_track_with_meta(self, metadata, progress):
        stream = metadata["streams"].get(
               quality=config.config["output.quality"],
                preftype="opus",
                )
        if(not stream):
            raise NoYouTubeVideoFoundError("Aucun stream correspondant aux préférence")

        track = Track(metadata)
        filename = spotdl.metadata.format_string(
            self.completeFormat,
            metadata,
            output_extension=self.ext,
            )


        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        log.info("Téléchargement %s " % filename)
        #track.download_while_re_encoding(stream, filename)
        self.download_while_re_encoding(track, stream, filename, progress)

        track.apply_metadata(filename)

        return TrackEntry(metadata)

    def download_while_re_encoding(self, track, stream, filename, progress,
                                   target_encoding=None,
                                   encoder=EncoderFFmpeg(cfg["utils.ffmpeg"], False)):

        total_chunks = track._calculate_total_chunks(stream["filesize"])

        process = encoder.re_encode_from_stdin(
            stream["encoding"],
            filename,
            target_encoding=target_encoding
        )
        response = stream["connection"]

        progress.new_task(stream["filesize"])
        while not progress.is_finished():
            chunk = response.read(track._chunksize)
            process.stdin.write(chunk)
            progress.progress(chunk)

        process.stdin.close()
        process.wait()

    def get_metadata(self, track, youtubeurl=None):
        subtracks = track.split("::")
        download_track = subtracks[0]
        custom_metadata_track = len(subtracks) > 1
        if custom_metadata_track:
            metadata_track = subtracks[1]
        else:
            metadata_track = download_track

        search_metadata = MetadataSearch(
            metadata_track
        )

        ret=search_metadata.on_youtube_and_spotify()

        if youtubeurl:
            tmp=search_metadata.providers["youtube"].from_url(youtubeurl)
            ret["streams"]=tmp["streams"]
        return ret


    def fetch_album(self, album_uri):
        return self.tool.fetch_album(album_uri)

    def track(self, uri):
        tr = self.spotipy.track(uri)
        return TrackEntry(tr)

    def artist_tracks(self, artist_uri):
        albums = self.tool.fetch_albums_from_artist(artist_uri)
        ts = TrackSet()
        artist=self.spotipy._get_id("artist", artist_uri) if artist_uri else None
        for album in albums:
            if not artist_uri or  has_artist(album, artist):
                ts.add_tracks(self.album_tracks(album["id"], artist_uri))
        return ts

    def album_tracks(self, album_uri, artist_uri=None):
        tmp=self.spotipy.album_tracks(album_uri)
        alb=self.spotipy.album(album_uri)
        n=0
        artist=self.spotipy._get_id("artist", artist_uri) if artist_uri else None
        newTracks=[]
        for track in tmp["items"]:
            if not artist_uri or has_artist(track, artist):
                n+=1
                track["album"]=alb["name"]
                newTracks.append(track)
        tmp["items"]=newTracks
        tmp["total"]=n
        return TrackSet(tmp["items"])

    def _download(self, tracks, progress, url=False):
        if isinstance(tracks, str):
            if tracks.startswith("https://open.spotify.com/track/"):
                return self.download_track(tracks, progress, url)
            if tracks.startswith("https://open.spotify.com/artist/"):
                return self._download(self.artist_tracks(tracks), progress)
            if tracks.startswith("https://open.spotify.com/album/"):
                return self._download(self.album_tracks(tracks), progress)
        if isinstance(tracks, TrackSet):
            return self._download(tracks.tracks, progress)
        if isinstance(tracks, TrackEntry):
            return self._download(tracks.url, progress, tracks.youtube_url)
        if isinstance(tracks, (list,tuple)):
            ts = TrackSet()
            for track in tracks:
                self.download_track(track.url, progress, tracks.youtube_url)
            return ts

    def download(self, tracks, progress):
        tracks=self._download(tracks, progress)
        if isinstance(tracks, TrackEntry):
            return TrackSet(tracks)
        if isinstance(tracks, TrackSet):
            return tracks
        raise Exception("Type de retour de _download inattendu")

