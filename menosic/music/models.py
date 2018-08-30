import os
import json
import urllib.parse
import urllib.error
import urllib.request
import datetime
import importlib
import mimetypes
from collections import defaultdict
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from music import fields, helpers
from music.backend import files as files_backend

class Collection(models.Model):
    COLLECTION_BACKENDS = (
        ('T', 'Tags'),
        ('F', 'Files'),  # not yet implemented
        ('R', 'Remote'),  # not yet implemented
    )
    name = models.CharField(max_length=255, db_index=True)
    backend = models.CharField(max_length=1, choices=COLLECTION_BACKENDS)
    location = models.CharField(max_length=255)
    sendfile_location = models.CharField(max_length=255, null=True, blank=True)
    disabled = models.BooleanField(default=False)

    def scan(self, path=None):
        if path and path.startswith(self.location):
            path = path[len(self.location):]
        try:
            backend_module = self.get_backend_display().lower()
            module = 'music.backend.%s.scan' % backend_module
            backend = importlib.import_module(module)
            return backend.Scan(self, path=path)
        except ImportError:
            print("Don't know how to scan :(")


class Genre(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('music:genre_detail', args=[self.pk])

    def artists(self):
        return self.artist_set.exclude(album=None)


class Country(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('music:country_detail', args=[self.pk])


class Artist(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    sortname = models.CharField(max_length=255, db_index=True)
    genres = models.ManyToManyField(Genre)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    path = models.CharField(max_length=255, db_index=True, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    musicbrainz_artistid = fields.UUIDField()

    class Meta:
        ordering = ['sortname']
        unique_together = (
            ('collection', 'path'),
            ('collection', 'name'),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('music:artist_detail', args=[self.pk])

    def related_artists(self):
        return Artist.objects.filter(track__artists=self).exclude(id=self.id).distinct()

    def related_albums(self):
        return Album.objects.filter(track__artists=self).exclude(artist=self).distinct()


class AlbumType(models.Model):
    name = models.CharField(max_length=255, db_index=True)


class AlbumStatus(models.Model):
    name = models.CharField(max_length=255, db_index=True)


class Label(models.Model):
    name = models.CharField(max_length=255, db_index=True)


class Album(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    date = models.CharField(max_length=15, null=True, db_index=True)
    genres = models.ManyToManyField(Genre)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    path = models.CharField(max_length=255, db_index=True, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    labels = models.ManyToManyField(Label)
    albumtypes = models.ManyToManyField(AlbumType)
    albumstatus = models.ManyToManyField(AlbumStatus)

    musicbrainz_albumid = fields.UUIDField()
    musicbrainz_releasegroupid = fields.UUIDField()

    class Meta:
        ordering = ['date']
        unique_together = (
            ('collection', 'path'),
            ('collection', 'musicbrainz_albumid'))

    def __str__(self):
        return self.title

    @property
    def year(self):
        if self.date:
            return self.date[:4]
        else:
            return None

    @property
    def album_types(self):
        return [ at.name for at in self.albumtypes.all() if at.name != 'album' ]

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('music:album_detail', args=[self.pk])

    def cover(self, return_if_not_exists=False):
        if self.path:
            path = self.path
        else:
            try:
                first_track = self.track_set.all()[0]
            except IndexError:
                return None
            path = os.path.dirname(first_track.path)
            if os.path.basename(path).startswith('Disc'):
                path = os.path.dirname(path)

        c = os.path.join(path, 'cover.jpg')
        if os.path.isfile(c) or return_if_not_exists:
            return c

    def get_cover_url(self):
        from django.urls import reverse
        return reverse('music:cover', args=[self.pk])

    def _mbid_cover_download(self, mbid, cover):
        try:
            request = "http://coverartarchive.org/release/{mbid}/".format(mbid=mbid)
            response = urllib.request.urlopen(request)
            obj = json.loads(response.read().decode('utf-8'))
            url = obj['images'][0]['image']
            urllib.request.urlretrieve(url, cover)
            return True
        except (urllib.error.HTTPError, KeyError):
            return False


    def download_cover(self, override=False, search_lastfm=False):
        cover = self.cover(return_if_not_exists=True)

        if (cover and os.path.isfile(cover)) and not override:
            return 

        if not (self.musicbrainz_albumid and self._mbid_cover_download(self.musicbrainz_albumid, cover)) and search_lastfm:
            request = "http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={api_key}&artist={artist}&album={album}&format=json".format(
                    api_key = settings.LASTFM_API_KEY,
                    artist = urllib.parse.quote_plus(self.artist),
                    album = urllib.parse.quote_plus(self.title))

            try:
                response = urllib.request.urlopen(request)
                obj = json.loads(response.read().decode('utf-8'))
            except urllib.error.URLError:
                print("image not found on lastfm: {artist} - {album}".format(artist=self.artist, album=self.title))

            else:
                images = dict([ (item['size'], item['#text']) for item in obj['album']['image'] ])
                image_preference = ['mega', 'extralarge', 'large', 'medium', 'small']

                image_url = None
                for i in image_preference:
                    if i in images.keys():
                        image_url = images[i]
                        break

                if image_url:
                    try:
                        urllib.request.urlretrieve(image_url, cover)
                    except urllib.error.URLError:
                        print("error while downloading cover for {artist} - {album} on url: {url}".format(artist=self.artist, album=self.title, url=image_url))


class Track(models.Model):
    discnumber = models.PositiveIntegerField(null=True)
    tracknumber = models.PositiveIntegerField(null=True)
    title = models.CharField(max_length=255)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='track_display_set')
    artists = models.ManyToManyField(Artist)
    length = models.PositiveIntegerField(null=True)
    bitrate = models.PositiveIntegerField(null=True)
    filetype = models.CharField(max_length=15, null=True)
    filesize = models.PositiveIntegerField(null=True)
    mtime = models.DateTimeField(null=True)
    path = models.CharField(max_length=255, db_index=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    musicbrainz_trackid = fields.UUIDField()

    class Meta:
        ordering = ['discnumber', 'tracknumber']
        unique_together = (
            ('collection', 'path'),)

    def __str__(self):
        return self.title

    @property
    def full_path(self):
        return self.path

    @property
    def relative_path(self):
        if not self.full_path.startswith(self.collection.location):
            raise Exception('Something is wrong.. The file path is outside the collection path.')
        return self.full_path[len(self.collection.location):]

    @property
    def sendfile_location(self):
        return urlquote("%s%s" % (self.collection.sendfile_location, self.relative_path))

    @property
    def duration(self):
        return helpers.duration(self.length)

    @property
    def mimetype(self):
        mimetype, encoding = mimetypes.guess_type(self.path)
        return mimetype

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('music:track_detail', args=[self.pk])

    def get_mp3_url(self):
        from django.urls import reverse
        return reverse('music:track', args=['mp3', self.pk])

    def get_ogg_url(self):
        from django.urls import reverse
        return reverse('music:track', args=['ogg', self.pk])

    def get_original_url(self):
        from django.urls import reverse
        return reverse('music:track', args=['original', self.pk])


# Playlist stuff
class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def tracks(self):
        return self.playlisttrack_set.prefetch_related('tags_track__artist', 'tags_track__album').all()

    def empty(self):
        self.playlisttrack_set.all().delete()

    def add_file_tracks(self, tracks):
        last = PlaylistTrack.objects.last()
        last_sort = last.sort_order if last else 0

        try:
            tracks = iter(tracks)
        except TypeError:
            tracks = [tracks]

        PlaylistTrack.objects.bulk_create(
            [PlaylistTrack(
                playlist_id=self.id,
                file_path=track.path,
                sort_order=last_sort+counter,
                collection_id=track.collection.id)
                for counter, track in enumerate(tracks, start=1)]
        )

    def add_tag_tracks(self, tracks):
        last = PlaylistTrack.objects.last()
        last_sort = last.sort_order if last else 0

        try:
            tracks = iter(tracks)
        except TypeError:
            tracks = [tracks]

        PlaylistTrack.objects.bulk_create(
            [PlaylistTrack(
                playlist_id=self.id,
                tags_track_id=track.id,
                sort_order=last_sort+counter,
                collection_id=track.collection.id)
                for counter, track in enumerate(tracks, start=1)]
        )


class BaseTrack(models.Model):
    tags_track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True)
    file_path = models.CharField(max_length=255, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @property
    def track(self):
        if self.tags_track:
            return self.tags_track
        elif self.file_path:
            return files_backend.FileItem(self.collection, self.file_path)

    @property
    def identifier(self):
        if self.tags_track:
            return "%s_%s" % (self.id, self.tags_track_id)
        elif self.file_path:
            return self.track.encoded_path

    def set_track(self, track):
        if type(track) == Track:
            self.tags_track = track
            self.file_path = None
        else:
            self.tags_track = None
            self.file_path = track.path

        self.collection = track.collection


class PlaylistTrack(BaseTrack):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    sort_order = models.IntegerField()

    class Meta:
        ordering = ['sort_order']

    def safe(self, *args, **kwargs):
        if not self.sort_order:
            last = PlaylistTrack.objects.last()
            self.sort_order = last.sort_order + 1 if last else 1
        super(PlaylistTrack, self).save(*args, **kwargs)


class LastPlayed(BaseTrack):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time']

    @property
    def minutes_ago(self):
        delta = timezone.now() - self.time
        return int(delta.seconds / 60)


class Player(models.Model):
    PLAYER_TYPES = (
        ('B', 'Browser'),
        ('E', 'External'),  # not yet implemented
        ('C', 'Client'))  # not yet implemented
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=PLAYER_TYPES)
    playlist = models.OneToOneField(Playlist, on_delete=models.CASCADE)
