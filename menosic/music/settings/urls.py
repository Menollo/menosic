from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.MusicSettingsView.as_view(), name="detail"),
)
