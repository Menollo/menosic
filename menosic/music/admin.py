from django.contrib import admin
from music import models


class ArtistAdmin(admin.ModelAdmin):
    fields = ('name',)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'backend', 'location')


admin.site.register(models.Collection, CollectionAdmin)
admin.site.register(models.Artist, ArtistAdmin)
