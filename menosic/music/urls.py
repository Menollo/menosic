from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from music import views

urlpatterns = patterns('',
    url(r'^$', views.ArtistListView.as_view(), name='artist_list'),
    url(r'^artist/(?P<pk>\d+)/$', views.ArtistDetailView.as_view(), name='artist_detail'),
    url(r'^album/(?P<pk>\d+)/$', views.AlbumDetailView.as_view(), name='album_detail'),
)
