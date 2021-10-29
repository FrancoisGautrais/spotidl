from django.contrib import admin

# Register your models here.
from django.urls import path

from .models import Preferences, Queue, LogTrack, LogAlbum, LogArtist

admin.site.register(Preferences)