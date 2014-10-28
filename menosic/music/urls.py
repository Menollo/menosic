from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from music import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', login_required(TemplateView.as_view(template_name='base.html')), name='home'),
    url(r'^artist/(?P<pk>\d+)/$', views.ArtistDetailView.as_view(), name='artist_detail'),
    url(r'^browse/(?P<collection>\d+)/(?P<path>\w+)/$', views.BrowseView.as_view(), name='browse'),
    url(r'^album/(?P<pk>\d+)/$', views.AlbumDetailView.as_view(), name='album_detail'),
    url(r'^track/(?P<pk>\d+)/$', views.TrackDetailView.as_view(), name='track_detail'),
    url(r'^last_played/$', views.LastPlayedView.as_view(), name='last_played'),

    url(r'^play_album_track/(?P<pk>\d+)/$', views.PlayAlbumTrack.as_view(), name='play_album_track'),
    url(r'^play_album_files/(?P<collection>\d+)/(?P<path>\w+)/$', views.PlayAlbumFiles.as_view(), name='play_album_files'),
    url(r'^add_album/(?P<pk>\d+)/$', views.AddAlbumToPlaylist.as_view(), name='add_album'),
    url(r'^add_track/(?P<pk>\d+)/$', views.AddTrackToPlaylist.as_view(), name='add_track'),
    url(r'^edit_playlist_track/(?P<pk>\d+)/(?P<action>\w+)/$', views.PlaylistTrack.as_view(), name='edit_playlist_track'),
    url(r'^client/(?P<pk>\d+)/$', views.PlayerJSON.as_view(), name='client'),

    url(r'^file/(?P<pk>\d+)/$', views.TrackView.as_view(), name='track'),
    url(r'^file/(?P<output>\w+)/(?P<pk>\d+)/$', views.TrackView.as_view(), name='track'),
    url(r'^file/(?P<output>\w+)/(?P<collection>\d+)/(?P<path>\w+)/$', views.FileView.as_view(), name='file'),

    url(r'^cover/(?P<pk>\d+)/$', views.CoverFileView.as_view(), name='cover'),
    url(r'^album/random/$', views.RandomAlbumRedirect.as_view(), name='random_album'),
    url(r'^album/new/$', views.NewAlbumList.as_view(), name="new_albums"),
)
