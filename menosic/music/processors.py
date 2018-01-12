from django.conf import settings

from music import helpers


def playlist(request):
    _playlist = []
    if request.user.is_authenticated:
        _playlist = helpers.player_for_user(request.user).playlist
    return {'playlist': _playlist}

def ws_url(request):
    ws_url = settings.WS_URL
    if ws_url[:2] == '//':
        if request.scheme == 'https':
            ws_url = 'wss:' + ws_url
        else:
            ws_url = 'ws:' + ws_url

    return {'ws_url': ws_url}
