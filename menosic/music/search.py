import re

from django.db.models import Q
from music import models


def search_terms(string):
    fixspaces = re.compile(r'\s{2,}').sub
    split_terms = re.compile(r'"([^"]+)"|(\S+)').findall

    return [fixspaces(' ', (t[0] or t[1]).strip()) for t in split_terms(string)]


def search_query(terms, fields):
    query = Q()
    for term in terms:
        query_fields = Q()
        for field in fields:
            q = Q(**{"%s__icontains" % field: term})
            query_fields = query_fields | q
        query = query & query_fields

    return query


def search_artists(string):
    terms = search_terms(string)
    fields = ['name', 'sortname']

    artists = models.Artist.objects.exclude(album=None).filter(collection__disabled=False)
    return artists.filter(search_query(terms, fields))


def search_albums(string):
    terms = search_terms(string)
    fields = ['title']

    albums = models.Album.objects.filter(collection__disabled=False)
    return albums.filter(search_query(terms, fields))


def search_tracks(string):
    terms = search_terms(string)
    fields = ['title']

    tracks = models.Track.objects.filter(collection__disabled=False)
    return tracks.filter(search_query(terms, fields))
