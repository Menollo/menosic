# menosic/music/settings/middleware.py
from .models import MusicSettings

class MusicSettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, "user") and request.user:
            request.user.settings = MusicSettings.get(request.user.pk)

        return self.get_response(request)
