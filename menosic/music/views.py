from django.shortcuts import render
from django.views.generic import ListView, DetailView

from music import models

class ArtistListView(ListView):
    queryset = models.Artist.objects.exclude(album=None)

class ArtistDetailView(DetailView):
    model = models.Artist

class AlbumDetailView(DetailView):
    model = models.Album
