from django.urls import include, path

from django.contrib import admin

app_name = 'menosic'
urlpatterns = [
    path('', include('music.urls', namespace='music')),

    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
]
