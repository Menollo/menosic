import mimetypes

from django.views.generic import ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse
#from django.core.servers.basehttp import FileWrapper
from django.conf import settings

from music import models

class ArtistListView(ListView):
    queryset = models.Artist.objects.exclude(album=None)

class ArtistDetailView(DetailView):
    model = models.Artist

class AlbumDetailView(DetailView):
    model = models.Album

class TrackDetailView(DetailView):
    model = models.Track

class TrackView(SingleObjectMixin, View):
    model = models.Track

    def get(self, request, *args, **kwargs):
        track = self.get_object()

        response = HttpResponse(content_type=track.mimetype)

        if settings.DEBUG:
            response.write(open(track.path, 'rb').read()) # FileWrapper?
        else:
            response['X-Accel-Redirect'] = track.path

        return response
    
