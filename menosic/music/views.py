import datetime
import json
import os
import subprocess
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.http import urlsafe_base64_decode
from django.views.generic import DetailView, View, TemplateView, ListView
from django.views.generic.detail import SingleObjectMixin, BaseDetailView
from music import helpers, models
from music.backend import files as files_backend


# browse views
class ArtistDetailView(DetailView):
    model = models.Artist


class AlbumDetailView(DetailView):
    model = models.Album


class TrackDetailView(DetailView):
    model = models.Track


class BrowseView(TemplateView):
    template_name = 'music/browse.html'

    def get_context_data(self, collection, path, **kwargs):
        path = urlsafe_base64_decode(path).decode('utf-8')

        collection = models.Collection.objects.get(pk=collection)
        dirs, files = files_backend.items_for_path(collection, path)

        crumbs = []
        for p in path.split('/'):
            parents = [c.name for c in crumbs]
            parents.append(p)
            p = os.path.join(*parents)
            crumbs.append(files_backend.DirItem(collection, p))

        return {
            'title': os.path.basename(path),
            'dirs': dirs,
            'files': files,
            'crumbs': crumbs}


# playlist view
class PlayerMixin(object):
    template_name = 'music/playlist.html'

    def get_context_data(self, **kwargs):
        player = helpers.player_for_user(self.request.user)
        playlist = self.update_playlist(player.playlist)
        context_data = {
            'playlist': playlist,
            'current': self.get_current(playlist)}
        context_data.update(kwargs)
        return context_data

    def update_playlist(self, playlist):
        return playlist

    def get_current(self, playlist):
        return None


class PlayAlbumFiles(PlayerMixin, TemplateView):
    def update_playlist(self, playlist):
        collection = models.Collection.objects.get(pk=self.kwargs['collection'])
        path = urlsafe_base64_decode(self.kwargs['path']).decode('utf-8')

        tracks = files_backend.items_for_path(collection, os.path.dirname(path))[1]

        playlist.empty()
        playlist.add_file_tracks(tracks)
        playlist.save()

        return playlist

    def get_current(self, playlist):
        return self.kwargs['path']


class PlayAlbumTrack(PlayerMixin, DetailView):
    model = models.Track

    def update_playlist(self, playlist):
        playlist.empty()
        playlist.add_tag_tracks(self.object.album.track_set.all())
        playlist.save()

        return playlist

    def get_current(self, playlist):
        return playlist.tracks.get(tags_track=self.object).identifier


class AddAlbumToPlaylist(PlayerMixin, DetailView):
    model = models.Album

    def update_playlist(self, playlist):
        playlist.add_tag_tracks(self.object.track_set.all())
        return playlist


class AddTrackToPlaylist(PlayerMixin, DetailView):
    model = models.Track

    def update_playlist(self, playlist):
        playlist.add_tag_tracks(self.object)
        return playlist


class PlaylistTrack(PlayerMixin, DetailView):
    model = models.PlaylistTrack

    def update_playlist(self, playlist):
        action = self.kwargs['action']
        track = self.get_object()

        if action == 'remove':
            playlist.tracks.get(pk=track.pk).delete()
        elif action == 'up':
            prev = playlist.tracks.filter(sort_order__lt=track.sort_order).order_by('-sort_order')[0]
            helpers.swap_playlist_tracks(track, prev)
        elif action == 'down':
            next = playlist.tracks.filter(sort_order__gt=track.sort_order)[0]
            helpers.swap_playlist_tracks(track, next)

        return models.Playlist.objects.get(pk=playlist.pk)


class JSONResponseMixin(object):
    def render_to_response(self, context):
        return HttpResponse(
            json.dumps(context),
            content_type='application/json')


class PlayerJSON(JSONResponseMixin, BaseDetailView):
    model = models.Player

    def get_context_data(self, **kwargs):
        playlist = self.get_object().playlist
        tracks = [{
            'id': pt.identifier,
            'sort': pt.sort_order,
            'mp3': pt.track.get_mp3_url(),
            'ogg': pt.track.get_ogg_url(),
            'length': pt.track.length,
            'title': str(pt.track.title),
            'album': str(pt.track.album.title),
            'artist': str(pt.track.artist)
            } for pt in playlist.tracks]
        context_data = {
            'playlist': tracks,
        }
        return context_data


# Serve the track files
class ServeFileMixin(object):

    output = 'mp3'

    def get_content_type(self):
        if self.output == 'mp3':
            return 'audio/mpeg'
        elif self.output == 'ogg':
            return 'audio/ogg'

    def serve_directly(self):
        response = HttpResponse(content_type=self.get_content_type())
        response['Content-Length'] = os.path.getsize(self.track.full_path)
        if settings.DEBUG:
            response.write(open(self.track.full_path, 'rb').read())
        else:
            response['X-Accel-Redirect'] = self.track.full_path
        return response

    def convert(self):
        # input
        if self.track.filetype == 'flac':
            cmd = ["flac", "--silent", "--decode", "--stdout", self.track.full_path]
        elif self.track.filetype == 'mp3':
            cmd = ["lame", "--silent", "--decode", self.track.full_path, "-"]
        else:
            cmd = ["ffmpeg", "-i", self.track.full_path, "-v", "0", "-f", "wav", "-"]

        stream_in = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        # output
        if self.output == 'mp3':
            cmd = ["lame", "--silent", "-h", "-b", "192", "-"]
        elif self.output == 'ogg':
            cmd = ["oggenc", "--quiet", "-q", "3", "-"]

        stream_out = subprocess.Popen(
            cmd,
            stdin=stream_in.stdout,
            stdout=subprocess.PIPE)

        def yield_and_cleanup(p_out, p_in):
            try:
                for line in p_out.stdout:
                    yield line
            finally:
                p_out.communicate()
                p_in.communicate()

        return StreamingHttpResponse(
            yield_and_cleanup(stream_out, stream_in),
            content_type=self.get_content_type())

    def get(self, request, *args, **kwargs):
        self.track = self.get_object()

        helpers.register_playback(self.track, request.user)

        if 'output' in kwargs:
            self.output = kwargs['output']

        if self.output == self.track.filetype:
            return self.serve_directly()
        else:
            return self.convert()


class FileView(ServeFileMixin, View):
    def get_object(self):
        collection = models.Collection.objects.get(pk=self.kwargs['collection'])
        path = urlsafe_base64_decode(self.kwargs['path']).decode('utf-8')
        return files_backend.FileItem(collection, path)


class TrackView(SingleObjectMixin, ServeFileMixin, View):
    model = models.Track


class LastPlayedView(ListView):
    template_name = 'music/last_played.html'

    def get_queryset(self):
        some_time_ago = datetime.datetime.now()-datetime.timedelta(minutes=15)
        return models.LastPlayed.objects.filter(time__gt=some_time_ago)
