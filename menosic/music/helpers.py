def player_for_user(user):
    from music import models
    try:
        player = models.Player.objects.get(user=user, type='B')
    except models.Player.DoesNotExist:
        player = models.Player(user=user, type='B')
        playlist = models.Playlist(user=user)
        playlist.save()

        player.playlist = playlist
        player.save()
    return player


def duration(length):
    import datetime

    duration = str(datetime.timedelta(seconds=length))
    return duration[2:] if duration[0:2] == '0:' else duration


def artists():
    # tags backend
    from music.models import Artist, Collection
    artists = list(Artist.objects.exclude(album=None))

    # files backend
    from music.backend.files import items_for_path

    for collection in Collection.objects.filter(backend='F'):
        artists += items_for_path(collection, '/')[0]

    artists = sorted(artists, key=lambda a: a.sortname)

    return artists
