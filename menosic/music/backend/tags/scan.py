import os
import sys
from django.conf import settings
from django.db import transaction
from music import models
from music.backend.tags.reader import File


class Scan(object):
    unknown = lambda self, x: x or settings.UNKNOWN_TEXT

    def __init__(self, collection, path=None):
        self.collection = collection

        # Do a query to initiate a database connection, and ignore unknown characters in id3 tags
        print('Start scanning with already %s tracks registred' % models.Track.objects.count())
        if sys.version_info < (3, 0):
            from django.db import connection
            connection.connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")

        location = collection.location
        if path:
            path = path[1:] if path[0] == os.sep else path
            location = os.path.join(location, path)

        for root, dirs, files in os.walk(location):
            self.handle_folder(root, files)

    def get_artist_by_artistid(self, artistid, name):
        return models.Artist.objects.get(
            musicbrainz_artistid=artistid,
            name=name,
            collection=self.collection)

    def get_artist_by_name(self, name):
        return models.Artist.objects.get(
            musicbrainz_artistid__isnull=True,
            name=name,
            collection=self.collection)

    def artist(self, t, artist):
        mb_artistid  = artist.musicbrainz_artistid
        if mb_artistid and len(mb_artistid) == 1:
            mb_artistid = mb_artistid[0]
        else:
            mb_artistid = None

        try:
            if mb_artistid:
                try:
                    a = self.get_artist_by_artistid(mb_artistid, artist.name)
                except models.Artist.DoesNotExist:
                    a = self.get_artist_by_name(artist.name)
            else:
                a = self.get_artist_by_name(artist.name)

        except models.Artist.DoesNotExist:
            # create a new artist..
            a = models.Artist(collection=self.collection)

        a.name = self.unknown(artist.name)
        a.sortname = artist.sortname or self.unknown(artist.name)
        a.musicbrainz_artistid = mb_artistid
        a.save()

        if mb_artistid:
            a.artists.add(*list(
                    models.Artist.objects.filter(
                        musicbrainz_artistid=mb_artistid
                    ).exclude(id=a.id)))

        a.genres.add(*self.genres(t.genres))
        return a

    def artists(self, t, _artists):
        for artist in _artists:
            a = self.artist(t, artist)
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
        albumartist = self.artist(t, t.album.artist)

        if len(t.album.artist.musicbrainz_artistid) > 1:
            albumartist.artists.add(*list(
                    models.Artist.objects.filter(
                        musicbrainz_artistid__in=t.album.artist.musicbrainz_artistid
                    )))

        try:
            _album = models.Album.objects.get(
                title=t.album.title,
                artist=albumartist,
                date=t.album.date,
                collection=self.collection)
        except models.Album.DoesNotExist:
            try:
                if t.album.musicbrainz_albumid:
                    _album = models.Album.objects.get(
                        musicbrainz_albumid=t.album.musicbrainz_albumid,
                        collection=self.collection)
                else:
                    raise models.Album.DoesNotExist('No musicbrainz albumid')
            except models.Album.DoesNotExist:
                _album = models.Album(collection=self.collection)
                if settings.DOWNLOAD_COVER_ON_SCAN:
                    _album.download_cover(override=False, search_lastfm=True)

        _album.title = self.unknown(t.album.title)
        _album.artist = albumartist
        _album.date = t.album.date
        _album.country = self.country(t.album.country)
        _album.musicbrainz_albumid = t.album.musicbrainz_albumid
        _album.musicbrainz_releasegroupid = t.album.musicbrainz_releasegroupid
        _album.save()

        #_album.artists.add(*self.artists(t, t.album.albumartists))
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
                track.artist = self.artist(t, t.artist)
                track.length = t.length
                track.bitrate = t.bitrate
                track.filetype = t.filetype
                track.filesize = t.filesize
                track.mtime = t.mtime
                track.musicbrainz_trackid = t.musicbrainz_trackid
                track.path = path
                track.save()
                track.artists.clear()
                track.artists.add(*list(self.artists(t, t.artists)))
