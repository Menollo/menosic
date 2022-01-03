from mutagen.oggvorbis import OggVorbis
from music.backend.tags import reader


l = reader.list_to_item


class Track(reader.Track):
    filetype = 'ogg'

    def __init__(self, path):
        super(Track, self).__init__(path)
        self.ogg = OggVorbis(path)
        f = self.ogg

        self.title = l(f.get('title'))
        self.discnumber = l(f.get('discnumber'))
        self.tracknumber = l(f.get('tracknumber'))
        self.length = int(f.info.length)
        self.bitrate = int(f.info.bitrate)

        self.musicbrainz_trackid = l(f.get('musicbrainz_trackid'))
        self.genres = f.get('genre')

        artist = reader.Artist()
        artist.name = l(f.get('artist'))
        artist.sortname = l(f.get('artistsort'))
        artist.musicbrainz_artistid = f.get('musicbrainz_artistid')
        self.artist = artist

        for a, i in zip(
                f.get('Artists', []),
                f.get('musicbrainz_artistid', []),
                ):
            artist = reader.Artist()
            artist.name = a
            artist.musicbrainz_artistid = i
            self.artists.append(artist)

        album = reader.Album()
        album.title = l(f.get('album'))
        album.date = l(f.get('originaldate') or f.get('date'))
        album.country = l(f.get('releasecountry'))
        album.musicbrainz_albumid = l(f.get('musicbrainz_albumid'))
        album.musicbrainz_releasegroupid = l(f.get('musicbrainz_releasegroupid'))
        album.labels = f.get('label')
        album.albumtypes = f.get('releasetype')
        album.albumstatus = f.get('releasestatus')

        albumartist = reader.Artist()
        albumartist.name = l(f.get('albumartist') or f.get('album artist'))
        albumartist.sortname = l(f.get('albumartistsort'))
        albumartist.musicbrainz_artistid = f.get('musicbrainz_albumartistid')
        album.artist = albumartist

        self.album = album
