import os
import sys
import time
import mutagenx
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from music.tags import File

from music import models

unknown = lambda x: x or settings.UNKNOWN_TEXT

def artists(t, _artists):
    for artist in _artists:
        try:
            a = models.Artist.objects.get(name=unknown(artist.name))
        except models.Artist.DoesNotExist:
            try:
                if artist.musicbrainz_artistid:
                    a = models.Artist.objects.get(musicbrainz_artistid=artist.musicbrainz_artistid)
                else:
                    raise models.Artist.DoesNotExist('No musicbrainz artistid')
            except models.Artist.DoesNotExist:
                a = models.Artist(
                        name = unknown(artist.name),
                        sortname = artist.sortname or unknown(artist.name),
                        musicbrainz_artistid = artist.musicbrainz_artistid,
                    )
                a.save()

        a.genres.add(*genres(t.genres))
        yield a

def albumtypes(names):
    return [models.AlbumType.objects.get_or_create(name=name)[0] for name in names or []]

def albumstatus(names):
    return [models.AlbumStatus.objects.get_or_create(name=name)[0] for name in names or []]

def labels(names):
    return [models.Label.objects.get_or_create(name=name)[0] for name in names or []]

def genres(names):
    return [models.Genre.objects.get_or_create(name=name)[0] for name in names or []]

def country(name):
    if name:
        return models.Country.objects.get_or_create(name=name)[0]

def album(t):
    try:
        _album = models.Album.objects.get(title=t.album.title, artists__name__in = [unknown(a.name) for a in t.album.albumartists])
    except models.Album.DoesNotExist:
        try:
            if t.album.musicbrainz_albumid:
                _album = models.Album.objects.get(musicbrainz_albumid=t.album.musicbrainz_albumid)
            else:
                raise models.Album.DoesNotExist('No musicbrainz albumid')
        except models.Album.DoesNotExist:
            _album = models.Album(
                    title = unknown(t.album.title),
                    date = t.album.date,
                    country = country(t.album.country),
                    musicbrainz_albumid = t.album.musicbrainz_albumid,
                    musicbrainz_releasegroupid = t.album.musicbrainz_releasegroupid
                )
            _album.save()

    _album.artists.add(*artists(t, t.album.albumartists))
    _album.genres.add(*genres(t.genres))
    _album.labels.add(*labels(t.album.labels))
    _album.albumtypes.add(*albumtypes(t.album.albumtypes))
    _album.albumstatus.add(*albumstatus(t.album.albumstatus))
    return _album

@transaction.atomic()
def handle_folder(root, files):
    print('Scanning folder: %s' % root)
    for f in files:
        path = os.path.join(root, f)
        try:
            track = models.Track.objects.get(path=path)
            if int(track.mtime.strftime('%s')) == int(os.stat(path).st_mtime):
                continue
        except models.Track.DoesNotExist:
            track = models.Track()

        t = File(path)
        if t:
            track.discnumber = t.discnumber
            track.tracknumber = t.tracknumber
            track.title = t.title or (f if settings.UNKNOWN_TEXT else None)
            track.album = album(t)
            track.length = t.length
            track.bitrate = t.bitrate
            track.filetype = t.filetype
            track.filesize = t.filesize
            track.mtime = t.mtime
            track.musicbrainz_trackid = t.musicbrainz_trackid
            track.path = path
            track.save()
            track.artists.add(*artists(t, t.artists))


class Command(BaseCommand):
    def handle(self, *args, **options):

        # Do a query to initiate a database connection, and ignore unknown characters in id3 tags
        print('Start scanning with already %s tracks registred' % models.Track.objects.count())
        from django.db import connection
        connection.connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")

        for root, dirs, files in os.walk(settings.MUSIC_DIR):
            handle_folder(root, files)
