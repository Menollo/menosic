from music import models

class LoginTokenMiddleware(object):
    def process_request(self, request):
        if 'token' in request.GET:
            player = models.Player.objects.get(id=request.GET.get('token'))
            request.user = player.user
