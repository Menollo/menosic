import datetime
import mimetypes
import importlib
from django.db import models
from music import fields
from django.contrib.auth.models import User

class Collection(models.Model):
    COLLECTION_BACKENDS = (
            ('T', 'Tags'),
            ('F', 'Files'), # not yet implemented
            ('R', 'Remote'), # not yet implemented
        )
    name = models.CharField(max_length=255, db_index=True)
    backend = models.CharField(max_length=1, choices=COLLECTION_BACKENDS)
    location = models.CharField(max_length=255)

    def scan(self):
        try:
            import bpdb; bpdb.set_trace()
            backend = importlib.import_module('music.backend.%s.scan' % self.get_backend_display().lower())
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
                ('collection', 'musicbrainz_albumid'),
            )

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
    #genre = models.ManyToManyField(Genre, null=True)
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
                ('collection', 'path'),
            )

    @property
    def artist(self):
        return ", ".join([a.name for a in self.artists.all()])

    @property
    def duration(self):
        duration = str(datetime.timedelta(seconds=self.length))
        return duration[2:] if duration[0:2] == '0:' else duration

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

##################
# Playlist stuff #
##################
class Playlist(models.Model):
    user = models.ForeignKey(User)

    @property
    def tracks(self):
        return self.playlisttrack_set.all()

    def empty(self):
        self.playlisttrack_set.all().delete()

    def add_tracks(self, qs):
        last = PlaylistTrack.objects.last()
        last_sort = last.sort_order if last else 0

        PlaylistTrack.objects.bulk_create(
                [PlaylistTrack(playlist_id = self.id, track_id=track.id, sort_order=last_sort+counter) for counter, track in enumerate(qs, start=1)]
            )


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist)
    track = models.ForeignKey(Track)
    sort_order = models.IntegerField()

    class Meta:
        ordering = ['sort_order']

    @property
    def identifier(self):
        return "%s_%s" % (self.id, self.track_id)

    def safe(self, *args, **kwargs):
        if not self.sort_order:
            last = PlaylistTrack.objects.last()
            self.sort_order = last.sort_order + 1 if last else 1
        super(PlaylistTrack, self).savew(*args, **kwargs)


class Player(models.Model):
    PLAYER_TYPES = (
            ('B', 'Browser'),
            ('E', 'External'), # not yet implemented
            ('C', 'Client'), # not yet implemented
        )
    user = models.ForeignKey(User)
    type = models.CharField(max_length=1, choices=PLAYER_TYPES)
    playlist = models.OneToOneField(Playlist)
