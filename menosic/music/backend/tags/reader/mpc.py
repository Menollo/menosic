from mutagen.musepack import Musepack
from music.backend.tags import reader


class Track(reader.Track):
    filetype = 'mpc'

    def __init__(self, path):
        super(Track, self).__init__(path)
        self.mpc = Musepack(path)
        f = self.mpc

        self.title = f.get('Title')
        self.discnumber = reader.number(f.get('Disc'))
        self.tracknumber = reader.number(f.get('Track'))
        self.length = int(f.info.length)
        self.bitrate = int(f.info.bitrate)

        self.musicbrainz_trackid = reader.value(f.get('Musicbrainz_Trackid'))
        self.genres = reader.item_to_list(f.get('Genre'))

        artist = reader.Artist()
        artist.name = f.get('Artist')
        artist.sortname = f.get('Artistsort')
        artist.musicbrainz_artistids = reader.item_to_list(f.get('Musicbrainz_Artistid'))
        self.artist = artist

        for a, i in zip(
                reader.item_to_list(f.get('Artists')),
                reader.item_to_list(f.get('Musicbrainz_Artistid')),
                ):
            artist = reader.Artist()
            artist.name = a
            artist.musicbrainz_artistid = i
            self.artists.append(artist)

        album = reader.Album()
        album.title = f.get('Album')
        album.date = f.get('Originaldate') or f.get('Year')
        album.country = f.get('Releasecountry')
        album.musicbrainz_albumid = reader.value(f.get('Musicbrainz_Albumid'))
        album.musicbrainz_releasegroupid = reader.value(f.get('Musicbrainz_Releasegroupid'))
        album.labels = reader.item_to_list(f.get('Label'))
        album.albumtypes = reader.item_to_list(f.get('MUSICBRAINZ_ALBUMTYPE'))
        album.albumstatus = reader.item_to_list(f.get('MUSICBRAINZ_ALBUMSTATUS'))

        albumartist = reader.Artist()
        albumartist.name = f.get('Album Artist') or f.get('Albumartist')
        albumartist.sortname = f.get('Albumartistsort')
        albumartist.musicbrainz_artistid = reader.item_to_list(f.get('Musicbrainz_Albumartistid'))
        album.artist = albumartist

        self.album = album
