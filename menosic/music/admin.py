from django.contrib import admin
from music import models
# Register your models here.
class ArtistAdmin(admin.ModelAdmin):
    fields = ('name',)

admin.site.register(models.Artist, ArtistAdmin)
