import datetime
import json
import os
import subprocess

from PIL import Image

from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse, Http404
from django.utils.http import urlsafe_base64_decode, urlquote
from django.views.generic import (
    DetailView, View, TemplateView, ListView, RedirectView
)
from django.views.generic.detail import SingleObjectMixin, BaseDetailView
from music import helpers, models, search
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
            response['X-Accel-Redirect'] = self.track.sendfile_location
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


class CoverFileView(BaseDetailView):
    model = models.Album

    def sendfile_location(self, path):
        relative_path = path[len(self.object.collection.location):]
        return urlquote("%s%s" % (self.object.collection.sendfile_location, relative_path))

    def render_to_response(self, request):
        cover_path = self.object.cover()
                            # Sanity check for cover_path
        if not cover_path or \
           (cover_path and not os.path.exists(cover_path)):
            raise Http404

        save = False
        if not settings.DEBUG:
            save = True
            thumbnail_path = os.path.join(os.path.dirname(cover_path), "thumbnail.jpg")

        try:
            if save and os.path.exists(thumbnail_path):
                im = Image.open(thumbnail_path)
            else:
                im = Image.open(cover_path)
                                    # Thumbnail keeps aspect ratio
                im.thumbnail((200, 200), Image.ANTIALIAS)

                if save:
                    im.save(thumbnail_path, 'JPEG', quality=90)

        except None:        # TODO: Figure out which exceptions can be thrown?
            raise Http404

        response = HttpResponse(content_type='image/jpeg')
        if settings.DEBUG:
            im.save(response, 'JPEG', quality=90);
        else:
            response['Content-Length'] = os.path.getsize(thumbnail_path)
            response['X-Accel-Redirect'] = self.sendfile_location(thumbnail_path)
        return response


class RandomAlbumRedirect(RedirectView):
    model = models.Album
    permanent = False

    def get_queryset(self):
        return self.model.objects.all()

    def get_redirect_url(self, *args, **kwargs):
        albums = self.get_queryset().order_by('?')
        if albums.count() > 0:
            album = albums[0]
            return album.get_absolute_url()
        raise Http404


class RandomAlbumForArtistRedirect(RandomAlbumRedirect):
    def get_queryset(self):
        qs = super(RandomAlbumForArtistRedirect, self).get_queryset()
        qs = qs.filter(artists__pk=self.kwargs.get('pk', 0))
        return qs


class NewAlbumList(ListView):
    model = models.Album
    template_name = 'music/new_album_list.html'
    paginate_by = 12
    context_object_name = 'new_albums'

    def get_queryset(self):
        qs = super(NewAlbumList, self).get_queryset()
        return qs.order_by('-pk')


class SearchView(JSONResponseMixin, TemplateView):

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('q')
        if not q:
            raise Http404

        data = {}

        artists = search.search_artists(q).values('name', 'id')
        artist_url = reverse('artist_detail', args=(0,))
        data['artists'] = list(map(lambda x: {'name': x['name'], 'url': artist_url.replace('0', str(x['id']))}, artists))

        albums = search.search_albums(q).values('title', 'id', 'artists__name')
        album_url = reverse('album_detail', args=(0,))
        data['albums'] = list(map(lambda x: {'title': x['title'], 'artist': x['artists__name'], 'url': album_url.replace('0', str(x['id']))}, albums))

        tracks = search.search_tracks(q).values('title', 'album__id', 'artists__name')
        album_url = reverse('album_detail', args=(0,))
        data['tracks'] = list(map(lambda x: {'title': x['title'], 'artist': x['artists__name'], 'url': album_url.replace('0', str(x['album__id']))}, tracks))

        return data
