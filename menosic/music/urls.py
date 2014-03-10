from django.conf.urls import patterns, include, url
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

    url(r'^play_album_track/(?P<pk>\d+)/$', views.PlayAlbumTrack.as_view(), name='play_album_track'),
    url(r'^add_album/(?P<pk>\d+)/$', views.AddAlbumToPlaylist.as_view(), name='add_album'),
    url(r'^external/(?P<pk>\d+)/$', views.PlayerJSON.as_view(), name='external'),

    url(r'^file/(?P<pk>\d+)/$', views.TrackView.as_view(), name='track'),
    url(r'^file/(?P<output>\w+)/(?P<pk>\d+)/$', views.TrackView.as_view(), name='track'),
)
