from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from music import views

app_name = 'music'
urlpatterns = [
    path('', login_required(views.HomePageView.as_view()), name='home'),
    path('guest/<int:pk>/', views.GuestPlaylistView.as_view(), name='guest_playlist'),
    path('playlist/', views.TemplateView.as_view(template_name='music/playlist.html'), name='playlist'),
    path('artist/<int:pk>/', views.ArtistDetailView.as_view(), name='artist_detail'),
    path('browse/<int:collection>/<path>/', views.BrowseView.as_view(), name='browse'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('track/<int:pk>/', views.TrackDetailView.as_view(), name='track_detail'),
    path('last_played/', views.LastPlayedView.as_view(), name='last_played'),

    # playlist

    # tags
    path('play_album_track/<int:pk>/', views.PlayAlbumTrack.as_view(), name='play_album_track'),
    path('add_album/<int:pk>/', views.AddAlbumToPlaylist.as_view(), name='add_album'),
    path('add_track/<int:pk>/', views.AddTrackToPlaylist.as_view(), name='add_track'),

    # files
    path('play_album_files/<int:collection>/<path>/', views.PlayAlbumFiles.as_view(), name='play_album_files'),
    path('add_album_files/<int:collection>/<path>/', views.AddDirectoryToPlaylist.as_view(), name='add_album_files'),
    path('add_file/<int:collection>/<path>/', views.AddFileToPlaylist.as_view(), name='add_file'),

    path('edit_playlist_track/<int:pk>/<action>/', views.PlaylistTrack.as_view(), name='edit_playlist_track'),
    path('client/<int:pk>/', views.PlayerJSON.as_view(), name='client'),

    path('file/<int:pk>/', views.TrackView.as_view(), name='track'),
    path('file/<output>/<int:pk>/', views.TrackView.as_view(), name='track'),
    path('file/<output>/<int:collection>/<path>/', views.FileView.as_view(), name='file'),

    path('cover/<int:pk>/', views.CoverFileView.as_view(), name='cover'),
    path('album/random/<int:pk>/', views.RandomAlbumForArtistRedirect.as_view(), name='random_album'),
    path('album/random/', views.RandomAlbumRedirect.as_view(), name='random_album'),
    path('album/new/', views.NewAlbumList.as_view(), name="new_albums"),

    path('genre/<int:pk>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('country/<int:pk>/', views.CountryDetailView.as_view(), name='country_detail'),

    path('settings/', include('music.settings.urls', namespace='music_settings')),
    path('search/', views.SearchView.as_view(), name='search'),
]
