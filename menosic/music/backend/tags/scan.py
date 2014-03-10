import os
import sys

from django.conf import settings
from django.db import transaction

from music.backend.tags.reader import File
from music import models

class Scan(object):
    unknown = lambda self, x: x or settings.UNKNOWN_TEXT

    def __init__(self, collection):
        self.collection = collection

        # Do a query to initiate a database connection, and ignore unknown characters in id3 tags
        print('Start scanning with already %s tracks registred' % models.Track.objects.count())
        if sys.version_info < (3, 0): 
            from django.db import connection
            connection.connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")

        for root, dirs, files in os.walk(collection.location):
            self.handle_folder(root, files)


    def artists(self, t, _artists):
        for artist in _artists:
            try:
                a = models.Artist.objects.get(name=self.unknown(artist.name), collection=self.collection)
            except models.Artist.DoesNotExist:
                try:
                    if artist.musicbrainz_artistid:
                        a = models.Artist.objects.get(musicbrainz_artistid=artist.musicbrainz_artistid, collection=self.collection)
                    else:
                        raise models.Artist.DoesNotExist('No musicbrainz artistid')
                except models.Artist.DoesNotExist:
                    a = models.Artist(
                            name = self.unknown(artist.name),
                            sortname = artist.sortname or self.unknown(artist.name),
                            musicbrainz_artistid = artist.musicbrainz_artistid,
                            collection = self.collection,
                        )
                    a.save()

            a.genres.add(*self.genres(t.genres))
            yield a

    def albumtypes(self, names):
        return [models.AlbumType.objects.get_or_create(name=name)[0] for name in names or []]

    def albumstatus(self, names):
        return [models.AlbumStatus.objects.get_or_create(name=name)[0] for name in names or []]

    def labels(self, names):
        return [models.Label.objects.get_or_create(name=name)[0] for name in names or []]

    def genres(self, names):
        return [models.Genre.objects.get_or_create(name=name)[0] for name in names or []]

    def country(self, name):
        if name:
            return models.Country.objects.get_or_create(name=name)[0]

    def album(self, t):
        try:
            _album = models.Album.objects.get(title=t.album.title, artists__name__in = [self.unknown(a.name) for a in t.album.albumartists], collection=self.collection)
        except models.Album.DoesNotExist:
            try:
                if t.album.musicbrainz_albumid:
                    _album = models.Album.objects.get(musicbrainz_albumid=t.album.musicbrainz_albumid, collection=self.collection)
                else:
                    raise models.Album.DoesNotExist('No musicbrainz albumid')
            except models.Album.DoesNotExist:
                _album = models.Album(
                        title = self.unknown(t.album.title),
                        date = t.album.date,
                        country = self.country(t.album.country),
                        musicbrainz_albumid = t.album.musicbrainz_albumid,
                        musicbrainz_releasegroupid = t.album.musicbrainz_releasegroupid,
                        collection = self.collection,
                    )
                _album.save()

        _album.artists.add(*self.artists(t, t.album.albumartists))
        _album.genres.add(*self.genres(t.genres))
        _album.labels.add(*self.labels(t.album.labels))
        _album.albumtypes.add(*self.albumtypes(t.album.albumtypes))
        _album.albumstatus.add(*self.albumstatus(t.album.albumstatus))
        return _album

    @transaction.atomic()
    def handle_folder(self, root, files):
        print('Scanning folder: %s' % root)
        for f in files:
            path = os.path.join(root, f)
            try:
                track = models.Track.objects.get(path=path, collection=self.collection)
                if int(track.mtime.strftime('%s')) == int(os.stat(path).st_mtime):
                    continue
            except models.Track.DoesNotExist:
                track = models.Track(collection=self.collection)

            t = File(path)
            if t:
                track.discnumber = t.discnumber
                track.tracknumber = t.tracknumber
                track.title = t.title or (f if settings.UNKNOWN_TEXT else None)
                track.album = self.album(t)
                track.length = t.length
                track.bitrate = t.bitrate
                track.filetype = t.filetype
                track.filesize = t.filesize
                track.mtime = t.mtime
                track.musicbrainz_trackid = t.musicbrainz_trackid
                track.path = path
                track.save()
                track.artists.add(*self.artists(t, t.artists))
