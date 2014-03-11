from music import helpers


def playlist(request):
    _playlist = []
    if request.user.is_authenticated():
        _playlist = helpers.player_for_user(request.user).playlist
    return {'playlist': _playlist}


def artists(request):
    return {'artists': helpers.artists()}
