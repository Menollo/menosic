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
    def __init__(self, collection, tag):
        self.collection = collection
        self.tag = tag

    @property
    def title(self):
        return self.tag.title

    @property
    def sort(self):
        return self.tag.tracknumber or self.tag.name


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
                files.append(FileItem(collection, tag))
    return (
        sorted(dirs, key=lambda i: i.sortname),
        sorted(files, key=lambda i: i.sort))
