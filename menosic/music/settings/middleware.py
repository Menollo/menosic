# menosic/music/settings/middleware.py
from .models import MusicSettings


class MusicSettingsMiddleware(object):
    def process_request(self, request):
        if hasattr(request, "user") and request.user:
            request.user.settings = MusicSettings.get(request.user.pk)
