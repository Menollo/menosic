from music import fields
from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=255, db_index=True)

class Country(models.Model):
    name = models.CharField(max_length=255, db_index=True)

class Artist(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    sortname = models.CharField(max_length=255, db_index=True)
    genres = models.ManyToManyField(Genre, null=True)
    country = models.ForeignKey(Country, null=True)
    path = models.CharField(max_length=255, unique=True, db_index=True, null=True)

    musicbrainz_artistid = fields.UUIDField()

class AlbumType(models.Model):
    name = models.CharField(max_length=255, db_index=True)

class AlbumStatus(models.Model):
    name = models.CharField(max_length=255, db_index=True)

class Label(models.Model):
    name = models.CharField(max_length=255, db_index=True)

class Album(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    artists = models.ManyToManyField(Artist, null=True)
    date = models.CharField(max_length=15, null=True)
    genres = models.ManyToManyField(Genre, null=True)
    country = models.ForeignKey(Country, null=True)
    discnumber = models.PositiveIntegerField(null=True) 
    path = models.CharField(max_length=255, db_index=True, null=True)

    labels = models.ManyToManyField(Label, null=True)
    albumtypes = models.ManyToManyField(AlbumType, null=True)
    albumstatus = models.ManyToManyField(AlbumStatus, null=True)

    musicbrainz_albumid = fields.UUIDField(unique=True)
    musicbrainz_releasegroupid = fields.UUIDField()


class Track(models.Model):
    tracknumber = models.PositiveIntegerField(null=True)
    title = models.CharField(max_length=255)
    album = models.ForeignKey(Album, null=True)
    artists = models.ManyToManyField(Artist, null=True)
    performer = models.CharField(max_length=255, null=True)
    genre = models.ManyToManyField(Genre, null=True)
    length = models.PositiveIntegerField(null=True)
    path = models.CharField(max_length=255, unique=True, db_index=True)

    musicbrainz_trackid = fields.UUIDField()
