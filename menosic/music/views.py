import mimetypes

from django.views.generic import ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse, StreamingHttpResponse
#from django.core.servers.basehttp import FileWrapper
from django.conf import settings
import subprocess
import os

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

        if track.mimetype == 'audio/mpeg':
            response = HttpResponse(content_type='audio/mpeg')
            if settings.DEBUG:
                response.write(open(track.path, 'rb').read()) # FileWrapper?
            else:
                response['X-Accel-Redirect'] = track.path

        else:
            if track.mimetype == 'audio/x-flac':
                flac = subprocess.Popen(
                    ["flac", "--silent", "--decode", "--stdout", track.path],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                mp3 = subprocess.Popen(
                    ["lame", "--silent", "-h", "-b", "192", "-"],
                    stdin=flac.stdout, stdout=subprocess.PIPE)
                response = StreamingHttpResponse(mp3.stdout, content_type='audio/mpeg')
            else:
                pipe = subprocess.Popen(
                        ["ffmpeg", "-i", track.path, "-ab", "192k", "-v", "0", "-f", "mp3", "-"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE
                    )
                response = StreamingHttpResponse(pipe.stdout, content_type='audio/mpeg')
        return response
    
