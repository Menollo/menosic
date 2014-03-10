from music import helpers

def playlist(request):
    playlist = helpers.player_for_user(request.user).playlist if request.user.is_authenticated() else []
    return {'playlist': playlist}

def artists(request):
    return {'artists': helpers.artists()}
