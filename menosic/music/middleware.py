from music import models


class LoginTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'token' in request.GET:
            player = models.Player.objects.get(id=request.GET.get('token'))
            request.user = player.user

        return self.get_response(request)
