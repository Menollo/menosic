from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.MusicSettingsView.as_view(), name="detail"),
]
