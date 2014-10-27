from django.contrib import admin
from music import models


class ArtistAdmin(admin.ModelAdmin):
    fields = ('name',)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'backend', 'location', 'path_exists')

    def path_exists(self, obj):
        from os import path
        if path.lexists(obj.location):
            return True
        return False
    path_exists.short_description = "Location path exists"
    path_exists.boolean = True

admin.site.register(models.Collection, CollectionAdmin)
admin.site.register(models.Artist, ArtistAdmin)
