import datetime
import importlib
import mimetypes
from django.contrib.auth.models import User
from django.db import models
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

    def scan(self):
        try:
            backend_module = self.get_backend_display().lower()
            module = 'music.backend.%s.scan' % backend_module
            backend = importlib.import_module(module)
            return backend.Scan(self)
        except ImportError:
            print("Don't know how to scan :(")


class Genre(models.Model):
    name = models.CharField(max_length=255, db_index=True)


class Country(models.Model):
    name = models.CharField(max_length=255, db_index=True)


class Artist(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    sortname = models.CharField(max_length=255, db_index=True)
    genres = models.ManyToManyField(Genre, null=True)
    country = models.ForeignKey(Country, null=True)
    path = models.CharField(max_length=255, db_index=True, null=True)
    collection = models.ForeignKey(Collection)

    musicbrainz_artistid = fields.UUIDField()

    class Meta:
        ordering = ['sortname']
        unique_together = (
            ('collection', 'path'),
            ('collection', 'name'),
        )

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('artist_detail', args=[self.pk])


class AlbumType(models.Model):
    name = models.CharField(max_length=255, db_index=True)


class AlbumStatus(models.Model):
    name = models.CharField(max_length=255, db_index=True)


class Label(models.Model):
    name = models.CharField(max_length=255, db_index=True)


class Album(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    artists = models.ManyToManyField(Artist, null=True)
    date = models.CharField(max_length=15, null=True, db_index=True)
    genres = models.ManyToManyField(Genre, null=True)
    country = models.ForeignKey(Country, null=True)
    path = models.CharField(max_length=255, db_index=True, null=True)
    collection = models.ForeignKey(Collection)

    labels = models.ManyToManyField(Label, null=True)
    albumtypes = models.ManyToManyField(AlbumType, null=True)
    albumstatus = models.ManyToManyField(AlbumStatus, null=True)

    musicbrainz_albumid = fields.UUIDField()
    musicbrainz_releasegroupid = fields.UUIDField()

    class Meta:
        ordering = ['date']
        unique_together = (
            ('collection', 'path'),
            ('collection', 'musicbrainz_albumid'))

    @property
    def year(self):
        if self.date:
            return self.date[:4]
        else:
            return '0000'

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('album_detail', args=[self.pk])


class Track(models.Model):
    discnumber = models.PositiveIntegerField(null=True)
    tracknumber = models.PositiveIntegerField(null=True)
    title = models.CharField(max_length=255)
    album = models.ForeignKey(Album, null=True)
    artists = models.ManyToManyField(Artist, null=True)
    length = models.PositiveIntegerField(null=True)
    bitrate = models.PositiveIntegerField(null=True)
    filetype = models.CharField(max_length=15, null=True)
    filesize = models.PositiveIntegerField(null=True)
    mtime = models.DateTimeField(null=True)
    path = models.CharField(max_length=255, db_index=True)
    collection = models.ForeignKey(Collection)

    musicbrainz_trackid = fields.UUIDField()

    class Meta:
        ordering = ['discnumber', 'tracknumber']
        unique_together = (
            ('collection', 'path'),)

    @property
    def full_path(self):
        return self.path

    @property
    def artist(self):
        return ", ".join([a.name for a in self.artists.all()])

    @property
    def duration(self):
        return helpers.duration(self.length)

    @property
    def mimetype(self):
        mimetype, encoding = mimetypes.guess_type(self.path)
        return mimetype

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('track_detail', args=[self.pk])

    def get_mp3_url(self):
        from django.core.urlresolvers import reverse
        return reverse('track', args=['mp3', self.pk])

    def get_ogg_url(self):
        from django.core.urlresolvers import reverse
        return reverse('track', args=['ogg', self.pk])


# Playlist stuff
class Playlist(models.Model):
    user = models.ForeignKey(User)

    @property
    def tracks(self):
        return self.playlisttrack_set.all()

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
    tags_track = models.ForeignKey(Track, null=True)
    file_path = models.CharField(max_length=255, null=True)
    collection = models.ForeignKey(Collection)

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
    playlist = models.ForeignKey(Playlist)
    sort_order = models.IntegerField()

    class Meta:
        ordering = ['sort_order']

    def safe(self, *args, **kwargs):
        if not self.sort_order:
            last = PlaylistTrack.objects.last()
            self.sort_order = last.sort_order + 1 if last else 1
        super(PlaylistTrack, self).save(*args, **kwargs)


class LastPlayed(BaseTrack):
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time']

    @property
    def minutes_ago(self):
        delta = datetime.datetime.now() - self.time
        return int(delta.seconds / 60)


class Player(models.Model):
    PLAYER_TYPES = (
        ('B', 'Browser'),
        ('E', 'External'),  # not yet implemented
        ('C', 'Client'))  # not yet implemented
    user = models.ForeignKey(User)
    type = models.CharField(max_length=1, choices=PLAYER_TYPES)
    playlist = models.OneToOneField(Playlist)
