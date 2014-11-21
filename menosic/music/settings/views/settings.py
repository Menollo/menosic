# menosic/music/settings/views/settings.py
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import UpdateView

from .. import forms


class MusicSettingsView(UpdateView):
    form_class = forms.MusicSettingsForm
    template_name = "music/settings/settings.html"

    def get_object(self, **kwargs):
        if hasattr(self, "request") and \
           hasattr(self.request, "user") and \
           hasattr(self.request.user, "settings"):
            obj = self.request.user.settings
            if not obj.pk:
                obj.save()
            return obj
        else:
            raise Http404

    def get_success_url(self):
        return reverse("home")
