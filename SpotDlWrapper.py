import os

import spotdl
from spotdl.authorize.services import AuthorizeSpotify
from spotdl.config import DEFAULT_CONFIGURATION
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
        self.dir=config.OUTPUT_DIR
        self.format=config.OUTPUT_FORMAT
        self.completeFormat=os.path.join(self.dir, self.format)
        if init: self.init()

    def init(self):
        self.spotipy=AuthorizeSpotify(
            client_id=DEFAULT_CONFIGURATION["spotify-downloader"]["spotify_client_id"],
            client_secret=DEFAULT_CONFIGURATION["spotify-downloader"]["spotify_client_secret"],
        )
        self.tool=SpotifyHelpers(self.spotipy)

    def download_track(self, track):
        print("Fetching metadata for '%s'"%track)
        metadata = self.get_metadata(track)
        return self.download_track_with_meta(metadata)

    def download_track_with_meta(self, metadata):
        stream = metadata["streams"].get(
               quality="best",
                preftype="opus",
                )
        track = Track(metadata)
        filename = spotdl.metadata.format_string(
            self.completeFormat,
            metadata,
            output_extension="mp3",
            )

        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        print("Dwonloading %s " % filename)
        track.download_while_re_encoding(stream, filename)

        track.apply_metadata(filename)

        return TrackEntry(metadata)


    def get_metadata(self, track):
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

        return  search_metadata.on_youtube_and_spotify()

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

    def _download(self, tracks):
        if isinstance(tracks, str):
            if tracks.startswith("https://open.spotify.com/track/"):
                return self.download_track(tracks)
            if tracks.startswith("https://open.spotify.com/artist/"):
                return self._download(self.artist_tracks(tracks))
            if tracks.startswith("https://open.spotify.com/album/"):
                return self._download(self.album_tracks(tracks))
        if isinstance(tracks, TrackSet):
            return self._download(tracks.tracks)
        if isinstance(tracks, TrackEntry):
            return self._download(tracks.url)
        if isinstance(tracks, (list,tuple)):
            ts = TrackSet()
            for track in tracks:
                ts.add_tracks(self.download_track(track.url))
            return ts

    def download(self, tracks):
        tracks=self._download(tracks)
        if isinstance(tracks, TrackEntry):
            return TrackSet(tracks)
        if isinstance(tracks, TrackSet):
            return tracks
        raise Exception("Type de retour de _download inattendu")

