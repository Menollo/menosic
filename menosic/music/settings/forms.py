# menosic/music/settings/forms
from django import forms

from .models import MusicSettings


class MusicSettingsForm(forms.ModelForm):
    class Meta:
        model = MusicSettings
        fields = ['ordering',]
