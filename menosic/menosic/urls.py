from django.conf.urls import include, url

from django.contrib import admin

app_name = 'menosic'
urlpatterns = [
    url(r'^', include('music.urls', namespace='music')),

    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
]
