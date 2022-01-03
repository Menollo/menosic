from django.urls import path
from . import views

app_name = 'settings'
urlpatterns = [
    path('', views.MusicSettingsView.as_view(), name="detail"),
]
