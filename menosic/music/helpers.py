from music import models

def player_for_user(user):
    try:
        player = models.Player.objects.get(user=user, type='B')
    except models.Player.DoesNotExist:
        player = models.Player(
                user=user,
                type='B'
            )
        playlist = models.Playlist(user=user)
        playlist.save()

        player.playlist = playlist
        player.save()

    return player
