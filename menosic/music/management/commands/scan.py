import os
import sys
import mutagenx
from django.conf import settings
from django.core.management.base import BaseCommand

from music import models

def tag(m, tag):
    if m.get(tag):
        if len(m.get(tag)) == 1:
            return m.get(tag)[0]
        else: 
            print("artist: %s, album: %s, tag: %s, value: %s" % (m.get('artist'), m.get('album'), tag, m.get(tag)))
            return m.get(tag)[0]

def number(string):
    return int(string.split('/')[0])

def length(m):
    return m.info.length or tag(m, 'length') or None

def index_or_first(l, i):
    if not l:
        return None
    elif len(l) > i:
        return l[i]
    else:
        return l[0]

def _artists(m, names, sortnames=None, musicbrainz_artistids=None, paths=None):
    for index, name in enumerate(names):
        sortname = index_or_first(sortnames, index)
        musicbrainz_artistid = index_or_first(musicbrainz_artistids, index)
        path = index_or_first(paths, index)

        try:
            artist =  models.Artist.objects.get(name=name)
        except models.Artist.DoesNotExist:
            artist = models.Artist(
                    name = name,
                    sortname = sortname,
                    musicbrainz_artistid = musicbrainz_artistid,
                    path = path
                )
            artist.save()

        artist.genres.add(*list(genres(m)))
        yield artist

def artists(m):
    return _artists(m,
            m.get('artist'),
            m.get('artistsort'), 
            m.get('musicbrainz_artistid'),
            None)

def albumartists(m):
    return _artists(m,
            m.get('albumartist') or m.get('artist'),
            m.get('albumartistsort') or m.get('artistsort'),
            m.get('musicbrainz_albumartistid') or m.get('musicbrainz_artistid'),
            None)

def albumtypes(m):
    for name in m.get('musicbrainz_albumtype') or []:
        yield models.AlbumType.objects.get_or_create(name=name)[0]

def albumstatus(m):
    for name in m.get('musicbrainz_albumstatus') or []:
        yield models.AlbumStatus.objects.get_or_create(name=name)[0]

def labels(m):
    for name in m.get('label') or []:
        yield models.Label.objects.get_or_create(name=name)[0]

def genres(m):
    for name in m.get('genre') or []:
        yield models.Genre.objects.get_or_create(name=name)[0]

def country(name):
    if name:
        return models.Country.objects.get_or_create(name=name)[0]

def album(m):
    try:
        _album = models.Album.objects.get(name=tag(m, 'album'))
    except models.Album.DoesNotExist:
        _album = models.Album(
                name = tag(m, 'album'),
                date = tag(m, 'date'),
                discnumber = number(tag(m, 'discnumber')),
                #albumtype = tag(m, 'albumtype'),
                country = country(tag(m, 'country')),

                musicbrainz_albumid = m.get('musicbrainz_albumid'),
                musicbrainz_releasegroupid = m.get('musicbrainz_releasegroupid')
            )
        _album.save()

    _album.artists.add(*list(albumartists(m)))
    _album.genres.add(*list(genres(m)))
    _album.labels.add(*list(labels(m)))
    _album.albumtypes.add(*list(albumtypes(m)))
    _album.albumstatus.add(*list(albumstatus(m)))
    return _album


class Command(BaseCommand):
    def handle(self, *args, **options):
        for root, dirs, files in os.walk(settings.MUSIC_DIR):
            for f in files:
                m = mutagenx.File(os.path.join(root,f), easy=True)
                if m:
                    path = os.path.join(root, f)
                    try:
                        track = models.Track.objects.get(path=path)
                        print('Track allready exists')
                    except models.Track.DoesNotExist:
                        track = models.Track(
                            tracknumber = number(tag(m, 'tracknumber')),
                            title = tag(m, 'title'),
                            album = album(m),
                            #performer = tag(m, 'performer'), # todo, make model
                            #genre
                            length = length(m),
                            path = path,
                            musicbrainz_trackid = tag(m, 'musicbrainz_trackid')

                        )
                        track.save()
                        track.artists.add(*artists(m))
