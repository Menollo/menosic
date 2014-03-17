import os
from django.utils.http import urlsafe_base64_encode
from music.backend.tags import reader


class DirItem(object):
    def __init__(self, collection, path):
        self.collection = collection
        self.path = path

    @property
    def name(self):
        path = self.path.encode('utf-8', 'ignore').decode('utf-8')
        return os.path.basename(path)

    @property
    def sortname(self):
        return self.name

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        path = urlsafe_base64_encode(self.path.encode('utf-8', 'ignore'))
        return reverse(
            'browse',
            kwargs={'collection': self.collection.id, 'path': path})


class FileItem(object):
    def __init__(self, collection, path, tag=None):
        self.collection = collection
        self.path = path
        if tag:
            self.tag = tag
        else:
            self.tag = reader.File(self.full_path)

    @property
    def full_path(self):
        return os.path.join(self.collection.location, self.path)

    @property
    def title(self):
        return str(self.tag.title)

    @property
    def artist(self):
        return ",".join([str(artist.name) for artist in self.tag.artists])

    @property
    def sort(self):
        return self.tag.tracknumber or self.tag.name

    @property
    def encoded_path(self):
        return urlsafe_base64_encode(self.path.encode('utf-8', 'ignore')).decode('utf-8')

    def __getattribute__(self, name):
        try:
            return super(FileItem, self).__getattribute__(name)
        except AttributeError:
            attribute = getattr(self.tag, name)
            if name == 'album':
                setattr(attribute, 'get_absolute_url', DirItem(self.collection, os.path.dirname(self.path)).get_absolute_url)
            return attribute

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse(
            'play_album_files',
            kwargs={'collection': self.collection.id, 'path': self.encoded_path})

    def get_mp3_url(self):
        from django.core.urlresolvers import reverse
        return reverse('file', kwargs={'output': 'mp3', 'collection': self.collection.id, 'path': self.encoded_path})

    def get_ogg_url(self):
        from django.core.urlresolvers import reverse
        return reverse('file', kwargs={'output': 'ogg', 'collection': self.collection.id, 'path': self.encoded_path})


def items_for_path(collection, path):
    dirs = []
    files = []
    path = path[1:] if path[0] == '/' else path
    full_path = os.path.join(collection.location, path)
    for item in os.listdir(full_path):
        if os.path.isdir(os.path.join(full_path, item)):
            dirs.append(DirItem(collection, os.path.join(path, item)))
        else:
            tag = reader.File(os.path.join(full_path, item))
            if tag:
                files.append(FileItem(collection, os.path.join(path, item), tag))
    return (
        sorted(dirs, key=lambda i: i.sortname),
        sorted(files, key=lambda i: i.sort))
