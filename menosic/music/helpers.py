import os
from django.utils.http import urlsafe_base64_encode
from music import models

def player_for_user(user):
    try:
        player = models.Player.objects.get(user=user, type='B')
    except models.Player.DoesNotExist:
        player = models.Player(
                user=user,
                type='B'
            )
        playlist = models.Playlist(user=user)
        playlist.save()

        player.playlist = playlist
        player.save()

    return player

class DirItem(object):
    def __init__(self, collection, path):
        self.collection = collection
        self.path = path

    @property
    def name(self):
        return os.path.basename(self.path.encode('utf-8', 'ignore').decode('utf-8'))

    @property
    def sortname(self):
        return self.name

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        path = urlsafe_base64_encode(self.path.encode('utf-8', 'ignore'))
        return reverse('browse', kwargs={'collection':self.collection.id, 'path': path})

class FileItem(DirItem):
    def __init__(self, collection, path):
        self.collection = collection
        self.path = path

    @property
    def title(self):
        return self.name


def items_for_path(collection, path):
    dirs = []
    files = []
    path = path[1:] if path[0] == '/' else path
    full_path = os.path.join(collection.location, path)
    for item in os.listdir(full_path):
        if os.path.isdir(os.path.join(full_path, item)):
            dirs.append(DirItem(collection, os.path.join(path, item)))
        else:
            files.append(FileItem(collection, os.path.join(path, item)))
    return (sorted(dirs, key=lambda i: i.sortname), sorted(files, key=lambda i: i.sortname))

def artists():
    # tags backend
    artists = list(models.Artist.objects.exclude(album=None))

    # files backend
    for collection in models.Collection.objects.filter(backend='F'):
        artists += items_for_path(collection, '/')[0]
        
    artists = sorted(artists, key=lambda a: a.sortname)

    return artists

