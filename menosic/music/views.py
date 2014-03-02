import mimetypes

from django.views.generic import ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin, BaseDetailView
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


class PlayerMixin(object):
    def get_player(self):
        try:
            player = models.Player.objects.get(user=self.request.user, type='B')
        except models.Player.DoesNotExist:
            player = models.Player(
                    user=self.request.user,
                    type='B'
                )
            playlist = models.Playlist(user=self.request.user)
            playlist.save()

            player.playlist = playlist
            player.save()

        self.player = player
        return player

    def get_context_data(self, **kwargs):
        context_data = {
            'playlist': self.update_playlist(self.get_player().playlist),
            'current': self.get_current_track(),
        }
        context_data.update(kwargs)
        return context_data

    def update_playlist(self, playlist):
        return playlist

    def get_current_track(self):
        return None


class PlayAlbumTrack(PlayerMixin, DetailView):
    model = models.Track
    template_name = 'music/playlist.html'

    def update_playlist(self, playlist):
        playlist.tracks.clear()
        playlist.add_tracks(self.object.album.track_set.all())
        playlist.save()

        return playlist

    def get_current_track(self):
        return self.object


class TrackView(SingleObjectMixin, View):
    model = models.Track
    output = 'mp3'

    def get_content_type(self):
        if self.output == 'mp3':
            return 'audio/mpeg'
        elif self.output == 'ogg':
            return 'audio/ogg'

    def serve_directly(self):
        response = HttpResponse(content_type=self.get_content_type())
        response['Content-Length'] = os.path.getsize(self.track.path)
        if settings.DEBUG:
            response.write(open(self.track.path, 'rb').read()) # FileWrapper?
        else:
            response['X-Accel-Redirect'] = self.track.path
        return response

    def convert(self):
        # input
        if self.track.filetype == 'flac':
            cmd = ["flac", "--silent", "--decode", "--stdout", self.track.path]
        elif self.track.filetype == 'mp3':
            cmd = ["lame", "--silent", "--decode", self.track.path, "-"]
        else:
            cmd = ["ffmpeg", "-i", self.track.path, "-v", "0", "-f", "wav", "-"]
        stream_in = subprocess.Popen(cmd,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        # output
        if self.output == 'mp3':
            cmd = ["lame", "--silent", "-h", "-b", "192", "-"]
        elif self.output == 'ogg':
            cmd = ["oggenc", "--quiet", "-q", "3", "-"]
        stream_out = subprocess.Popen(cmd,
            stdin=stream_in.stdout, stdout=subprocess.PIPE)
        return StreamingHttpResponse(stream_out.stdout, content_type=self.get_content_type())

    def get(self, request, *args, **kwargs):
        self.track = self.get_object()
        if 'output' in kwargs:
            self.output = kwargs['output']

        if self.output == self.track.filetype:
            return self.serve_directly()
        else:
            return self.convert()

